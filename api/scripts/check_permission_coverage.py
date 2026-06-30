#!/usr/bin/env python3
"""
Permission coverage audit for AERC API routes.

Usage:
    python api/scripts/check_permission_coverage.py           # full report
    python api/scripts/check_permission_coverage.py --gaps    # only unprotected routes
    python api/scripts/check_permission_coverage.py --ci      # exit 1 if critical gaps found

Critical gap definition: write endpoint (POST/PUT/PATCH/DELETE) with no verify_access AND no check_permission.
Read endpoint gaps are reported but do not fail CI.
"""

import ast
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTES_DIR = REPO_ROOT / "api" / "src" / "routes"

# Routes that are intentionally public or handled by a different mechanism.
# Format: (method, path_prefix)  —  prefix match, "" matches everything
INTENTIONAL_EXCEPTIONS = {
    # Deprecated endpoint — always returns 410
    ("POST", "/case/{case_number}/create-version"),
    # Applicant subsidy summary: read-only aggregate, no PII exposed per field, open to authenticated users
    ("GET", "/applicant-subsidy-summary/"),
    # Batch cross-year: admin-only operation confirmed by business requirement
    ("POST", "/batch-cross-year"),
    # Search: covered by CRUD-layer role filter (get_grants passes current_user)
    # Note: search_grants_api does NOT pass current_user — tracked as gap, not exception
}

# Scan window: lines after @router.* decorator to search for access checks
SCAN_WINDOW = 45


def scan_route_file(filepath: Path) -> list[dict]:
    """Parse a route file and return per-endpoint coverage info."""
    with open(filepath) as f:
        lines = f.readlines()

    results = []
    i = 0
    while i < len(lines):
        m = re.match(r'\s*@router\.(get|post|put|patch|delete)\(', lines[i])
        if not m:
            i += 1
            continue

        method = m.group(1).upper()

        # Extract path from decorator
        path = ""
        for j in range(i, min(i + 5, len(lines))):
            pm = re.search(r'"(/[^"]*)"', lines[j]) or re.search(r"'(/[^']*)'", lines[j])
            if pm:
                path = pm.group(1)
                break

        # Extract function name
        func_name = ""
        for j in range(i + 1, min(i + 10, len(lines))):
            fm = re.search(r'async def (\w+)', lines[j])
            if fm:
                func_name = fm.group(1)
                break

        # Scan for protection patterns within window
        window = lines[i:min(i + SCAN_WINDOW, len(lines))]
        window_text = "".join(window)

        # Legacy imperative patterns (routes not yet migrated)
        has_verify = "_verify_grant_access" in window_text
        has_check_perm = "check_permission" in window_text
        # Declarative factory patterns (target state)
        has_scope_guard = (
            "require_grant_scope_by_case_number" in window_text
            or "require_grant_scope_by_id" in window_text
        )
        has_perm_guard = "require_permission(" in window_text

        has_require_auth = "require_full_auth" in window_text or "Depends(require_full_auth)" in window_text

        # Classify gap severity
        is_write = method in ("POST", "PUT", "PATCH", "DELETE")
        is_protected = has_verify or has_check_perm or has_scope_guard or has_perm_guard

        if not has_require_auth:
            severity = "PUBLIC"
        elif not is_protected and is_write:
            severity = "CRITICAL"
        elif not is_protected and not is_write:
            severity = "GAP"
        elif has_verify and not has_check_perm:
            severity = "PARTIAL"   # access check but no action-level permission
        else:
            severity = "OK"

        # Check intentional exceptions
        is_exception = False
        for exc_method, exc_prefix in INTENTIONAL_EXCEPTIONS:
            if method == exc_method and path.startswith(exc_prefix.rstrip("/")):
                is_exception = True
                break

        results.append({
            "file": filepath.name,
            "line": i + 1,
            "method": method,
            "path": path,
            "func": func_name,
            "has_verify": has_verify,
            "has_check_perm": has_check_perm,
            "has_scope_guard": has_scope_guard,
            "has_perm_guard": has_perm_guard,
            "has_require_auth": has_require_auth,
            "severity": severity,
            "exception": is_exception,
        })

        i += 1

    return results


