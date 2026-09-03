#!/usr/bin/env python3
"""一次性匯入：把部署機上現行的公告，從前端資料檔搬進 announcements 資料表。

040 之前，公告寫在 dry-farm/src/data/announcement.ts 這個前端資料檔裡，改完要
重新 build 才會更新。040 之後公告改由資料庫與管理介面維護，本腳本負責搬既有內容，
**只跑一次**。

為什麼資料不放在 migration 裡
------------------------------
放進 migration 就得把內容寫死成快照，而快照只等於某次送交時的樣子。客戶會直接在
他們那邊改這個檔（git 記錄有六次 "Sync changes from SVN trunk (manual
modifications by client)"），部署機上的實際內容無法預先得知，寫死的快照極可能
與實際不符——而不符的長相是「幾則看起來完全正常的公告」，沒有人分得出哪幾則該在、
哪幾則不該在，也沒有任何錯誤訊息。
改用腳本則是讀部署機上的真實檔案，對不對在 dry-run 報表上看得見。代價是要人記得
跑；漏跑的後果是公告頁空白，會被立刻發現，不會靜默錯下去。

只能跑一次，且必須在公告改由管理介面維護之前
--------------------------------------------
本腳本以標題為鍵覆寫內容。上線後若有人用管理介面編輯過公告，再跑一次會把那些編輯
回捲成 announcement.ts 的舊內容。故 --apply 偵測到下列任一跡象就拒絕執行，要繼續
必須明確加 --force：
  - 有 created_by 非空的公告（＝有人用管理介面建立過）
  - 有 updated_at 明顯晚於 created_at 的公告（＝有人編輯過）

涵蓋範圍（誠實的界線）
----------------------
以標題為鍵 upsert：標題存在就更新內容，不存在就新增。**不刪除**資料庫既有的任何
公告。因此「來源把標題改掉了」會變成新增一則、舊標題那則留著；「來源把某則刪掉了」
則是資料庫那則留著。兩者都不會有錯誤訊息，跑完請自行核對筆數。

三點刻意的設計
--------------
1. **只寫 content_markdown，不做渲染。** 與 POST 寫入路徑相同，沒有匯入專用分支
   ——渲染一律發生在輸出端（services/content_renderer.py），這裡不重複消毒。
2. **type_id 以名稱查出，不寫死。** migration 76 的 seed 不指定 id，寫死整數會在
   seed 順序變更時靜默寫錯類型。
3. **INSERT 不指定 id，交給序列。** AERC-0417 教訓：手動指定 id 會讓序列落後於
   實際資料，之後每次新增都撞主鍵。

HTML→Markdown 的界線
--------------------
來源可能有 `<div class="pdf-announcement">` 固定模板的 HTML。它不能原樣移入——
渲染管線 html=False，整段會被逃生成純文字。本腳本對這個固定模板做確定性轉換
（抽 <p> 說明句、縮圖 <a>/<img src>/<img alt>、下載 <a> 文字）。結構固定所以轉換
可驗證，但**結果仍須在 dry-run 報表上人工確認**。若結構偏離模板而抽不出必要欄位、
或出現非此模板的 HTML，一律報錯中止，不靜默降級成純文字。

來源欄位對映（不可按同名對映）
------------------------------
    目標 title            ← 來源 content（來源沒有 title 欄位）
    目標 content_markdown ← 來源 fullContent
按字面同名對映會把標題存進內容欄，而且不會有任何錯誤訊息。

用法
----
    # 1. 先跑 migration 建表與公告類型
    docker exec -w /app aerc-api-1 aerich upgrade
    # 2. 把部署機上的 announcement.ts 複製進容器
    docker cp dry-farm/src/data/announcement.ts aerc-api-1:/tmp/announcement.ts
    # 3. dry-run（預設），逐則核對報表內容
    docker exec -w /app aerc-api-1 \\
        python scripts/import_announcements.py /tmp/announcement.ts
    # 4. 確認無誤才寫入
    docker exec -w /app aerc-api-1 \\
        python scripts/import_announcements.py /tmp/announcement.ts --apply
"""

