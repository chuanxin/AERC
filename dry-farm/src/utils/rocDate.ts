/**
 * 民國年月日格式化。
 *
 * 專案內原本沒有這個工具——既有 20 餘處 `1911` 全部只是
 * `new Date().getFullYear() - 1911` 取當前民國年，沒有完整日期的格式化。
 * 公告的發布日期在所有使用者可見的位置都必須以民國年月日顯示（FR-015），
 * 三處以上各自 inline 轉換必定漂移（月日是否補零、分隔符號用 . 還是 /），
 * 故集中於此。
 *
 * 格式沿用既有公告資料的既定形式 `YYY.MM.DD`（例：115.06.12），月日補零
 * ——那是使用者已經看慣的樣子。
 */

/**
 * 西元日期字串（ISO `YYYY-MM-DD`，或任何 Date 可解析的值）轉民國 `YYY.MM.DD`。
 *
 * 無法解析或空值時回傳空字串，不拋例外也不回傳 `NaN.NaN.NaN`
 * ——畫面上的空白比錯誤的日期誠實。
 */
export function toRocDate (value: string | Date | null | undefined): string {
  if (!value) return ''

  // 只取日期部分再解析，避免時區位移把 2026-01-01 變成 2025-12-31
  const d = typeof value === 'string'
    ? parseIsoDateOnly(value)
    : value

  if (!d || Number.isNaN(d.getTime())) return ''

  const rocYear = d.getFullYear() - 1911
  if (rocYear <= 0) return ''

  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${rocYear}.${mm}.${dd}`
}

/**
 * 解析 `YYYY-MM-DD`（允許後綴時間）為**當地時區**的 Date。
 *
 * 刻意不用 `new Date('2026-01-01')`——那會被當成 UTC 午夜，在 UTC+8
 * 顯示為前一天。公告的 publish_date 是純日期、無時區語意。
 */
function parseIsoDateOnly (value: string): Date | null {
  const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(value.trim())
  if (!m) {
    const fallback = new Date(value)
    return Number.isNaN(fallback.getTime()) ? null : fallback
  }
  return new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]))
}

/** 當前民國年（既有頁面已有多處 inline 實作，此處供新程式使用） */
export function currentRocYear (): number {
  return new Date().getFullYear() - 1911
}
