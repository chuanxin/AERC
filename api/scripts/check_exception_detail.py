#!/usr/bin/env python3
"""
檢查 HTTPException 的 detail 參數是否洩漏例外變數（str(e) / f-string 含 {e}）。

捕捉模式：
  raise HTTPException(status_code=4xx, detail=str(e))
  raise HTTPException(status_code=4xx, detail=f"...{str(e)}...")
  raise HTTPException(status_code=4xx, detail=f"...{e}...")

允許模式：
  raise HTTPException(status_code=4xx, detail="固定字串")
  raise HTTPException(status_code=4xx, detail=f"案件 {case_number} 不存在")
  raise HTTPException(status_code=5xx, ...)  # 5xx 由 global handler 處理，不在此規則範圍

用法：
  python check_exception_detail.py [file1.py file2.py ...]
  exit code 0 = 通過；exit code 1 = 發現違規
"""
import ast
import sys
from pathlib import Path


def _is_exception_var(node: ast.expr, exc_vars: set[str]) -> bool:
    """判斷 AST 節點是否為例外變數或 str(例外變數) 呼叫"""
    if isinstance(node, ast.Name) and node.id in exc_vars:
        return True
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "str"
        and len(node.args) == 1
        and isinstance(node.args[0], ast.Name)
        and node.args[0].id in exc_vars
    ):
        return True
    return False


def _fstring_contains_exc(node: ast.JoinedStr, exc_vars: set[str]) -> bool:
    """檢查 f-string 的插值部分是否含有例外變數"""
    for value in node.values:
        if isinstance(value, ast.FormattedValue):
            if _is_exception_var(value.value, exc_vars):
                return True
    return False


def _get_detail_arg(call: ast.Call) -> ast.expr | None:
    """從 HTTPException(...) 取得 detail= 關鍵字引數"""
    for kw in call.keywords:
        if kw.arg == "detail":
            return kw.value
    return None


def _resolve_status_code(node: ast.expr) -> int | None:
    """將 status_code 節點解析為整數：支援字面量與 status.HTTP_XXX 屬性"""
    if isinstance(node, ast.Constant) and isinstance(node.value, int):
        return node.value
    # status.HTTP_404_NOT_FOUND → 從屬性名稱萃取數字
    if isinstance(node, ast.Attribute):
        import re
        m = re.search(r"HTTP_(\d{3})", node.attr)
        if m:
            return int(m.group(1))
    return None


def _get_status_code(call: ast.Call) -> int | None:
    """取得 HTTPException 的 status_code（字面量或 status.HTTP_XXX；動態值回傳 None）"""
    for kw in call.keywords:
        if kw.arg == "status_code":
            return _resolve_status_code(kw.value)
    # 位置引數：HTTPException(404, detail=...)
    if call.args:
        return _resolve_status_code(call.args[0])
    return None


class ExceptionDetailLeakChecker(ast.NodeVisitor):
    def __init__(self, filename: str):
        self.filename = filename
        self.violations: list[tuple[int, str]] = []
        self._exc_vars: set[str] = set()

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if node.name:
            self._exc_vars.add(node.name)
        self.generic_visit(node)
        if node.name:
            self._exc_vars.discard(node.name)

    def visit_Raise(self, node: ast.Raise) -> None:
        if not (
            node.exc
            and isinstance(node.exc, ast.Call)
            and isinstance(node.exc.func, ast.Name)
            and node.exc.func.id == "HTTPException"
        ):
            return

        detail = _get_detail_arg(node.exc)
        if detail is None:
            return

        # 5xx 由 global handler 保護，只對 4xx 強制（status_code 不明時保守地標記）
        status = _get_status_code(node.exc)
        if status is not None and status >= 500:
            return

        if _is_exception_var(detail, self._exc_vars):
            self.violations.append((
                node.lineno,
                f"detail=str(e) 直接暴露例外訊息，請改用固定的業務錯誤訊息",
            ))
        elif isinstance(detail, ast.JoinedStr) and _fstring_contains_exc(detail, self._exc_vars):
            self.violations.append((
                node.lineno,
                f"detail 的 f-string 含有例外變數，請改用固定的業務錯誤訊息",
            ))


def check_file(path: Path) -> list[tuple[int, str]]:
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as e:
        return [(e.lineno or 0, f"語法錯誤：{e}")]

    checker = ExceptionDetailLeakChecker(str(path))
    checker.visit(tree)
    return checker.violations


def main() -> int:
    files = [Path(f) for f in sys.argv[1:]] if len(sys.argv) > 1 else []
    if not files:
        print("用法: check_exception_detail.py <file.py> [file.py ...]")
        return 0

    total_violations = 0
    for path in files:
        violations = check_file(path)
        for lineno, msg in violations:
            print(f"{path}:{lineno}: {msg}")
            total_violations += 1

    if total_violations:
        print(f"\n發現 {total_violations} 個違規：HTTPException detail 不得使用例外變數")
        print("建議改用固定字串，或參考 UserFacingError 架構（specs/027-error-message-hardening/plan.md）")

    return 1 if total_violations else 0


if __name__ == "__main__":
    sys.exit(main())
