#!/usr/bin/env python3
"""
Permission overview — shows full frontend + backend permission configuration.

Usage (from AERC root):
    python3 api/scripts/permission_overview.py
"""

import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# ── Parse enum values ─────────────────────────────────────────────────────────
def extract_enum(src, class_name):
    members = {}
    in_class = False
    for line in src.splitlines():
        if re.match(rf'\s*class {class_name}.*:', line): in_class = True; continue
        if in_class:
            if re.match(r'\s*class ', line): break
            m = re.match(r'\s+(\w+)\s*=\s*"([^"]+)"', line)
            if m: members[m.group(1)] = m.group(2)
    return members

schema_src = (ROOT / 'api/src/schemas/permissions.py').read_text()
modules_map = extract_enum(schema_src, 'ModuleName')
actions_map = extract_enum(schema_src, 'PermissionAction')
ROLES = ['admin', 'manager', 'staff', 'user']
all_mods = sorted(modules_map.values())

# ── Parse DEFAULT_ROLE_PERMISSIONS ────────────────────────────────────────────
perm_src = (ROOT / 'api/src/services/permission_service.py').read_text()
matrix = {r: {} for r in ROLES}
current_role = None
in_matrix = False

for line in perm_src.splitlines():
    if 'DEFAULT_ROLE_PERMISSIONS' in line and '=' in line: in_matrix = True
    if not in_matrix: continue
    rm = re.match(r'\s+"(\w+)":\s*\{', line)
    if rm and rm.group(1) in ROLES: current_role = rm.group(1); continue
    if current_role is None: continue
    mm = re.search(r'ModuleName\.(\w+):\s*\{([^}]*)\}', line)
    if mm:
        mod_val = modules_map.get(mm.group(1), mm.group(1).lower())
        act_vals = sorted(actions_map.get(k, k.lower())
                          for k in re.findall(r'PermissionAction\.(\w+)', mm.group(2)))
        matrix[current_role][mod_val] = act_vals
    if line.strip() == '}' and current_role: current_role = None

# ── 1. Backend matrix ─────────────────────────────────────────────────────────
print("=" * 78)
print("  後端  DEFAULT_ROLE_PERMISSIONS")
print("=" * 78)
W = 26
print(f"  {'module':<18}" + "".join(f"{r:<{W}}" for r in ROLES))
print("  " + "-" * (18 + W * 4))
for mod in all_mods:
    row = f"  {mod:<18}"
    for role in ROLES:
        acts = matrix[role].get(mod, [])
        row += f"{', '.join(acts) or '—':<{W}}"
    print(row)

# ── 2. Frontend roleGuard ─────────────────────────────────────────────────────
print()
print("=" * 78)
print("  前端  ROLE_RESTRICTED_ROUTES  (router/index.ts)")
print("=" * 78)
router_text = (ROOT / 'dry-farm/src/router/index.ts').read_text()
print(f"  {'route':<32} {'permission':<24} {'✓ allowed':<22} ✗ blocked")
print("  " + "-" * 74)
for m in re.finditer(
    r"'(/[^']+)':\s*\{[^}]*requiredPermission:\s*\{[^}]*module:\s*'([^']+)'[^}]*action:\s*'([^']+)'",
    router_text, re.DOTALL
):
    path, mod, act = m.group(1), m.group(2), m.group(3)
    allowed = [r for r in ROLES if act in matrix[r].get(mod, [])]
    blocked = [r for r in ROLES if r not in allowed]
    print(f"  {path:<32} {mod+'.'+act:<24} {','.join(allowed):<22} {','.join(blocked)}")

# ── 3. Frontend component checks ──────────────────────────────────────────────
print()
print("=" * 78)
print("  前端組件  userStore.can / canAny")
print("=" * 78)
print(f"  {'file':<42} {'line':<6} {'call':<38} {'✓':<18} ✗")
print("  " + "-" * 74)
vue_root = ROOT / 'dry-farm/src'
pattern = re.compile(r"userStore\.(can(?:Any)?)\('([^']+)',\s*(?:'([^']+)'|\[([^\]]+)\])\)")

for f in sorted(list(vue_root.rglob('*.ts')) + list(vue_root.rglob('*.vue'))):
    text = f.read_text(errors='ignore')
    for m in pattern.finditer(text):
        fn, mod = m.group(1), m.group(2)
        acts = re.findall(r"'([^']+)'", m.group(4) or f"'{m.group(3)}'")
        lineno = text[:m.start()].count('\n') + 1
        rel = str(f.relative_to(vue_root))
        allowed = [r for r in ROLES if any(a in matrix[r].get(mod, []) for a in acts)]
        blocked = [r for r in ROLES if r not in allowed]
        call_str = f"{fn}('{mod}', {acts})"
        print(f"  {rel:<42} L{lineno:<5} {call_str:<38} {','.join(allowed):<18} {','.join(blocked)}")

# ── 4. CRUD row-level scope ───────────────────────────────────────────────────
# Source: crud/grants.py::get_grants() + auth/route_guards.py::_enforce_grant_scope()
# "能做什麼" (matrix) 之外，每個角色實際能看到的資料集合。
CRUD_SCOPE = {
    'grants (list)': {
        # crud/grants.py L173–184
        'admin':   '全域（所有案件，所有管理處）',
        'manager': '本辦公室（office_id = user.office.id）',
        'staff':   '本辦公室（office_id = user.office.id）',
        'user':    '後端：同管理處（office_id = user.office.id）'
                   ' ┃ 前端預設：只顯示本人建立（created_by.id = user.id，client-side filter）'
                   ' ┃ 前端搜尋中：顯示全管理處符合條件案件（search 有值時移除 creator filter）',
    },
    'grants (single)': {
        # auth/route_guards.py::_enforce_grant_scope() L70–98
        'admin':   '全域（無限制）',
        'manager': '本辦公室（grant.office_id = user.office.id）',
        'staff':   '本辦公室（grant.office_id = user.office.id）',
        'user':    '本人建立（grant.created_by_id = user.id）'
                   ' ┃ legacy: ALLOW_USER_LEGACY_GRANT_ACCESS 環境變數控制',
    },
    'users (list)': {
        # routes/users.py — list_users endpoint
        'admin':   '全域（所有使用者）',
        'manager': '全域（含 users.approve 權限）',
        'staff':   '—（無 users 模組權限）',
        'user':    '—（無 users 模組權限）',
    },
    'offices': {
        # offices 為靜態查找表，roles 僅 admin 可寫入
        'admin':   '全域讀寫（create / edit / delete / view）',
        'manager': '全域唯讀（view）',
        'staff':   '全域唯讀（view）',
        'user':    '全域唯讀（view）',
    },
}

print()
print("=" * 78)
print("  CRUD Row-Level Scope  （能看到哪些資料）")
print(f"  Source: crud/grants.py::get_grants()  auth/route_guards.py::_enforce_grant_scope()")
print("=" * 78)
for resource, scopes in CRUD_SCOPE.items():
    print(f"\n  [{resource}]")
    for role in ROLES:
        print(f"    {role:<10} {scopes.get(role, '—')}")
