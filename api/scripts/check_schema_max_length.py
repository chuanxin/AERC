#!/usr/bin/env python3
"""
檢查 Pydantic input schema 的字串欄位是否缺少 max_length 約束。

Tortoise ORM 的 CharField 在 get()/filter()/create()/save() 都會驗證 max_length，
若 Pydantic schema 未設定 max_length，過長的用戶輸入會穿透 Pydantic 層，
在 ORM 層拋出 ValidationError → 500（Schema Drift 問題）。

偵測模式：
  欄位型別為 str / Optional[str]，且 Field() 中有 min_length 但無 max_length。
  這是「開發者想過驗證但漏掉上界」的最明確錯誤訊號。

建議改法（優先順序）：
  1. 使用 pydantic_model_creator 自動從 ORM model 派生 schema（SSOT，無漂移）
  2. 查 api/src/database/models.py 對應的 CharField(max_length=N)，手動加上 max_length=N

用法：
  python check_schema_max_length.py [file1.py file2.py ...]
  exit code 0 = 通過；exit code 1 = 發現違規
"""
import ast
import sys
from pathlib import Path

# 名稱含以下字串的 class 視為 Response schema，不強制 max_length
_RESPONSE_PATTERNS = (
    "Response",
    "OutSchema",
    "ListSchema",
    "TortoiseSchema",
    "Out",
)


def _is_response_class(class_name: str) -> bool:
    return any(pat in class_name for pat in _RESPONSE_PATTERNS)


def _field_has_keyword(call: ast.Call, keyword: str) -> bool:
    return any(kw.arg == keyword for kw in call.keywords)


def _is_str_annotation(annotation: ast.expr) -> bool:
    """判斷型別標注是否為 str 或 Optional[str]"""
    if isinstance(annotation, ast.Name) and annotation.id == "str":
        return True
    if isinstance(annotation, ast.Subscript):
        val = annotation.value
        if isinstance(val, ast.Name) and val.id == "Optional":
            inner = annotation.slice
            if isinstance(inner, ast.Name) and inner.id == "str":
                return True
    return False


def _is_field_call(node: ast.expr | None) -> bool:
    """判斷賦值右側是否為 Field(...) 呼叫"""
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "Field"
    )


class SchemaMaxLengthChecker(ast.NodeVisitor):
    def __init__(self, filename: str):
        self.filename = filename
        self.violations: list[tuple[int, str, str]] = []  # (lineno, class, field)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        if _is_response_class(node.name):
            return

        for item in node.body:
            if not isinstance(item, ast.AnnAssign):
                continue
            if not _is_str_annotation(item.annotation):
                continue
            if not _is_field_call(item.value):
                continue

            call: ast.Call = item.value  # type: ignore
            has_min = _field_has_keyword(call, "min_length")
            has_max = _field_has_keyword(call, "max_length")

            if has_min and not has_max:
                field_name = (
                    item.target.id
                    if isinstance(item.target, ast.Name)
                    else "?"
                )
                self.violations.append((item.lineno, node.name, field_name))


def check_file(path: Path) -> list[tuple[int, str, str]]:
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as e:
        return [(e.lineno or 0, "SyntaxError", str(e))]

    checker = SchemaMaxLengthChecker(str(path))
    checker.visit(tree)
    return checker.violations


def main() -> int:
    files = [Path(f) for f in sys.argv[1:]] if len(sys.argv) > 1 else []
    if not files:
        print("用法: check_schema_max_length.py <file.py> [file.py ...]")
        return 0

    total = 0
    for path in files:
        for lineno, class_name, field_name in check_file(path):
            print(
                f"{path}:{lineno}: [{class_name}.{field_name}] "
                f"有 min_length 但缺少 max_length"
            )
            total += 1

    if total:
        print(f"\n發現 {total} 個 Schema Drift 風險：str 欄位有 min_length 但缺 max_length")
        print("修法（優先）：使用 pydantic_model_creator 自動從 ORM model 派生 schema")
        print("修法（手動）：查 api/src/database/models.py 對應 CharField(max_length=N)，補上 max_length=N")

    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
