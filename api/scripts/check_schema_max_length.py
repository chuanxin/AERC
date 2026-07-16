#!/usr/bin/env python3
"""
檢查 Pydantic schema 的字串欄位是否缺少 max_length 約束。

Tortoise ORM 的 CharField 在 get()/filter()/create()/save() 都會驗證 max_length，
若 Pydantic schema 未設定 max_length，過長的用戶輸入會穿透 Pydantic 層，
在 ORM 層拋出 ValidationError → 500（Schema Drift 問題）。即使欄位背後是
TextField/JSONField（Tortoise 不強制長度）或完全沒有 ORM 對應（如加密酬載、
token），專案慣例仍是加上合理上限做為輸入防禦，而非只在會直接觸發 ORM
例外時才設限。

偵測模式：
  欄位型別為 str / Optional[str]，且滿足以下任一條件：
  1. 用 Field() 宣告但缺少 max_length（無論是否有設定 min_length）
  2. 完全沒有用 Field() 包裝（例如 `name: str` 或 `name: str = "x"`），
     這種寫法從語法上就不可能設定 max_length，一律視為違規

排除方式（兩種，擇一即可跳過整個 class）：
  1. class 名稱包含 Response/OutSchema/ListSchema/TortoiseSchema/Out
  2. class 定義正上方（可在 decorator 之上）加註解 `# schema-max-length: skip`，
     用於標記本來就不是「使用者輸入 → 寫入」路徑的 schema（例如純回應/摘要
     模型、外部 API 回應解析模型）。每一次排除都是明確、可稽核的決定，
     不是靠名稱猜測。

建議改法（優先順序）：
  1. 使用 pydantic_model_creator 自動從 ORM model 派生 schema（SSOT，無漂移）
  2. 查 api/src/database/models.py 對應的 CharField(max_length=N)，手動加上 max_length=N
  3. 若欄位無對應 ORM 欄位（例如加密酬載、token），仍應加上合理的防禦性上限

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

_SKIP_MARKER = "schema-max-length: skip"


def _is_response_class(class_name: str) -> bool:
    return any(pat in class_name for pat in _RESPONSE_PATTERNS)


def _has_skip_marker(node: ast.ClassDef, source_lines: list[str]) -> bool:
    """檢查 class 定義（或其 decorator）正上方一行是否有 skip 標記註解"""
    first_lineno = node.decorator_list[0].lineno if node.decorator_list else node.lineno
    above_index = first_lineno - 2  # 轉成 0-indexed，取上一行
    if 0 <= above_index < len(source_lines):
        return _SKIP_MARKER in source_lines[above_index]
    return False


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
    def __init__(self, filename: str, source_lines: list[str]):
        self.filename = filename
        self.source_lines = source_lines
        self.violations: list[tuple[int, str, str]] = []  # (lineno, class, field)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        if _is_response_class(node.name) or _has_skip_marker(node, self.source_lines):
            return

        for item in node.body:
            if not isinstance(item, ast.AnnAssign):
                continue
            if not _is_str_annotation(item.annotation):
                continue

            field_name = (
                item.target.id if isinstance(item.target, ast.Name) else "?"
            )

            if _is_field_call(item.value):
                call: ast.Call = item.value  # type: ignore
                if not _field_has_keyword(call, "max_length"):
                    self.violations.append((item.lineno, node.name, field_name))
            else:
                # 裸欄位（例如 `name: str` 或 `name: str = "x"`，沒有 Field()）
                # 完全無法設定 max_length，一律視為違規
                self.violations.append((item.lineno, node.name, field_name))


def check_file(path: Path) -> list[tuple[int, str, str]]:
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as e:
        return [(e.lineno or 0, "SyntaxError", str(e))]

    checker = SchemaMaxLengthChecker(str(path), source.splitlines())
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
            print(f"{path}:{lineno}: [{class_name}.{field_name}] 缺少 max_length")
            total += 1

    if total:
        print(f"\n發現 {total} 個 Schema Drift 風險：str 欄位缺少 max_length")
        print("修法（優先）：使用 pydantic_model_creator 自動從 ORM model 派生 schema")
        print("修法（手動）：查 api/src/database/models.py 對應 CharField(max_length=N)，補上 max_length=N")
        print("若確認此 schema 不是使用者輸入路徑（回應/摘要/外部 API 解析），")
        print("可在 class 定義正上方加註解：# schema-max-length: skip")

    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