def print_report(all_results: list[dict], gaps_only: bool = False) -> int:
    """Print audit report. Returns count of non-exception critical gaps."""
    critical_gaps = 0

    # Group by file
    by_file: dict[str, list] = {}
    for r in all_results:
        by_file.setdefault(r["file"], []).append(r)

    severity_icon = {
        "OK": "✓",
        "PARTIAL": "~",
        "GAP": "⚠",
        "CRITICAL": "✗",
        "PUBLIC": "○",
    }
    severity_label = {
        "OK": "OK      ",
        "PARTIAL": "PARTIAL ",
        "GAP": "GAP     ",
        "CRITICAL": "CRITICAL",
        "PUBLIC": "PUBLIC  ",
    }

    for fname, results in sorted(by_file.items()):
        interesting = [r for r in results if r["severity"] not in ("OK", "PUBLIC") or not gaps_only]
        if gaps_only:
            interesting = [r for r in results if r["severity"] in ("CRITICAL", "GAP", "PARTIAL")]
        if not interesting:
            continue

        print(f"\n{'='*80}")
        print(f"  {fname}")
        print(f"{'='*80}")
        print(f"  {'Sv':<10} {'M':<7} {'scope':^6} {'perm':^6} {'Path':<45} Function")
        print(f"  {'-'*9} {'-'*6} {'-'*6} {'-'*6} {'-'*44} {'-'*25}")

        for r in results:
            if gaps_only and r["severity"] in ("OK", "PUBLIC"):
                continue

            icon = severity_icon[r["severity"]]
            label = severity_label[r["severity"]]
            exc_marker = " [except]" if r["exception"] else ""
            # scope: factory guard > legacy _verify_grant_access
            scope_ok = r["has_scope_guard"] or r["has_verify"]
            # perm: factory guard > legacy check_permission
            perm_ok = r["has_perm_guard"] or r["has_check_perm"]
            scope_str = " [f]✓" if r["has_scope_guard"] else (" [l]✓" if r["has_verify"] else "   ✗ ")
            perm_str  = " [f]✓" if r["has_perm_guard"]  else (" [l]✓" if r["has_check_perm"] else "   ✗ ")

            print(
                f"  {icon} {label} {r['method']:<6}  {scope_str}  {perm_str}  "
                f"{r['path']:<44} {r['func']}{exc_marker}"
            )

            if r["severity"] == "CRITICAL" and not r["exception"]:
                critical_gaps += 1

    print(f"\n{'='*80}")
    print(f"  SUMMARY")
    print(f"{'='*80}")

    severity_counts: dict[str, int] = {}
    exception_count = 0
    for r in all_results:
        severity_counts[r["severity"]] = severity_counts.get(r["severity"], 0) + 1
        if r["exception"] and r["severity"] == "CRITICAL":
            exception_count += 1

    for sv in ("OK", "PARTIAL", "GAP", "CRITICAL", "PUBLIC"):
        count = severity_counts.get(sv, 0)
        icon = severity_icon[sv]
        print(f"  {icon} {sv:<10}: {count}")

    print(f"\n  Critical gaps (non-exception): {critical_gaps}")
    if exception_count:
        print(f"  Critical gaps (intentional exception): {exception_count}")
    print()

    return critical_gaps


def main():
    gaps_only = "--gaps" in sys.argv
    ci_mode = "--ci" in sys.argv

    route_files = sorted(ROUTES_DIR.glob("*.py"))

    all_results = []
    for fpath in route_files:
        all_results.extend(scan_route_file(fpath))

    critical_gaps = print_report(all_results, gaps_only=gaps_only)

    if ci_mode and critical_gaps > 0:
        print(f"CI FAIL: {critical_gaps} unprotected write endpoint(s) found.")
        sys.exit(1)


if __name__ == "__main__":
    main()
