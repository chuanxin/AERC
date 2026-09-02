#!/usr/bin/env python3
"""偵測「同樣的邏輯被抄成第二份」——結構相同但函式名不同的重複實作。

為什麼掃全樹而不只掃變更檔
--------------------------
重複是**跨檔案**的關係，只看本次變更的檔案永遠比不出來（改 A 檔時另一份在 B 檔）。
因此本檢查一律建立 api/src 全樹的索引，再篩出「至少有一個成員落在本次變更檔案裡」
的組回報。沒碰到的既有重複不會擋你 commit。

比對方式與它的界線
------------------
把函式主體的 AST 正規化（去 docstring、參數與區域變數改成位置代號、保留呼叫目標
與字面值）後雜湊比對。**這代表它只抓得到結構相同的重複**——同一份邏輯若一份寫成
`return a or b`、另一份寫成三行 `if`，AST 不相等，本檢查抓不到。那類重複要靠寫之前
先用特徵字面值（header 名、環境變數鍵、magic number）grep 一次既有實作，工具接不住。

門檻：主體至少 3 行、排除 dunder。此組合在本專案實測為零誤報。

例外標記
--------
確認是刻意保留的重複，在函式定義正上方加註解：

    # duplicate-check: skip

已知且暫時接受的重複，記在 duplicate_functions_baseline.txt（一行一組，成員以
逗號分隔），格式與內容由 --update-baseline 產生。
"""

import ast
import sys
from collections import defaultdict
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parent.parent / "src"
BASELINE = Path(__file__).resolve().parent / "duplicate_functions_baseline.txt"
MIN_BODY_LINES = 3
SKIP_MARKER = "# duplicate-check: skip"


class _Normalizer(ast.NodeTransformer):
    """參數與區域變數改成位置代號；呼叫目標、屬性名、字面值原樣保留。

    保留後三者是刻意的——它們承載語意。全部抹平會把「兩個都是三行 if」這種
    骨架相同、內容無關的函式判成重複。
    """

    def __init__(self):
        self.names: dict[str, str] = {}

    def visit_arg(self, node: ast.arg) -> ast.arg:
        node.arg = self.names.setdefault(node.arg, f"v{len(self.names)}")
        return node

    def visit_Name(self, node: ast.Name) -> ast.Name:
        if node.id in self.names:
            node.id = self.names[node.id]
        return node


def _signature(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> str | None:
    """回傳可比對的正規化主體；不符門檻回傳 None。"""
    body = list(fn.body)
    if (
        body
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)
    ):
        body = body[1:]                                   # docstring 不參與比對
    if not body:
        return None
    reparsed = ast.parse(ast.unparse(ast.Module(body=body, type_ignores=[])))
    stub = ast.FunctionDef(
        name="_", args=fn.args, body=reparsed.body,
        decorator_list=[], returns=None, type_params=[],
    )
    stub = _Normalizer().visit(stub)
    ast.fix_missing_locations(stub)
    source = ast.unparse(stub)
    return source if source.count("\n") >= MIN_BODY_LINES - 1 else None


def _has_skip_marker(lines: list[str], fn_lineno: int) -> bool:
    """函式定義（含裝飾器）正上方是否有 skip 註解。"""
    i = fn_lineno - 2                                     # 0-indexed 的前一行
    while i >= 0:
        stripped = lines[i].strip()
        if stripped.startswith("@") or not stripped:
            i -= 1
            continue
        return stripped.startswith(SKIP_MARKER)
    return False


def build_index(root: Path) -> dict[str, list[tuple[str, int, str]]]:
    """全樹索引：正規化主體 → [(相對路徑, 行號, 函式名), ...]"""
    index: dict[str, list[tuple[str, int, str]]] = defaultdict(list)
    for path in sorted(root.rglob("*.py")):
        if "/tests/" in str(path) or "/migrations/" in str(path):
            continue
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (SyntaxError, UnicodeDecodeError):
            continue                                      # 語法錯誤交給別的檢查報
        lines = source.splitlines()
        rel = str(path.relative_to(root.parent.parent))
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if node.name.startswith("__"):                # dunder 天生長得一樣
                continue
            if _has_skip_marker(lines, node.lineno):
                continue
            sig = _signature(node)
            if sig:
                index[sig].append((rel, node.lineno, node.name))
    return index


def _group_key(members: list[tuple[str, int, str]]) -> str:
    """組的識別鍵用成員清單，不用雜湊——行號改變不影響，且人看得懂。"""
    return ",".join(sorted(f"{rel}::{name}" for rel, _, name in members))


def load_baseline() -> set[str]:
    if not BASELINE.is_file():
        return set()
    return {
        line.strip()
        for line in BASELINE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    }


def find_duplicates(changed: set[str]) -> list[list[tuple[str, int, str]]]:
    """回報牽涉到 changed 的重複組；baseline 內的略過。changed 為空則回報全部。"""
    baseline = load_baseline()
    found = []
    for members in build_index(SRC_ROOT).values():
        if len(members) < 2:
            continue
        if _group_key(members) in baseline:
            continue
        if changed and not any(rel in changed for rel, _, _ in members):
            continue
        found.append(members)
    return sorted(found, key=lambda m: -len(m))


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--update-baseline"]
    if "--update-baseline" in sys.argv:
        groups = find_duplicates(changed=set())
        BASELINE.write_text(
            "# 已知且暫時接受的重複實作。一行一組，成員為 路徑::函式名（逗號分隔）。\n"
            "# 由 check_duplicate_functions.py --update-baseline 產生。\n"
            "# 新增一行等於宣告「這個重複我知道，先不處理」——請同時開 TD 追蹤。\n"
            + "".join(_group_key(m) + "\n" for m in groups),
            encoding="utf-8",
        )
        print(f"baseline 已更新：{len(groups)} 組 → {BASELINE}")
        return 0

    changed = {a for a in args if a.startswith("api/src/")}
    duplicates = find_duplicates(changed)
    if not duplicates:
        return 0

    for members in duplicates:
        print(f"\n重複實作（{len(members)} 份，結構相同）：")
        for rel, lineno, name in members:
            print(f"    {rel}:{lineno}  {name}()")

    print(f"\n發現 {len(duplicates)} 組重複實作。")
    print("修法：留一份放到共用模組，其餘改為 import——不是把它們改成長得不一樣。")
    print(f"確認是刻意保留：在函式定義正上方加 `{SKIP_MARKER}`。")
    print("暫時接受（請同時開 TD 追蹤）：")
    print("    python api/scripts/check_duplicate_functions.py --update-baseline")
    return 1


if __name__ == "__main__":
    sys.exit(main())