import argparse
import asyncio
import logging
import re
import sys
from datetime import date, datetime, time, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 一、TS 原始碼解析
# ---------------------------------------------------------------------------
# announcement.ts 是 JS 陣列字面值 `[{...},{...}]`，欄位值有單引號字串與
# backtick 樣板字串（HTML 那兩則用 backtick，內含真實換行）；`//` 行註解
# 把 id 1 那則「停機公告」整段註解掉。用字元掃描器剝掉註解、壓掉字串外空白、
# 保留字串內容，再以括號配對切出每個物件元素。


def _strip_comments_and_space(ts: str) -> str:
    """剝掉 // 與 /* */ 註解，壓掉字串外的空白；字串內容原樣保留。"""
    out = []
    i, n = 0, len(ts)
    while i < n:
        c = ts[i]
        if c in ("'", '"', "`"):
            quote = c
            j = i + 1
            buf = quote
            while j < n and ts[j] != quote:
                if c != "`" and ts[j] == "\\" and j + 1 < n:
                    buf += ts[j] + ts[j + 1]
                    j += 2
                    continue
                buf += ts[j]
                j += 1
            buf += quote
            out.append(buf)
            i = j + 1
        elif c == "/" and i + 1 < n and ts[i + 1] == "/":
            while i < n and ts[i] != "\n":
                i += 1
        elif c == "/" and i + 1 < n and ts[i + 1] == "*":
            i += 2
            while i + 1 < n and not (ts[i] == "*" and ts[i + 1] == "/"):
                i += 1
            i += 2
        elif c in "\n\r\t ":
            i += 1
        else:
            out.append(c)
            i += 1
    return "".join(out)


