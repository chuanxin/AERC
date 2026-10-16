/**
 * 從 Content-Disposition 標頭取出下載檔名。
 *
 * 後端以 RFC 5987 的 `filename*=UTF-8''<percent-encoded>` 送出檔名；舊的 `filename=` 寫法仍相容。
 * 兩者並存時 `filename*` 優先（RFC 6266）。取不到時回傳 undefined，由瀏覽器自行決定檔名。
 */
export function parseContentDispositionFilename(header?: string | null): string | undefined {
  if (!header) return undefined

  // filename*=charset'language'value —— 只需 value；charset 一律視為 UTF-8（後端固定如此）
  const extended = /filename\*\s*=\s*[^']*'[^']*'([^;]+)/i.exec(header)
  if (extended?.[1]) {
    const raw = extended[1].trim()
    try {
      return decodeURIComponent(raw)
    } catch {
      return raw // 非合法 percent-encoding：保留原字串，不丟例外中斷下載
    }
  }

  const plain = /filename\s*=\s*(?:"([^"]*)"|([^;]+))/i.exec(header)
  const value = (plain?.[1] ?? plain?.[2])?.trim()
  return value || undefined
}
