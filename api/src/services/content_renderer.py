"""公告內容管線：Markdown 渲染 + 消毒。

設計要點（詳見 specs/040-announcement-management/data-model.md §3）：

1. **渲染發生在輸出端，不入庫。** 資料庫只儲存作者輸入的 Markdown 原文；
   呈現用的 HTML 於讀取時即時產生。渲染 + 消毒成本實測約 249 µs／則，
   而列表端點不回傳內容，因此只在單筆明細發生。

2. **兩層防線，職責不同：**
   - `html=False`：作者夾帶的原始碼被**轉義為文字**，攻擊在成為標記之前就失效。
     這比「先解析再消毒」更前面一步。
   - `nh3.clean()`：允許清單、URL 協定、連結加固。渲染器不是安全邊界，此層為縱深防禦。

3. **`breaks=True` 是強制的。** 預設 CommonMark 把單一換行當軟換行吃掉，
   既有 5 則純文字公告的行結構會全毀（兩行併為一行），且不會有任何錯誤訊息。
"""

import re
from typing import List, Set

import nh3
from markdown_it import MarkdownIt

# ── 渲染器 ────────────────────────────────────────────────────────────────
# html=False：不解析作者夾帶的原始 HTML，一律轉義為文字
# breaks=True：單一換行 → <br>（既有純文字公告的行結構依賴此設定）
_md = MarkdownIt("commonmark", {"breaks": True, "html": False})

# ── 消毒允許清單 ──────────────────────────────────────────────────────────
# 原則：允許清單即「渲染器可能產生的標籤」，不多開。
ALLOWED_TAGS: Set[str] = {
    "p", "br", "strong", "em",
    "ul", "ol", "li",
    "a", "img",
    "h1", "h2", "h3", "h4", "h5", "h6",
    "blockquote", "code", "pre", "hr",
}

# img 刻意不允許 width / height：兩者是呈現屬性，放行 height="300"
# 與阻擋 style="height:300px" 在語意上是同一件事，與「內容不攜帶樣式」相牴觸。
# Markdown 語法本來就產生不出它們，擋掉零成本。
ALLOWED_ATTRIBUTES = {
    "a": {"href", "title"},
    "img": {"src", "alt", "title"},
}

ALLOWED_URL_SCHEMES: Set[str] = {"http", "https", "mailto"}

# 連結加固：target="_blank" 時尤其必要（防 reverse tabnabbing）
_LINK_REL = "noopener noreferrer"


def render(markdown_text: str | None) -> str:
    """把 Markdown 原文渲染為可安全呈現的 HTML。

    這是唯一的渲染入口，供公開明細、管理明細、預覽端點共用。
    """
    if not markdown_text:
        return ""
    return nh3.clean(
        _md.render(markdown_text),
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        url_schemes=ALLOWED_URL_SCHEMES,
        link_rel=_LINK_REL,
    )


# ── 差異報告（僅供產生給人看的提示，不參與任何安全判定）────────────────────
#
# 安全由 render() 的兩層負責；此處掃描漏報只會少一句提示，不會放行任何內容。
# 四類缺一不可——只掃標籤會讓一段純行內樣式的貼上內容得到「有變動但列不出
# 變動內容」，而從 Word 或網頁貼上必然帶大量 style，那是最高頻的情況。

_RE_HTML_TAG = re.compile(r"<\s*/?\s*([a-zA-Z][a-zA-Z0-9]*)[\s/>]")
_RE_EVENT_ATTR = re.compile(r"\b(on[a-z]+)\s*=", re.IGNORECASE)
_RE_STYLE_ATTR = re.compile(r"\b(style|class)\s*=", re.IGNORECASE)
_RE_BAD_SCHEME = re.compile(r"\b(javascript|data|vbscript)\s*:", re.IGNORECASE)


def scan_notices(markdown_text: str | None) -> List[str]:
    """列出輸入中會被轉義或移除的形式，去重後回傳。

    四類：夾帶的原始碼標籤、on* 事件屬性、style/class 樣式指定、被拒絕的連結協定。
    """
    if not markdown_text:
        return []
    found: List[str] = []
    seen: Set[str] = set()

    def add(item: str) -> None:
        low = item.lower()
        if low not in seen:
            seen.add(low)
            found.append(low)

    for m in _RE_HTML_TAG.finditer(markdown_text):
        add(m.group(1))
    for m in _RE_EVENT_ATTR.finditer(markdown_text):
        add(m.group(1))
    for m in _RE_STYLE_ATTR.finditer(markdown_text):
        add(m.group(1))
    for m in _RE_BAD_SCHEME.finditer(markdown_text):
        add(m.group(1))
    return found


def preview(markdown_text: str | None) -> dict:
    """供編輯期回饋：回傳渲染結果與差異報告。

    `changed` 的權威判定是「輸入中是否含會被轉義或移除的形式」，
    以 scan_notices 是否有命中為準；notices 為給人看的清單。
    """
    notices = scan_notices(markdown_text)
    return {
        "content": render(markdown_text),
        "changed": bool(notices),
        "notices": notices,
    }
