/**
 * 補助申請流程 - 費用計算與顯示格式化工具
 * 使用字串截斷方式無條件捨去，不四捨五入
 */

/**
 * 公頃截斷顯示至小數第6位
 */
export const truncHa = (value: number): string => {
  const s = value.toFixed(15)
  const dot = s.indexOf('.')
  return s.slice(0, dot + 7).padEnd(dot + 7, '0')
}

/**
 * 平方公尺截斷顯示至小數第2位
 */
export const truncM2 = (value: number): string => {
  const s = value.toFixed(10)
  const dot = s.indexOf('.')
  return s.slice(0, dot + 3).padEnd(dot + 3, '0')
}

/**
 * 無條件捨去取整數
 */
export const floorInt = (value: number): number => Math.floor(value)