def _split_elements(clean: str) -> list[str]:
    """在剝淨後的字串上，用括號配對切出每個 `{...}` 物件元素。

    錨點是 `[{` 而非單純的 `[`——檔案裡在資料陣列之前就有 `Announcement[]` 這個
    型別標註，錨在第一個 `[` 只是碰巧因為它和真陣列之間沒有 `{` 才正確。
    """
    start = clean.find("[{")
    if start < 0:
        raise ValueError("找不到物件陣列起始 `[{`——來源檔結構與預期不符")
    elements = []
    i, n = start + 1, len(clean)
    while i < n:
        if clean[i] != "{":
            i += 1
            continue
        depth, j = 0, i
        while j < n:
            if clean[j] == "{":
                depth += 1
            elif clean[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        if j >= n:
            raise ValueError(f"物件未閉合: {clean[i : i + 60]}...")
        elements.append(clean[i : j + 1])
        i = j + 1
    return elements


_ESCAPES = {"n": "\n", "t": "\t", "r": "\r", "'": "'", '"': '"', "`": "`", "\\": "\\"}


def _decode(value: str) -> str:
    """解開引號包住的欄位值：單/雙引號版解 \n\\ 等跳脫；backtick 樣板原樣。"""
    body = value[1:-1]
    if value[0] not in ("'", '"'):
        return body
    out, i, n = [], 0, len(body)
    while i < n:
        if body[i] == "\\" and i + 1 < n and body[i + 1] in _ESCAPES:
            out.append(_ESCAPES[body[i + 1]])
            i += 2
        else:
            out.append(body[i])
            i += 1
    return "".join(out)


def _extract_element(element: str) -> dict:
    """從單一 `{id:.., date:.., type:.., content:.., fullContent:..}` 抽出欄位。

    id 是未加引號的整數，其餘欄位是引號字串（單引號或 backtick）。
    """
    fields = {}
    mid = re.search(r"\bid\s*:\s*(\d+)", element)
    if not mid:
        raise ValueError(f"物件缺 id: {element[:60]}...")
    fields["id"] = mid.group(1)
    for key in ("date", "type", "content", "fullContent"):
        m = re.search(r"\b" + key + r"\s*:\s*(['\"`])", element)
        if not m:
            raise ValueError(f"物件缺欄位 {key}: {element[:60]}...")
        quote, start = m.group(1), m.end()
        end = start
        while end < len(element):
            if element[end] == quote:
                if element[end - 1] == "\\":
                    end += 1
                    continue
                break
            end += 1
        if end >= len(element):
            raise ValueError(f"欄位 {key} 字串未閉合")
        fields[key] = _decode(quote + element[start:end] + quote)
    return fields


# ---------------------------------------------------------------------------
# 二、值轉換
# ---------------------------------------------------------------------------
def _roc_to_iso(roc: str) -> date:
    """民國 YYY.MM.DD → ISO date。115.06.12 → 2026-06-12（+1911）。"""
    parts = roc.strip().split(".")
    if len(parts) != 3:
        raise ValueError(f"無法解析民國日期: {roc!r}")
    try:
        return date(int(parts[0]) + 1911, int(parts[1]), int(parts[2]))
    except ValueError as e:
        raise ValueError(f"民國日期 {roc!r} 不是合法日期: {e}") from e


def _html_pdf_to_markdown(html: str) -> str:
    """把固定模板 `<div class="pdf-announcement">` HTML 轉成 Markdown。

    確定性：抽 <p> 說明句、縮圖 <a href>/<img src>/<img alt>、下載 <a> 文字，
    組成「說明句 / 可點擊縮圖 / 下載連結」三段式 Markdown。抽不出必要欄位就報錯。
    """
    p = re.search(r"<p[^>]*>(.*?)</p>", html, re.DOTALL)
    intro = p.group(1).strip() if p else None

    img = re.search(
        r'<a\s+href="([^"]+)"[^>]*>\s*<img\s+src="([^"]+)"[^>]*\s+alt="([^"]*)"',
        html,
        re.DOTALL,
    )
    thumb_link = img.group(1) if img else None
    img_src = img.group(2) if img else None
    img_alt = img.group(3).strip() if img else None

    a_tags = re.findall(r'<a\s+href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
    download_link = download_text = None
    for href, inner in a_tags:
        if "<img" not in inner:  # 下載連結是「非縮圖」的那個 <a>
            download_link = href
            download_text = re.sub(r"<[^>]+>", "", inner).strip()

    missing = [
        name
        for name, v in (
            ("<p> 說明句", intro),
            ("縮圖 <a href>", thumb_link),
            ("<img src>", img_src),
            ("<img alt>", img_alt),
            ("下載 <a href>", download_link),
            ("下載 <a> 文字", download_text),
        )
        if not v
    ]
    if missing:
        raise ValueError(
            "HTML 模板與預期不符，無法確定性轉換，缺: " + ", ".join(missing)
            + "。請人工檢查該則 fullContent 後再決定如何處理。"
        )
    # download_text 直接取自來源 <a> 內文，該內文本身通常已含「👉 點此下載：」之類
    # 的前綴；此處不可再補一次，否則會變成雙重前綴。
    return (
        f"{intro}\n\n"
        f"[![{img_alt}]({img_src})]({thumb_link})\n\n"
        f"[{download_text}]({download_link})"
    )


def _to_markdown(full_content: str) -> str:
    """fullContent → content_markdown。

    純文字原樣；固定模板 HTML 走確定性轉換。出現未預期 HTML 或轉失敗就報錯，
    拒絕靜默降級成純文字（那會把 HTML 當內容存，渲染時全被逃生成純文字）。
    """
    has_html = "<" in full_content and ">" in full_content
    if has_html:
        if "pdf-announcement" not in full_content:
            raise ValueError(
                "fullContent 含未預期的 HTML 標記（非固定 pdf-announcement 模板），"
                "無法自動轉換，請人工處理。"
            )
        return _html_pdf_to_markdown(full_content)
    return full_content


# ---------------------------------------------------------------------------
# 三、匯入主程式
# ---------------------------------------------------------------------------
def build_rows(elements: list[dict]) -> list[dict]:
    """把來源元素轉成匯入行列，並擋下來源重複標題。"""
    rows, seen_titles = [], {}
    for el in elements:
        # 標題原樣保留（含結尾空白）——upsert 以 title 為鍵，若在此 strip，遇到
        # 資料庫裡已存在的含尾空白標題就會查不到，靜默插成重複的一則。
        title = el.get("content") or ""
        if not title.strip():
            continue
        if title in seen_titles:
            raise ValueError(
                f"來源標題重複: {title!r}（id {seen_titles[title]} 與 {el.get('id')}）"
            )
        seen_titles[title] = el.get("id")
        rows.append(
            {
                "title": title,
                "publish_date": _roc_to_iso(el["date"]),
                "type_name": (el.get("type") or "").strip(),
                "content_markdown": _to_markdown(el["fullContent"]),
            }
        )
    return rows


def _fmt(md: str) -> str:
    """把 Markdown 壓成單行供報表閱讀（首行 + 行數）。"""
    lines = md.split("\n")
    head = lines[0] if lines else ""
    return (head + f" ...(+{len(lines)-1} 行)") if len(lines) > 1 else head


async def _detect_live_usage(Announcement) -> list[str]:
    """找出「公告已改由管理介面維護」的跡象，回傳人類可讀的說明列。

    兩個跡象都指向同一件事：資料庫裡的內容已經不再只是本腳本匯入的東西。此時再
    以標題為鍵覆寫，會把管理介面上的編輯回捲成 announcement.ts 的舊內容。
    """
    signs = []
    created_via_ui = await Announcement.filter(created_by_id__not_isnull=True).count()
    if created_via_ui:
        signs.append(f"有 {created_via_ui} 則公告的 created_by 非空（經管理介面建立）")
    # auto_now_add 與 auto_now 在同一次 INSERT 幾乎同時取值，容忍 2 秒
    edited = [
        a
        for a in await Announcement.all().only("id", "title", "created_at", "updated_at")
        if (a.updated_at - a.created_at).total_seconds() > 2
    ]
    if edited:
        listed = "、".join(f"id={a.id} {a.title[:16]!r}" for a in edited[:5])
        more = f" 等 {len(edited)} 則" if len(edited) > 5 else ""
        signs.append(f"有公告的 updated_at 晚於 created_at（曾被編輯）：{listed}{more}")
    return signs


async def run(path: str, apply: bool, force: bool = False) -> int:
    # 延遲 import，確保環境變數（DATABASE_URL）已就緒
    from tortoise import Tortoise
    from src.database.config import TORTOISE_ORM
    from src.database.models import Announcement, AnnouncementType

    source_path = Path(path)
    if not source_path.is_file():
        logger.error(f"找不到來源檔案: {source_path}")
        return 2
    ts_text = source_path.read_text(encoding="utf-8")

    elements = [
        _extract_element(e)
        for e in _split_elements(_strip_comments_and_space(ts_text))
    ]
    if not elements:
        logger.error("來源檔案中沒有解析出任何公告元素")
        return 2
    rows = build_rows(elements)
    logger.info(f"來源解析完成：{len(elements)} 則 → {len(rows)} 筆待匯入")
    for r in rows:
        logger.info(
            f"  - [{r['publish_date']}] {r['type_name']} {r['title']!r}"
            f"  md={_fmt(r['content_markdown'])}"
        )

    await Tortoise.init(config=TORTOISE_ORM)

    # type_id 以名稱逐一解析；名稱不同 → 失敗，回報該名稱，不猜、不寫死
    type_cache = {}
    try:
        # 本腳本只該在公告改由管理介面維護之前跑一次；之後再跑會回捲介面上的編輯
        signs = await _detect_live_usage(Announcement)
        if signs:
            for s in signs:
                logger.warning(f"跡象：{s}")
            if apply and not force:
                logger.error(
                    "公告看來已在管理介面上被使用，--apply 已中止——本腳本以標題為鍵"
                    "覆寫內容，會把介面上的編輯回捲成 announcement.ts 的舊內容。"
                    "確認要覆寫請加 --force。"
                )
                return 3
            if apply:
                logger.warning("--force 已指定，仍將覆寫上述內容")

        n_insert = n_update = n_skip = 0
        for r in rows:
            tname = r["type_name"] or "系統公告"
            if tname not in type_cache:
                t = await AnnouncementType.get_or_none(name=tname)
                if t is None:
                    raise ValueError(
                        f"類型「{tname}」不存在於 announcement_types——"
                        f"請先確認 migration 76 seed 與管理介面的類型維護"
                    )
                type_cache[tname] = t.id
            type_id = type_cache[tname]

            # title 沒有唯一約束，不能用 get_or_none（多筆時它拋的例外不會說是哪一則）
            matched = await Announcement.filter(title=r["title"])
            if len(matched) > 1:
                raise ValueError(
                    f"資料庫已有 {len(matched)} 則同標題公告 {r['title']!r}"
                    f"（id={[m.id for m in matched]}），無法判斷該更新哪一則，請先人工處理"
                )
            exists = matched[0] if matched else None
            if exists is None:
                n_insert += 1
                logger.info(f"[新增] {r['title']!r} → {r['publish_date']} (type_id={type_id})")
                if apply:
                    await Announcement.create(
                        title=r["title"],
                        type_id=type_id,
                        content_markdown=r["content_markdown"],
                        publish_date=r["publish_date"],
                        status="published",
                        is_pinned=False,
                        created_by_id=None,
                        published_at=datetime.combine(
                            r["publish_date"], time.min, tzinfo=timezone.utc
                        ),
                    )
                continue

            same = (
                exists.content_markdown == r["content_markdown"]
                and exists.publish_date == r["publish_date"]
                and exists.type_id == type_id
            )
            if same:
                n_skip += 1
                logger.info(f"[略過] {r['title']!r} 內容一致")
                continue
            n_update += 1
            logger.info(f"[更新] {r['title']!r} (id={exists.id}) → 更新內容欄位")
            if apply:
                exists.content_markdown = r["content_markdown"]
                exists.publish_date = r["publish_date"]
                exists.type_id = type_id
                await exists.save(update_fields=["content_markdown", "publish_date", "type_id"])

        logger.info("=" * 60)
        logger.info(f"摘要：新增 {n_insert} / 更新 {n_update} / 略過 {n_skip}")
        # 本腳本不刪除任何東西，所以「資料庫比來源多」是操作者必須自己判讀的訊號：
        # 可能是來源改過標題留下的舊那則、來源刪掉但資料庫還在，也可能是正常的新公告
        db_total = await Announcement.all().count()
        expected = db_total if apply else db_total + n_insert
        if expected > len(rows):
            logger.warning(
                f"資料庫共 {expected} 則，來源只有 {len(rows)} 則——多出的 "
                f"{expected - len(rows)} 則不在來源檔中。本腳本不刪除任何資料，"
                "請自行確認那幾則是該保留的公告，還是來源改標題／刪除後的殘留。"
            )
        if not apply:
            logger.info("DRY-RUN：未寫入任何資料。加 --apply 才真正匯入。")
        return 0
    finally:
        await Tortoise.close_connections()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="一次性匯入既有公告。預設 dry-run，--apply 才寫庫。",
    )
    parser.add_argument("path", help="dry-farm/src/data/announcement.ts 的容器內絕對路徑")
    parser.add_argument("--apply", action="store_true", help="實際寫入資料庫（預設僅 dry-run）")
    parser.add_argument(
        "--force",
        action="store_true",
        help="公告已在管理介面上被使用時仍強制覆寫（會回捲介面上的編輯）",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return asyncio.run(run(args.path, args.apply, args.force))


if __name__ == "__main__":
    sys.exit(main())
