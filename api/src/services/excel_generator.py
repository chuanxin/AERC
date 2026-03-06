from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
import tempfile
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
from copy import copy
from src.config.folder_mappings import settings

# ── 共用樣式常數（全報表共用）────────────────────────────────────────────────────
_XL_S_M = Side(style='medium')
_XL_S_T = Side(style='thin')

# 字型
_XL_F16  = Font(name='微軟正黑體', size=16)
_XL_F16B = Font(name='微軟正黑體', size=16, bold=True)
_XL_F12  = Font(name='微軟正黑體', size=12)
_XL_F14  = Font(name='微軟正黑體', size=14)

# 對齊
_XL_A_CTR  = Alignment(horizontal='center', vertical='center')
_XL_A_WRAP = Alignment(horizontal='center', vertical='center', wrap_text=True)
_XL_A_RT   = Alignment(horizontal='right', vertical='center')
_XL_A_NOTE = Alignment(horizontal='left', vertical='top', wrap_text=True)

# 列高
_XL_ROW_H_TITLE = 83.0
_XL_ROW_H_DATE  = 25.0
_XL_ROW_H_HDR1  = 25.0
_XL_ROW_H_HDR2  = 45.0
_XL_ROW_H_DATA  = 21.0
_XL_ROW_H_TOTAL = 21.0
_XL_ROW_H_NOTE  = 96.0

# ── A04/A05 規則建構常數（去範本化）──────────────────────────────────────────────
# 備註文字（A04/A05 共用）
_A0405_NOTE_TEXT = (
    '備註 :\n'
    '1、受理「補助案件」如跨越縣市/鄉鎮區土地，以第一筆縣市/鄉鎮區作為補助案件數之統計基準。\n'
)

# 每個年度欄頭的三格邊框（_tpl_merge_horizontal 使用；先設框再合併保留右外框）
_A0405_YEAR_HDR_BORDERS = [
    Border(left=_XL_S_M, right=_XL_S_M, top=_XL_S_M, bottom=_XL_S_T),  # 首欄
    Border(left=None,     right=None,     top=_XL_S_M, bottom=_XL_S_T),   # 中欄
    Border(left=None,     right=_XL_S_M, top=_XL_S_M, bottom=_XL_S_T),  # 末欄
]

# 子欄頭文字與邊框（補助案件數 / 補助面積 / 補助金額）
_A0405_SUBHDR_TEXT = ['補助案件數\n(已結案)', '補助面積(公頃)', '補助金額(元)']
_A0405_SUBHDR_BORDER = [
    Border(left=_XL_S_M, right=_XL_S_T, bottom=_XL_S_M),
    Border(left=_XL_S_T, right=_XL_S_T, bottom=_XL_S_M),
    Border(left=_XL_S_T, right=_XL_S_M, bottom=_XL_S_M),
]

# 資料格邊框（年度子欄，thin 分隔線）
_A0405_DATA_YEAR_BORDER = [
    Border(left=_XL_S_M, right=_XL_S_T, bottom=_XL_S_T),  # 案件數
    Border(left=_XL_S_T, right=_XL_S_T, bottom=_XL_S_T),  # 面積
    Border(left=_XL_S_T, right=_XL_S_M, bottom=_XL_S_T),  # 金額
]

# 固定欄頭邊框（key = (fixed_cols, col_0based)）
_A0405_FIXED_HDR_BORDER = {
    (2, 0): Border(left=_XL_S_M, right=_XL_S_T, top=_XL_S_M, bottom=_XL_S_M),  # A04 縣市
    (2, 1): Border(left=_XL_S_T, right=None,     top=_XL_S_M, bottom=_XL_S_M),  # A04 鄉鎮區
    (1, 0): Border(left=_XL_S_M, right=_XL_S_M, top=_XL_S_M, bottom=_XL_S_M),  # A05 管理處
}

# 固定欄 HDR2 底端格邊框（垂直合併後 _tpl_force_interior_border 注入）
_A0405_FIXED_HDR2_BORDER = {
    (2, 0): Border(left=_XL_S_M, right=_XL_S_T, bottom=_XL_S_M),
    (2, 1): Border(left=_XL_S_T, right=None,     bottom=_XL_S_M),
    (1, 0): Border(left=_XL_S_M, right=_XL_S_M, bottom=_XL_S_M),
}

# 固定欄資料格邊框
_A0405_FIXED_DATA_BORDER = {
    (2, 0): Border(left=_XL_S_M, right=_XL_S_T, bottom=_XL_S_T),
    (2, 1): Border(left=_XL_S_T, right=None,     bottom=_XL_S_T),
    (1, 0): Border(left=_XL_S_M, right=None,     bottom=_XL_S_T),
}

# 欄寬（fixed_cols → {col_0based: width, 'year': width_per_year_col}）
_A0405_COL_WIDTHS = {
    2: {0: 24.33, 1: 24.33, 'year': 24.33},  # A04 (fixed_cols=2)
    1: {0: 35.33,            'year': 24.33},  # A05 (fixed_cols=1)
}

# ── A02/A03/A07 規則建構常數（去範本化）─────────────────────────────────────────
# 表頭邊框（col_count, col_0based）
_A0203_HDR_BORDER = {
    # A02/A07 (5欄): 縣市 | 鄉鎮區 | 補助案件數 | 補助面積 | 補助金額
    (5, 0): Border(left=_XL_S_M, right=_XL_S_T, top=_XL_S_M, bottom=_XL_S_M),
    (5, 1): Border(left=_XL_S_T, right=_XL_S_M, top=_XL_S_M, bottom=_XL_S_M),
    (5, 2): Border(left=None,     right=_XL_S_T, top=_XL_S_M, bottom=_XL_S_M),
    (5, 3): Border(left=_XL_S_T, right=_XL_S_T, top=_XL_S_M, bottom=_XL_S_M),
    (5, 4): Border(left=_XL_S_T, right=_XL_S_M, top=_XL_S_M, bottom=_XL_S_M),
    # A03 (4欄): 管理處 | 補助案件數 | 補助面積 | 補助金額
    (4, 0): Border(left=_XL_S_M, right=_XL_S_M, top=_XL_S_M, bottom=_XL_S_M),
    (4, 1): Border(left=None,     right=_XL_S_T, top=_XL_S_M, bottom=_XL_S_M),
    (4, 2): Border(left=_XL_S_T, right=_XL_S_T, top=_XL_S_M, bottom=_XL_S_M),
    (4, 3): Border(left=_XL_S_T, right=_XL_S_M, top=_XL_S_M, bottom=_XL_S_M),
}
# 資料格邊框（col_count, col_0based）
_A0203_DATA_BORDER = {
    (5, 0): Border(left=_XL_S_M, right=_XL_S_T, bottom=_XL_S_T),
    (5, 1): Border(left=_XL_S_T, right=_XL_S_M, bottom=_XL_S_T),
    (5, 2): Border(left=None,     right=_XL_S_T, bottom=_XL_S_T),
    (5, 3): Border(left=_XL_S_T, right=_XL_S_T, bottom=_XL_S_T),
    (5, 4): Border(left=_XL_S_T, right=_XL_S_M, bottom=_XL_S_T),
    (4, 0): Border(left=_XL_S_M, right=_XL_S_M, bottom=_XL_S_T),
    (4, 1): Border(left=None,     right=_XL_S_T, bottom=_XL_S_T),
    (4, 2): Border(left=_XL_S_T, right=_XL_S_T, bottom=_XL_S_T),
    (4, 3): Border(left=_XL_S_T, right=_XL_S_M, bottom=_XL_S_T),
}
# 欄寬（col_count → {col_0based: width}）
_A0203_COL_WIDTHS = {
    5: {0: 24.33, 1: 24.33, 2: 24.33, 3: 24.33, 4: 24.33},  # A02/A07 (5欄)
    4: {0: 35.33, 1: 24.33, 2: 24.33, 3: 24.33},             # A03 (4欄)
}
# 表頭文字（col_count → [col 名稱]）
_A0203_HDR_TEXT = {
    5: ['縣市', '鄉鎮區', '補助案件數\n(已結案)', '補助面積(公頃)', '補助金額(元)'],
    4: ['管理處', '補助案件數\n(已結案)', '補助面積(公頃)', '補助金額(元)'],
}
# 表頭對齊（補助案件數含換行需 wrap_text）
_A0203_HDR_ALIGN = {
    5: [_XL_A_CTR, _XL_A_CTR, _XL_A_WRAP, _XL_A_CTR, _XL_A_CTR],
    4: [_XL_A_CTR, _XL_A_WRAP, _XL_A_CTR, _XL_A_CTR],
}

# ── A06 規則建構常數（去範本化）────────────────────────────────────────────────
_A06_COL_WIDTHS = {1: 35.33, **{i: 29 for i in range(2, 13)}}  # A欄35.33，其餘24.33
# 數字格式（1-based，與欄位對應）
_A06_NUM_FMT = {
    1:  'General',
    2:  'General',
    3:  '#,##0_);[Red](#,##0)',
    4:  'General',
    5:  'General',
    6:  '#,##0_);[Red](#,##0)',
    7:  '#,##0_ ;[Red]\\-#,##0\\ ',
    8:  'General',
    9:  'General',
    10: '#,##0_);[Red](#,##0)',
    11: '0.00_);[Red]\\(0.00\\)',
    12: '0.00_);[Red]\\(0.00\\)',
}
# 欄頭文字（Row 3，12 欄）
_A06_HDR_TEXT = [
    '管理處', '預定執行面積(公頃)', '預定執行預算(元)', '已編預算案件數',
    '已編預算面積(公頃)', '已編列補助款(元)', '未編列補助款(元)',
    '已驗收案件數', '已驗收面積(公頃)', '已驗收金額(元)', '面積執行率%', '計畫執行率%',
]
# 欄頭邊框（Row 3，0-based index；col 6/11 右側 None，視覺由相鄰格提供）
_A06_HDR_BORDER = [
    Border(left=_XL_S_M, right=_XL_S_T, top=_XL_S_M, bottom=_XL_S_M),  # 0 管理處
    Border(left=_XL_S_T, right=_XL_S_T, top=_XL_S_M, bottom=_XL_S_M),  # 1 預定面積
    Border(left=_XL_S_T, right=_XL_S_T, top=_XL_S_M, bottom=_XL_S_M),  # 2 預定預算
    Border(left=_XL_S_T, right=_XL_S_T, top=_XL_S_M, bottom=_XL_S_M),  # 3 已編案件數
    Border(left=_XL_S_T, right=_XL_S_T, top=_XL_S_M, bottom=_XL_S_M),  # 4 已編面積
    Border(left=_XL_S_T, right=None,     top=_XL_S_M, bottom=_XL_S_M),  # 5 已編補助款
    Border(left=_XL_S_T, right=_XL_S_T, top=_XL_S_M, bottom=_XL_S_M),  # 6 未編補助款
    Border(left=_XL_S_T, right=_XL_S_T, top=_XL_S_M, bottom=_XL_S_M),  # 7 已驗案件數
    Border(left=_XL_S_T, right=_XL_S_T, top=_XL_S_M, bottom=_XL_S_M),  # 8 已驗面積
    Border(left=_XL_S_T, right=_XL_S_T, top=_XL_S_M, bottom=_XL_S_M),  # 9 已驗金額
    Border(left=_XL_S_T, right=None,     top=_XL_S_M, bottom=_XL_S_M),  # 10 面積執行率
    Border(left=_XL_S_T, right=_XL_S_M, top=_XL_S_M, bottom=_XL_S_M),  # 11 計畫執行率
]
# 資料格邊框（0-based index；底線 thin，合計列改用 medium）
_A06_DATA_BORDER = [
    Border(left=_XL_S_M, right=_XL_S_T, bottom=_XL_S_T),  # 0
    Border(left=_XL_S_T, right=_XL_S_T, bottom=_XL_S_T),  # 1
    Border(left=_XL_S_T, right=_XL_S_T, bottom=_XL_S_T),  # 2
    Border(left=_XL_S_T, right=_XL_S_T, bottom=_XL_S_T),  # 3
    Border(left=_XL_S_T, right=_XL_S_T, bottom=_XL_S_T),  # 4
    Border(left=_XL_S_T, right=_XL_S_T, bottom=_XL_S_T),  # 5
    Border(left=_XL_S_T, right=_XL_S_T, bottom=_XL_S_T),  # 6
    Border(left=_XL_S_T, right=_XL_S_T, bottom=_XL_S_T),  # 7
    Border(left=_XL_S_T, right=_XL_S_T, bottom=_XL_S_T),  # 8
    Border(left=_XL_S_T, right=_XL_S_T, bottom=_XL_S_T),  # 9
    Border(left=_XL_S_T, right=None,     bottom=_XL_S_T),  # 10
    Border(left=_XL_S_T, right=_XL_S_M, bottom=_XL_S_T),  # 11
]
_A06_ROW_H_NOTE = 110.0
_A06_NOTE_TEXT = (
    '備註：\n'
    '    1、受理「補助案件」如跨越縣市/鄉鎮區土地，以第一筆縣市/鄉鎮區作為補助案件數之統計基準。\n'
    '計算公式 :\n'
    '    1、計畫執行率%=已編列補助款/預定執行預算。\n'
    '    2、面積執行率%=已編預算面積/預定執行面積。'
)
# Rich Text runs（underline: bool, text: str）；preserve 由 _inject_note_rich_text 自動判斷
_A06_NOTE_RUNS = (
    (False, '備註：\n    1、受理「補助案件」如跨越縣市/鄉鎮區土地，以第一筆縣市/鄉鎮區作為'),
    (True,  '補助案件數'),
    (False, '之統計基準。\n'),
    (True,  '計算公式 :'),
    (False, '\n    1、計畫執行率%=已編列補助款/預定執行預算。\n    2、面積執行率%=已編預算面積/預定執行面積。'),
)


# ── A01 規則建構常數（去範本化）────────────────────────────────────────────────
_A01_COL_WIDTHS = {1: 35.33, 2: 20.5, 3: 23.0, 4: 23.0, 5: 20.5, 6: 31.33}
_A01_HDR_TEXT = [
    '管理處', '核定金額(元)', '補助案件數\n(已結案)', '補助面積(公頃)', '補助金額(元)', '補助款\n執行率%',
]
_A01_HDR_ALIGN = [_XL_A_CTR, _XL_A_CTR, _XL_A_WRAP, _XL_A_CTR, _XL_A_CTR, _XL_A_WRAP]
_A01_HDR_BORDER = [
    Border(left=_XL_S_M, right=_XL_S_M, top=_XL_S_M, bottom=_XL_S_M),  # 0 管理處
    Border(left=None,     right=_XL_S_T, top=_XL_S_M, bottom=_XL_S_M),  # 1 核定金額
    Border(left=_XL_S_T, right=_XL_S_T, top=_XL_S_M, bottom=_XL_S_M),  # 2 補助案件數
    Border(left=_XL_S_T, right=_XL_S_T, top=_XL_S_M, bottom=_XL_S_M),  # 3 補助面積
    Border(left=_XL_S_T, right=None,     top=_XL_S_M, bottom=_XL_S_M),  # 4 補助金額
    Border(left=_XL_S_T, right=_XL_S_M, top=_XL_S_M, bottom=_XL_S_M),  # 5 執行率
]
_A01_DATA_BORDER = [
    Border(left=_XL_S_M, right=_XL_S_M, bottom=_XL_S_T),  # 0 管理處（獨立欄，兩側 medium）
    Border(left=None,     right=_XL_S_T, bottom=_XL_S_T),  # 1 核定金額
    Border(left=_XL_S_T, right=_XL_S_T, bottom=_XL_S_T),  # 2 補助案件數
    Border(left=_XL_S_T, right=_XL_S_T, bottom=_XL_S_T),  # 3 補助面積
    Border(left=_XL_S_T, right=_XL_S_T, bottom=_XL_S_T),  # 4 補助金額
    Border(left=_XL_S_T, right=_XL_S_M, bottom=_XL_S_T),  # 5 執行率
]
_A01_NUM_FMT = {1: 'General', 2: '#,##0_ ', 3: 'General', 4: 'General', 5: '#,##0_ ', 6: '0.00%'}
_A01_NOTE_TEXT = (
    '備註 :\n'
    '1、受理「補助案件」如跨越縣市/鄉鎮區土地，以第一筆縣市/鄉鎮區作為補助案件數之統計基準。\n'
    '2、計算公式：補助款執行率%=補助金額/核定金額。'
)
# Rich Text runs（underline: bool, text: str）；preserve 由 _inject_note_rich_text 自動判斷
_A01_NOTE_RUNS = (
    (False, '備註 :\n1、受理「補助案件」如跨越縣市/鄉鎮區土地，以第一筆縣市/鄉鎮區作為'),
    (True,  '補助案件數'),
    (False, '之統計基準。\n'),
    (True,  '計算公式：\n'),
    (False, '1、補助款執行率%=補助金額/核定金額。'),
)


# ── A07 規則建構常數（框線/欄寬/列高與 A02/A03 共用 _A0203_*/_XL_ROW_H_* 常數）──
_A07_NUM_FMT = {1: 'General', 2: 'General', 3: 'General', 4: 'General', 5: '#,##0'}
_A07_NOTE_TEXT = (
    '備註 :\n'
    '1、受理「補助案件」如跨越縣市/鄉鎮區土地，以第一筆縣市/鄉鎮區作為補助案件數之統計基準。'
)


# ── A09/A10 規則建構常數（事業區域內外推動成果統計，無範本依賴）────────────────

# 欄寬（當年度 16 欄 / 非當年度 7 欄，含 col 1 標籤欄）
_A0910_COL_WIDTHS = {
    16: {1: 27.0, **{i: 20.0 for i in range(2, 17)}},
    7:  {1: 27.0, **{i: 20.0 for i in range(2, 8)}},
}

# 表頭填充色
_A0910_FILL_BUDGETED  = PatternFill('solid', fgColor='E2EFDA')  # 已編列 淡綠
_A0910_FILL_COMPLETED = PatternFill('solid', fgColor='DDEBF7')  # 已結案 淡藍
_A0910_FILL_SUBTOTAL  = PatternFill('solid', fgColor='F2F2F2')  # 小計 淡灰

# 數字格式（每組 3 欄依序：案件數, 面積, 金額）
_A0910_NUM_FMT = ['General', '0.0000', '#,##0']

# 備註文字
_A0910_NOTE_TEXT = (
    '備註：\n'
    '1、事業區域歸屬依「任一土地」規則：補助案件所屬土地中任一筆 isIrrigationArea 為真，則整案歸入事業區域內，否則歸入事業區域外。\n'
    '2、「已結案」係指 status 為 completed 或 submitted 之案件；「已編列」係指排除 rejected/withdrawn/deleted 之所有有效案件。'
)
_A0910_ROW_H_NOTE = 60.0


# ── B03 規則建構常數（各縣市鄉鎮區各類補助項目統計表，19欄）────────────────────
# 欄寬（1-based，A=1 ~ S=19）
_B03_COL_WIDTHS = {
    1: 18.0,  # A 縣市
    2: 18.0,  # B 鄉鎮區
    3: 20.0,  # C 灌溉型式
    4: 14.0,  # D 補助面積(公頃)
    5: 12.0,  # E 補助案件數
    6: 16.0,  # F 農戶配合款(元)
    7: 16.0,  # G 田間管路設施(元)
    8: 16.0,  # H 調蓄設施(元)
    9: 16.0,  # I 動力設施(元)
    10: 16.0, # J 調控設備(元)
    11: 14.0, # K 設計費(元)
    12: 16.0, # L 總計(元)
    13: 16.0, # M 工程經費合計(元)
    14: 12.0, # N 噸
    15: 10.0,  # O 座
    16: 12.0, # P 抽水機(臺)
    17: 16.0, # Q 補助款(元)
    18: 12.0, # R 百分比%
    19: 16.0, # S 總工程費(元)
}
# 數值格式（1-based）
_B03_NUM_FMT = {
    1:  'General',    # 縣市
    2:  'General',    # 鄉鎮區
    3:  'General',    # 灌溉型式
    4:  '0.000',      # 補助面積(公頃)
    5:  '#,##0',      # 補助案件數
    6:  '#,##0',      # 農戶配合款(元)
    7:  '#,##0',      # 田間管路設施(元)
    8:  '#,##0',      # 調蓄設施(元)
    9:  '#,##0',      # 動力設施(元)
    10: '#,##0',      # 調控設備(元)
    11: '#,##0',      # 設計費(元)
    12: '#,##0',      # 補助總計(元)
    13: '#,##0',      # 工程經費合計(元)
    14: '#,##0',      # 噸
    15: '#,##0',      # 座
    16: '#,##0',      # 抽水機(臺)
    17: '#,##0',      # 補助款(元/公頃)
    18: '0.00%',      # 百分比%（值為 0-1 小數，openpyxl 自動 ×100 顯示）
    19: '#,##0',      # 總工程費(元/公頃)
}
# 備註文字
_B03_NOTE_TEXT = (
    '備註：\n'
    '1、受理「補助案件」如跨越縣市/鄉鎮區土地，以第一筆縣市/鄉鎮區作為補助案件數之統計基準。\n'
    '2、工程經費合計 = 農戶配合款 + 補助經費總計。\n'
    '3、*調蓄設施蓄水池欄位：噸的數量為蓄水池座數容量的總和。'
)


class ExcelGeneratorService:
    """Excel 文件生成服務 - 基於範本驅動架構生成 .xlsx 檔案"""

    # 範本結構常數定義
    TEMPLATE_HEADER_ROWS = 3      # 標題區塊：第1-3列
    TEMPLATE_DATA_START_ROW = 4   # 資料區塊起始：第4列
    TEMPLATE_DATA_END_ROW = 19    # 資料區塊結束：第19列
    TEMPLATE_PAGE_ROW = 20        # 頁數列：第20列
    TEMPLATE_DATA_ROWS_PER_PAGE = 16  # 每頁資料列數：16列 (4-19)
    TEMPLATE_TOTAL_ROWS_PER_PAGE = 20 # 每頁總列數：20列 (1-20)

    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "aerc_excel_downloads"
        self.temp_dir.mkdir(exist_ok=True)

    async def generate_photograph_carry_form(self, data: List[Dict[str, Any]], year: str, enable_pagination: bool = True) -> str:
        """
        生成外出拍攝照片攜帶表 Excel 檔案 - 完全基於範本驅動

        範本結構定義：
        - 第1-3列：標題區塊（包含機構名稱、年度、表單標題、欄位標題）
        - 第4-19列：資料區塊樣本（16列資料格式範本）
        - 第20列：頁數列樣本

        Args:
            data: 案件資料列表
            year: 申請年度
            enable_pagination: 分頁模式控制
                - True: 分頁模式 - 每頁顯示標題列和頁數，每頁16筆資料
                - False: 不分頁模式 - 只有第一頁標題列，連續顯示所有資料，無頁數

        Returns:
            str: 生成的 Excel 檔案路徑
        """
        # 使用環境配置取得範本檔案路徑 - 跨平台相容
        template_path = settings.get_template_path("photograph_carry_form_template.xlsx")

        if not template_path.exists():
            raise FileNotFoundError(f"範本檔案不存在: {template_path}\n環境: {settings.environment}\n根目錄: {settings.data_root}")

        # 載入範本檔案
        from openpyxl import load_workbook
        workbook = load_workbook(str(template_path))
        worksheet = workbook.active

        # 更新年度
        worksheet['F1'] = year

        # 使用範本驅動的資料填寫邏輯
        return await self._fill_template_data(workbook, worksheet, data, year, enable_pagination)

    async def _fill_template_data(self, workbook, worksheet, data: List[Dict[str, Any]], year: str,
                                  enable_pagination: bool = True) -> str:
        """
        基於範本結構填寫資料 - 範本驅動架構

        範本結構參考（20列為一個完整頁面結構）：
        - 列1-3：標題區塊（機構名稱、年度、表單標題、欄位標題）
        - 列4-19：資料區塊（16列資料格式）
        - 列20：頁數列

        Args:
            workbook: Excel工作簿
            worksheet: 工作表
            data: 資料列表
            year: 年度
            enable_pagination: 分頁模式控制
                - True: 分頁模式 - 每頁16筆資料，複製範本結構到新頁
                - False: 不分頁模式 - 連續填充資料，只保留第一頁標題
        """
        # 根據分頁模式調整邏輯
        if enable_pagination:
            # 分頁模式：每頁資料列數由範本定義
            data_per_page = self.TEMPLATE_DATA_ROWS_PER_PAGE
            total_pages = max(1, (len(data) + data_per_page - 1) // data_per_page)
        else:
            # 不分頁模式：所有資料連續放置
            data_per_page = len(data)
            total_pages = 1

        # 輸出關鍵統計資訊
        print(f"=== Excel 生成統計 ===")
        print(f"分頁模式: {'啟用' if enable_pagination else '停用'}")
        print(f"總資料筆數: {len(data)}")
        print(f"計算總頁數: {total_pages}")
        print(f"===================")

        # 分頁模式：為每頁建立完整的標題組結構
        if enable_pagination:
            # 為第2頁及之後的每一頁建立標題組
            for page_num in range(2, total_pages + 1):
                # 每頁總列數由範本定義
                page_start_row = (page_num - 1) * self.TEMPLATE_TOTAL_ROWS_PER_PAGE + 1

                # 1. 複製主標題列
                self._copy_row_with_format(worksheet, 1, page_start_row)

                # 2. 複製空白列
                worksheet.row_dimensions[page_start_row + 1].height = worksheet.row_dimensions[2].height
                for col in range(1, 12):  # A-K 欄
                    empty_cell = worksheet.cell(row=page_start_row + 1, column=col)
                    empty_cell.value = None
                    empty_cell.border = Border()

                # 3. 複製欄位標題列
                self._copy_row_with_format(worksheet, self.TEMPLATE_HEADER_ROWS, page_start_row + 2)
        else:
            # 不分頁模式：預先清除範本的頁數資訊（避免干擾資料顯示）
            template_page_cell = worksheet.cell(row=self.TEMPLATE_PAGE_ROW, column=11)
            template_page_cell.value = None

        # 依序填入所有資料
        for item_idx, item in enumerate(data):
            if enable_pagination:
                # 分頁模式：計算當前是第幾頁和該頁的第幾筆資料
                current_page = item_idx // data_per_page + 1
                data_index_in_page = item_idx % data_per_page

                # 計算當前資料應該放在哪一列（基於範本結構）
                page_start_row = (current_page - 1) * self.TEMPLATE_TOTAL_ROWS_PER_PAGE
                current_row = page_start_row + self.TEMPLATE_DATA_START_ROW + data_index_in_page

                # 資料定位已計算完成
            else:
                # 不分頁模式：所有資料連續放置，從範本資料起始列開始
                current_row = self.TEMPLATE_DATA_START_ROW + item_idx
                # 資料定位已計算完成

            # 複製資料列格式（從範本資料起始列複製）
            # 注意：第一筆資料直接使用範本起始列，其他資料需要複製格式
            if item_idx > 0:  # 第一筆資料不需複製格式
                self._copy_row_with_format(worksheet, self.TEMPLATE_DATA_START_ROW, current_row)

            # 處理資料
            land_data = item.get('land_data', {})
            total_area = 0
            if isinstance(land_data, dict) and 'land_locations' in land_data:
                for location in land_data['land_locations']:
                    if isinstance(location, dict) and 'area' in location:
                        try:
                            total_area += float(location['area'])
                        except (ValueError, TypeError):
                            continue

            facility_data = item.get('facility_data', {})
            facility_types = []
            if isinstance(facility_data, dict):
                if 'irrigation_type' in facility_data:
                    facility_types.append(str(facility_data['irrigation_type']))
                if 'facility_type' in facility_data:
                    facility_types.append(str(facility_data['facility_type']))
            facility_type_str = ', '.join(facility_types) if facility_types else '未設定'

            # 填寫資料
            row_data = [
                str(item.get('case_number', '')),
                str(item.get('applicant_name', '')),
                '',  # 鄉鎮
                '',  # 段名
                '',  # 地號
                f"{total_area:.4f}" if total_area > 0 else '',
                facility_type_str,
                '',  # 末端型式
                '',  # 農作物
                '',  # 電話
                str(item.get('address', ''))
            ]

            for col_idx, value in enumerate(row_data, start=1):
                cell = worksheet.cell(row=current_row, column=col_idx, value=value)
                # 設定自動換行
                if cell.alignment:
                    alignment = copy(cell.alignment)
                    alignment.wrap_text = True
                    cell.alignment = alignment
                else:
                    cell.alignment = Alignment(wrap_text=True)

        # 輸出資料填寫結果統計
        print(f"=== 資料填寫結果 ===")
        print(f"總計填寫: {len(data)} 筆資料")
        if enable_pagination:
            print(f"分為 {total_pages} 頁顯示")
        else:
            print("不分頁連續顯示")
        print(f"=====================")

        # 根據分頁模式設定頁碼
        if enable_pagination:
            # 分頁模式：在每頁的頁數列顯示頁碼
            for page_num in range(1, total_pages + 1):
                # 計算頁數列位置：基於範本結構
                page_row = page_num * self.TEMPLATE_TOTAL_ROWS_PER_PAGE

                # 設定頁碼
                page_cell = worksheet.cell(row=page_row, column=11)
                page_cell.value = f'第{page_num}頁，共{total_pages}頁'

                # 複製頁碼格式（從範本頁數列）
                template_page_cell = worksheet.cell(row=self.TEMPLATE_PAGE_ROW, column=11)
                if template_page_cell.font:
                    page_cell.font = copy(template_page_cell.font)
                if template_page_cell.alignment:
                    page_cell.alignment = copy(template_page_cell.alignment)

                # 設定頁數列格式
                worksheet.row_dimensions[page_row].height = 14.3

                # 處理頁數列的邊框
                for col in range(1, 12):  # A-K 欄
                    cell = worksheet.cell(row=page_row, column=col)
                    if col == 11:  # K欄（頁碼欄）
                        if page_num == 1:
                            # 第一頁：移除左、右、下邊框，只保留上邊框
                            cell.border = Border(top=Side(style='thin'))
                        else:
                            # 其他頁：保持原有邊框
                            pass
                    else:
                        # A-J欄：清空內容並移除所有邊框
                        cell.value = None
                        cell.border = Border()
            print(f"頁碼設定完成: {total_pages} 頁")

        # 生成檔案
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"photograph_carry_form_{year}_{timestamp}.xlsx"
        file_path = self.temp_dir / filename

        try:
            workbook.save(str(file_path))
            return str(file_path)
        except Exception as e:
            print(f"Excel save error: {e}")
            print(f"File path: {file_path}")
            raise

    def _copy_row_with_format(self, worksheet, source_row, target_row):
        """複製整列的內容和格式"""
        for col in range(1, 12):  # A-K 欄
            source_cell = worksheet.cell(row=source_row, column=col)
            target_cell = worksheet.cell(row=target_row, column=col)

            # 複製內容和格式
            target_cell.value = source_cell.value
            if source_cell.font:
                target_cell.font = copy(source_cell.font)
            if source_cell.alignment:
                target_cell.alignment = copy(source_cell.alignment)
            if source_cell.border:
                target_cell.border = copy(source_cell.border)
            if source_cell.fill:
                target_cell.fill = copy(source_cell.fill)

        # 複製行高
        worksheet.row_dimensions[target_row].height = worksheet.row_dimensions[source_row].height

        # 如果是第1列（標題列），需要處理合併儲存格
        if source_row == 1:
            # 合併 C、D、E 欄為單一儲存格（財團法人農業工程研究中心）
            merge_range = f'C{target_row}:E{target_row}'
            worksheet.merge_cells(merge_range)

            # 合併 G、H、I 欄為單一儲存格（年度施工照片拍攝攜帶表）
            merge_range = f'G{target_row}:I{target_row}'
            worksheet.merge_cells(merge_range)

    def _remove_top_border(self, worksheet, row_num):
        """移除指定列的上邊框"""
        for col in range(1, 12):  # A-K 欄
            cell = worksheet.cell(row=row_num, column=col)
            if cell.border:
                # 保持其他邊框，只移除上邊框
                new_border = Border(
                    left=cell.border.left,
                    right=cell.border.right,
                    top=None,  # 移除上邊框
                    bottom=cell.border.bottom
                )
                cell.border = new_border

    async def generate_a01_execution_progress_report(
        self,
        data: Dict[str, Any],
        year: int
    ) -> str:
        """
        生成 A01 各管理處執行進度報表 Excel 檔案（規則建構，無範本依賴）

        Args:
            data: ExecutionProgressResponse 資料（包含 offices 列表）
            year: 統計年度（民國年）

        Returns:
            str: 生成的 Excel 檔案路徑
        """
        COL_COUNT = 6
        DATA_START = 4

        workbook = Workbook()
        ws = workbook.active

        # 1. 欄寬
        for col, w in _A01_COL_WIDTHS.items():
            ws.column_dimensions[get_column_letter(col)].width = w

        # 2. Row 1 標題
        ws.row_dimensions[1].height = _XL_ROW_H_TITLE
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=COL_COUNT)
        c = ws.cell(1, 1)
        c.value = f"農業部農田水利署\n推廣管路灌溉設施計畫\n{year}年度各管理處執行進度"
        c.font = _XL_F16
        c.alignment = _XL_A_WRAP

        # 3. Row 2 表號 + 製表日期（E2:F2 合併）
        ws.row_dimensions[2].height = _XL_ROW_H_DATE
        c2 = ws.cell(2, 1)
        c2.value = 'A01'
        c2.font = _XL_F16B
        c2.alignment = _XL_A_CTR
        today = datetime.now()
        date_str = f"製表日期：{today.year - 1911}年{today.month:02d}月{today.day:02d}日"
        ws.merge_cells(start_row=2, start_column=5, end_row=2, end_column=COL_COUNT)
        dc = ws.cell(2, 5)
        dc.value = date_str
        dc.font = _XL_F12
        dc.alignment = _XL_A_RT

        # 4. Row 3 欄頭
        ws.row_dimensions[3].height = _XL_ROW_H_HDR2
        for j in range(COL_COUNT):
            cell = ws.cell(3, j + 1)
            cell.value = _A01_HDR_TEXT[j]
            cell.font = _XL_F14
            cell.alignment = _A01_HDR_ALIGN[j]
            cell.border = _A01_HDR_BORDER[j]

        # 5. 資料列
        offices = data.get('offices', [])
        for idx, office in enumerate(offices):
            row = DATA_START + idx
            ws.row_dimensions[row].height = _XL_ROW_H_DATA
            row_values = [
                office.get('office_name', ''),
                office.get('approved_budget', 0) or 0,
                office.get('completed_cases', 0) or 0,
                float(office.get('total_area', 0) or 0),
                office.get('total_subsidy', 0) or 0,
                float(office.get('execution_rate', 0) or 0),
            ]
            for ci, val in enumerate(row_values):
                cell = ws.cell(row, ci + 1)
                cell.value = val
                cell.font = _XL_F14
                cell.alignment = _XL_A_CTR
                cell.border = _A01_DATA_BORDER[ci]
                cell.number_format = _A01_NUM_FMT[ci + 1]

        # 6. 最末列外框底線（medium bottom）
        if offices:
            last_row = DATA_START + len(offices) - 1
            for ci in range(COL_COUNT):
                cell = ws.cell(last_row, ci + 1)
                db = _A01_DATA_BORDER[ci]
                cell.border = Border(left=db.left, right=db.right, bottom=_XL_S_M)

        # 7. 備註列（資料末列後空一行）
        note_row = DATA_START + len(offices) + 1
        ws.merge_cells(start_row=note_row, start_column=1, end_row=note_row, end_column=COL_COUNT)
        note_c = ws.cell(note_row, 1)
        note_c.value = _A01_NOTE_TEXT
        note_c.font = _XL_F14
        note_c.alignment = _XL_A_NOTE
        ws.row_dimensions[note_row].height = _XL_ROW_H_NOTE

        # 8. 儲存後注入備註底線 Rich Text
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = self.temp_dir / f"A01_execution_progress_{year}_{timestamp}.xlsx"
        workbook.save(str(file_path))
        self._inject_note_rich_text(str(file_path), note_row, _A01_NOTE_RUNS)
        return str(file_path)

    # ==================== A02 系列統計報表 ====================

    def _set_cell_value_safe(self, worksheet, cell_ref: str, value):
        """
        安全地設定單元格值（處理合併單元格）

        如果目標單元格是合併單元格的一部分，會自動使用合併區域的左上角單元格
        """
        from openpyxl.utils import coordinate_to_tuple

        row, col = coordinate_to_tuple(cell_ref)

        # 檢查是否在合併單元格中
        for merge_range in worksheet.merged_cells.ranges:
            if (merge_range.min_row <= row <= merge_range.max_row and
                merge_range.min_col <= col <= merge_range.max_col):
                # 使用合併區域的左上角單元格
                worksheet.cell(row=merge_range.min_row, column=merge_range.min_col).value = value
                return

        # 不在合併單元格中，直接賦值
        worksheet[cell_ref] = value

    def _set_cell_value_safe_by_position(self, worksheet, row: int, col: int, value):
        """
        安全地設定單元格值（使用行列位置，處理合併單元格）

        Args:
            worksheet: Excel worksheet
            row: 行號（1-based）
            col: 列號（1-based）
            value: 要設定的值
        """
        from openpyxl.cell.cell import MergedCell

        cell = worksheet.cell(row=row, column=col)

        # 如果是合併單元格，找到合併區域的左上角單元格
        if isinstance(cell, MergedCell):
            for merge_range in worksheet.merged_cells.ranges:
                if (merge_range.min_row <= row <= merge_range.max_row and
                    merge_range.min_col <= col <= merge_range.max_col):
                    worksheet.cell(row=merge_range.min_row, column=merge_range.min_col).value = value
                    return
        else:
            # 不是合併單元格，直接設定
            cell.value = value

    # ── openpyxl 工具組 ──────────────────────────────────────────────────────
    # 以下兩個靜態方法封裝了 openpyxl 合併格的固有行為限制，
    # 供所有動態報表方法複用。

    @staticmethod
    def _tpl_merge_horizontal(
        ws,
        row: int,
        col_start: int,
        col_count: int,
        borders: list,
    ) -> None:
        """
        橫向合併儲存格並保留各欄邊框。

        必要性：openpyxl 的 merge_cells 會保留合併範圍各欄的 border 資料並寫入 XML，
        但若在合併之後才設定邊框，右邊界欄的右外框可能遺失。
        正確做法：先對每欄設定邊框，再執行合併，Excel 即可正確顯示四邊完整框線。

        Args:
            ws: 工作表
            row: 列號
            col_start: 合併起始欄索引
            col_count: 合併欄數
            borders: 長度為 col_count 的邊框列表（對應每欄的邊框）
        """
        for j in range(col_count):
            ws.cell(row, col_start + j).border = borders[j]
        ws.merge_cells(
            start_row=row, start_column=col_start,
            end_row=row, end_column=col_start + col_count - 1,
        )

    @staticmethod
    def _tpl_force_interior_border(ws, row: int, col: int, border) -> None:
        """
        強制注入邊框到垂直合併格的底端格。

        必要性：openpyxl 的 merge_cells 會從 ws._cells 中刪除非左上角格（底端格），
        導致對底端格設定的邊框在合併後消失。
        Excel 讀取垂直合併格時，底端格若無明確 XML 樣式，該格行高區域的左/下框線不顯示。
        本方法在合併之後建立新的 Cell 物件並直接注入 ws._cells，繞過此限制。

        使用時機：固定欄（縱向合併 HDR1:HDR2）的底端列邊框設定，須在 merge_cells 之後呼叫。

        Args:
            ws: 工作表
            row: 底端格的列號
            col: 底端格的欄號
            border: 要注入的 Border 物件
        """
        from openpyxl.cell.cell import Cell as _OxlCell
        interior = _OxlCell(worksheet=ws, row=row, column=col)
        interior.border = border
        ws._cells[(row, col)] = interior

    def _generate_a02_report(
        self,
        template_name: str,
        col_count: int,
        title_text: str,
        date_text: str,
        rows: List[List[Any]],
        filename_prefix: str,
    ) -> str:
        """
        A02-1/A02-2 報表通用生成邏輯（規則建構，無範本依賴）

        生成結構：
          Row 1: 標題（合併全欄，wrap_text）
          Row 2: 表號 + 製表日期（最後兩欄合併）
          Row 3 (HDR): 各欄頭（單列，高度 45）
          Row 4+: 資料列
          備註列: 純文字備註（合併全欄，與最末列間隔一空列）
        """
        from openpyxl import Workbook
        from openpyxl.styles import Border
        from openpyxl.utils import get_column_letter

        HDR        = 3
        DATA_START = 4
        tbl_num    = template_name.replace('.xlsx', '')

        workbook = Workbook()
        ws       = workbook.active

        # ── 1. 欄寬 ──────────────────────────────────────────────────────
        for i, w in _A0203_COL_WIDTHS[col_count].items():
            ws.column_dimensions[get_column_letter(i + 1)].width = w

        # ── 2. Row 1 標題 ────────────────────────────────────────────────
        ws.row_dimensions[1].height = _XL_ROW_H_TITLE
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=col_count)
        c           = ws.cell(1, 1)
        c.value     = title_text
        c.font      = _XL_F16
        c.alignment = _XL_A_WRAP

        # ── 3. Row 2 表號 + 製表日期 ─────────────────────────────────────
        ws.row_dimensions[2].height = _XL_ROW_H_DATE
        c2           = ws.cell(2, 1)
        c2.value     = tbl_num
        c2.font      = _XL_F16B
        c2.alignment = _XL_A_CTR
        ws.merge_cells(start_row=2, start_column=col_count - 1, end_row=2, end_column=col_count)
        dc           = ws.cell(2, col_count - 1)
        dc.value     = date_text
        dc.font      = _XL_F12
        dc.alignment = _XL_A_RT

        # ── 4. Row 3 (HDR) 欄頭 ──────────────────────────────────────────
        ws.row_dimensions[HDR].height = _XL_ROW_H_HDR2  # 45.0
        hdr_texts  = _A0203_HDR_TEXT[col_count]
        hdr_aligns = _A0203_HDR_ALIGN[col_count]
        for j in range(col_count):
            cell           = ws.cell(HDR, j + 1)
            cell.value     = hdr_texts[j]
            cell.font      = _XL_F14
            cell.alignment = hdr_aligns[j]
            cell.border    = _A0203_HDR_BORDER[(col_count, j)]

        # ── 5. 資料列 ─────────────────────────────────────────────────────
        for idx, row_values in enumerate(rows):
            row_num                           = DATA_START + idx
            ws.row_dimensions[row_num].height = _XL_ROW_H_DATA
            for ci, val in enumerate(row_values):
                cell           = ws.cell(row_num, ci + 1)
                cell.value     = val
                cell.font      = _XL_F14
                cell.alignment = _XL_A_CTR
                cell.border    = _A0203_DATA_BORDER[(col_count, ci)]

        # ── 6. 最末列套用外框底線（medium bottom）────────────────────────
        if rows:
            last_row = DATA_START + len(rows) - 1
            for col in range(1, col_count + 1):
                cell = ws.cell(last_row, col)
                b = cell.border
                cell.border = Border(
                    left   = b.left   if b else None,
                    right  = b.right  if b else None,
                    top    = b.top    if b else None,
                    bottom = _XL_S_M,
                )

        # ── 7. 備註列（與最末列間隔一空列，與舊版行為一致）──────────────
        note_row        = DATA_START + len(rows) + 1
        last_col_letter = get_column_letter(col_count)
        ws.merge_cells(f"A{note_row}:{last_col_letter}{note_row}")
        note_c            = ws.cell(note_row, 1)
        note_c.value      = _A0405_NOTE_TEXT
        note_c.font       = _XL_F14
        note_c.alignment  = _XL_A_NOTE
        ws.row_dimensions[note_row].height = _XL_ROW_H_NOTE

        # ── 8. 儲存 ─────────────────────────────────────────────────────
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename  = f"{filename_prefix}_{timestamp}.xlsx"
        file_path = self.temp_dir / filename
        workbook.save(str(file_path))
        return str(file_path)

    async def generate_a02_1_report(self, data: Dict[str, Any], year: int) -> str:
        """生成 A02-1 各縣市鄉鎮區統計報表"""
        today = datetime.now()
        rows = []
        for s in data.get('stats', []):
            rows.append([
                s.get('county_name', ''),
                s.get('town_name', ''),
                s.get('completed_cases', 0) or 0,
                float(s.get('total_area', 0) or 0),
                s.get('total_subsidy', 0) or 0,
            ])
        return self._generate_a02_report(
            template_name="A02.xlsx",
            col_count=5,
            title_text=f"農業部農田水利署\n推廣管路灌溉設施計畫\n{year}年度各縣市鄉鎮區統計",
            date_text=f"製表日期：{today.year - 1911}年{today.month:02d}月{today.day:02d}日",
            rows=rows,
            filename_prefix=f"A02_{year}",
        )

    async def generate_a02_2_report(self, data: Dict[str, Any], year: int) -> str:
        """生成 A02-2 各管理處統計報表"""
        today = datetime.now()
        rows = []
        for s in data.get('stats', []):
            rows.append([
                s.get('office_name', ''),
                s.get('completed_cases', 0) or 0,
                float(s.get('total_area', 0) or 0),
                s.get('total_subsidy', 0) or 0,
            ])
        return self._generate_a02_report(
            template_name="A03.xlsx",
            col_count=4,
            title_text=f"農業部農田水利署\n推廣管路灌溉設施計畫\n{year}年度各管理處統計",
            date_text=f"製表日期：{today.year - 1911}年{today.month:02d}月{today.day:02d}日",
            rows=rows,
            filename_prefix=f"A03_{year}",
        )

    async def generate_a02_3_report(self, data: Dict[str, Any]) -> str:
        """生成 A02-3 歷年各縣市鄉鎮區統計報表（範本驅動橫向年度展開）"""
        return self._generate_a02_yearly_report(
            template_name="A04.xlsx",
            fixed_cols=2,
            data=data,
            filename_prefix=f"A04_{data.get('start_year', '')}-{data.get('end_year', '')}",
            show_total=False,
        )

    async def generate_a02_4_report(self, data: Dict[str, Any]) -> str:
        """生成 A02-4 歷年各管理處統計報表（範本驅動橫向年度展開）"""
        return self._generate_a02_yearly_report(
            template_name="A05.xlsx",
            fixed_cols=1,
            data=data,
            filename_prefix=f"A05_{data.get('start_year', '')}-{data.get('end_year', '')}",
            show_total=False,
        )

    async def generate_a08_aboriginal_yearly_report(self, data: Dict[str, Any]) -> str:
        """生成 A08 歷年原民區域統計報表（橫向年度展開，與 A04 結構相同）"""
        return self._generate_a02_yearly_report(
            template_name="A08.xlsx",
            fixed_cols=2,
            data=data,
            filename_prefix=f"A08_{data.get('start_year', '')}-{data.get('end_year', '')}",
            show_total=False,
        )

    def _generate_a02_yearly_report(
        self,
        template_name: str,
        fixed_cols: int,
        data: Dict[str, Any],
        filename_prefix: str,
        show_total: bool = True,
    ) -> str:
        """
        A02-3/A02-4 橫向年度展開報表生成（規則建構，無範本依賴）

        生成結構：
          Row 1: 標題（合併 A1:固定欄+3，wrap_text）
          Row 2: 表號 + 製表日期（最後兩欄合併）
          Row 3 (HDR1): 固定欄頭（合併 row3:4）+ N 年度合併欄頭
          Row 4 (HDR2): 指標子欄頭（補助案件數 / 補助面積 / 補助金額）× N
          Row 5+: 資料列（固定識別欄 + N×3 年度指標欄）
          合計列: 合計（show_total=True）
          備註列: 純文字備註（合併全欄）
        """
        from openpyxl import Workbook
        from openpyxl.styles import Border
        from openpyxl.utils import get_column_letter
        from openpyxl.cell.cell import MergedCell
        from decimal import Decimal as _Decimal

        years        = data.get('years', [])
        rows_data    = data.get('rows', [])
        start_year   = data.get('start_year', 0)
        end_year_val = data.get('end_year', 0)
        N            = len(years)
        total_cols   = fixed_cols + N * 3
        # Row 1/2 合併範圍（固定欄 + 1 個年度組），與舊範本版本保持一致
        TPL_TOTAL_COLS = fixed_cols + 3
        HDR1       = 3
        HDR2       = 4
        DATA_START = 5

        # 從 template_name 衍生表號與固定欄頭（無須載入範本檔案）
        tbl_num = template_name.replace('.xlsx', '')
        _FIXED_HDR_NAMES = {2: ['縣市', '鄉鎮區'], 1: ['管理處']}
        _TITLE_TMPLS = {
            'A04.xlsx': '農業部農田水利署\n推廣管路灌溉設施計畫\nOOO年度～OOO年度各縣市鄉鎮區統計表',
            'A05.xlsx': '農業部農田水利署\n推廣管路灌溉設施計畫\nOOO年度～OOO年度各管理處統計表',
            'A08.xlsx': '農業部農田水利署\n推廣管路灌溉設施計畫\nOOO年度～OOO年度原住民地區推動成果統計表',
        }
        title_text      = _TITLE_TMPLS.get(template_name, '').replace(
            'OOO年度～OOO年度', f'{start_year}年度～{end_year_val}年度'
        )
        fixed_hdr_names = _FIXED_HDR_NAMES[fixed_cols]

        workbook = Workbook()
        ws       = workbook.active

        # ── 1. 欄寬 ──────────────────────────────────────────────────────
        cw = _A0405_COL_WIDTHS[fixed_cols]
        for i in range(fixed_cols):
            ws.column_dimensions[get_column_letter(i + 1)].width = cw[i]
        for i in range(N):
            for j in range(3):
                ws.column_dimensions[get_column_letter(fixed_cols + i * 3 + j + 1)].width = cw['year']

        # ── 2. Row 1 標題 ────────────────────────────────────────────────
        ws.row_dimensions[1].height = _XL_ROW_H_TITLE
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=TPL_TOTAL_COLS)
        c           = ws.cell(1, 1)
        c.value     = title_text
        c.font      = _XL_F16
        c.alignment = _XL_A_WRAP

        # ── 3. Row 2 表號 + 製表日期 ─────────────────────────────────────
        ws.row_dimensions[2].height = _XL_ROW_H_DATE
        c2           = ws.cell(2, 1)
        c2.value     = tbl_num
        c2.font      = _XL_F16B
        c2.alignment = _XL_A_CTR

        today          = datetime.now()
        date_txt       = f"製表日期：{today.year - 1911}年{today.month:02d}月{today.day:02d}日"
        date_start_col = TPL_TOTAL_COLS - 1
        ws.merge_cells(start_row=2, start_column=date_start_col, end_row=2, end_column=TPL_TOTAL_COLS)
        dc           = ws.cell(2, date_start_col)
        dc.value     = date_txt
        dc.font      = _XL_F12
        dc.alignment = _XL_A_RT

        # ── 4. HDR1 (Row 3) 固定欄頭（合併 row3:4）──────────────────────
        ws.row_dimensions[HDR1].height = _XL_ROW_H_HDR1
        for i in range(fixed_cols):
            col  = i + 1
            ws.merge_cells(start_row=HDR1, start_column=col, end_row=HDR2, end_column=col)
            cell           = ws.cell(HDR1, col)
            cell.value     = fixed_hdr_names[i]
            cell.font      = _XL_F16
            cell.alignment = _XL_A_CTR
            cell.border    = _A0405_FIXED_HDR_BORDER[(fixed_cols, i)]
            # merge_cells 刪除底端格；強制注入邊框確保 HDR2 行高區域的框線顯示
            self._tpl_force_interior_border(ws, HDR2, col, _A0405_FIXED_HDR2_BORDER[(fixed_cols, i)])

        # ── 5. HDR1 (Row 3) 年度合併欄頭 ────────────────────────────────
        for i, year in enumerate(years):
            sc             = fixed_cols + i * 3 + 1
            self._tpl_merge_horizontal(ws, HDR1, sc, 3, _A0405_YEAR_HDR_BORDERS)
            cell           = ws.cell(HDR1, sc)
            cell.value     = f"{year}年度"
            cell.font      = _XL_F16
            cell.alignment = _XL_A_CTR

        # ── 6. HDR2 (Row 4) 指標子欄頭 ──────────────────────────────────
        ws.row_dimensions[HDR2].height = _XL_ROW_H_HDR2
        _subhdr_align = [_XL_A_WRAP, _XL_A_CTR, _XL_A_CTR]
        for i in range(N):
            for j in range(3):
                col            = fixed_cols + i * 3 + j + 1
                cell           = ws.cell(HDR2, col)
                cell.value     = _A0405_SUBHDR_TEXT[j]
                cell.font      = _XL_F14
                cell.alignment = _subhdr_align[j]
                cell.border    = _A0405_SUBHDR_BORDER[j]

        # ── 7. 資料列 ─────────────────────────────────────────────────────
        year_totals = {y: {'cases': 0, 'area': _Decimal('0'), 'subsidy': 0} for y in years}

        for idx, row_item in enumerate(rows_data):
            row_num                           = DATA_START + idx
            ws.row_dimensions[row_num].height = _XL_ROW_H_DATA

            fixed_vals = (
                [row_item.get('county_name', ''), row_item.get('town_name', '')]
                if fixed_cols == 2 else
                [row_item.get('office_name', '')]
            )
            for ci, val in enumerate(fixed_vals):
                cell           = ws.cell(row_num, ci + 1)
                cell.value     = val
                cell.font      = _XL_F14
                cell.alignment = _XL_A_CTR
                cell.border    = _A0405_FIXED_DATA_BORDER[(fixed_cols, ci)]

            for i, ym in enumerate(row_item.get('year_metrics', [])):
                y       = ym.get('year', 0)
                cases   = int(ym.get('completed_cases', 0) or 0)
                area    = float(ym.get('total_area', 0) or 0)
                subsidy = int(ym.get('total_subsidy', 0) or 0)
                sc      = fixed_cols + i * 3 + 1
                for j, val in enumerate([cases, area, subsidy]):
                    cell           = ws.cell(row_num, sc + j)
                    cell.value     = val
                    cell.font      = _XL_F14
                    cell.alignment = _XL_A_CTR
                    cell.border    = _A0405_DATA_YEAR_BORDER[j]
                if y in year_totals:
                    year_totals[y]['cases']   += cases
                    year_totals[y]['area']    += _Decimal(str(area))
                    year_totals[y]['subsidy'] += subsidy

        # ── 8. 合計列（僅 show_total=True 時生成）────────────────────────
        if show_total:
            total_row                           = DATA_START + len(rows_data)
            ws.row_dimensions[total_row].height = _XL_ROW_H_TOTAL
            # 先設邊框再合併，確保右邊界外框不遺失
            for i in range(fixed_cols):
                c           = ws.cell(total_row, i + 1)
                c.font      = _XL_F14
                c.alignment = _XL_A_CTR
                c.border    = _A0405_FIXED_DATA_BORDER[(fixed_cols, i)]
            if fixed_cols == 2:
                ws.merge_cells(start_row=total_row, start_column=1, end_row=total_row, end_column=2)
            ws.cell(total_row, 1).value = '合  計'
            for i, year in enumerate(years):
                sc  = fixed_cols + i * 3 + 1
                yt  = year_totals[year]
                for j, val in enumerate([yt['cases'], float(yt['area']), yt['subsidy']]):
                    cell           = ws.cell(total_row, sc + j)
                    cell.value     = val
                    cell.font      = _XL_F14
                    cell.alignment = _XL_A_CTR
                    cell.border    = _A0405_DATA_YEAR_BORDER[j]
            note_start_row = total_row + 1
        else:
            note_start_row = DATA_START + len(rows_data)

        # ── 9. 最末列套用外框底線（medium bottom）────────────────────────
        last_table_row = total_row if show_total else DATA_START + len(rows_data) - 1
        if rows_data:
            for col in range(1, total_cols + 1):
                cell = ws.cell(last_table_row, col)
                if isinstance(cell, MergedCell):
                    continue
                b = cell.border
                cell.border = Border(
                    left   = b.left   if b else None,
                    right  = b.right  if b else None,
                    top    = b.top    if b else None,
                    bottom = _XL_S_M,
                )

        # ── 10. 備註列 ───────────────────────────────────────────────────
        note_row        = note_start_row
        last_col_letter = get_column_letter(total_cols)
        ws.merge_cells(f"A{note_row}:{last_col_letter}{note_row}")
        note_c            = ws.cell(note_row, 1)
        note_c.value      = _A0405_NOTE_TEXT
        note_c.font       = _XL_F14
        note_c.alignment  = _XL_A_NOTE
        ws.row_dimensions[note_row].height = _XL_ROW_H_NOTE

        # ── 11. 儲存 ─────────────────────────────────────────────────────
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename  = f"{filename_prefix}_{timestamp}.xlsx"
        file_path = self.temp_dir / filename
        workbook.save(str(file_path))
        return str(file_path)

    # ==================== A03 管理處經費統計報表 ====================

    async def generate_a03_budget_analysis_report(
        self,
        data: Dict[str, Any],
        year: int
    ) -> str:
        """
        生成 A03 各管理處經費統計報表 Excel 檔案（規則建構，無範本依賴）

        Args:
            data: BudgetAnalysisResponse 資料（包含 offices、total_* 等欄位）
            year: 統計年度（民國年）

        Returns:
            str: 生成的 Excel 檔案路徑
        """
        DATA_START = 4
        COL_COUNT = 12

        workbook = Workbook()
        ws = workbook.active

        # 1. 欄寬
        for col, w in _A06_COL_WIDTHS.items():
            ws.column_dimensions[get_column_letter(col)].width = w

        # 2. Row 1 標題
        ws.row_dimensions[1].height = _XL_ROW_H_TITLE
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=COL_COUNT)
        c = ws.cell(1, 1)
        c.value = f"農業部農田水利署\n推廣管路灌溉設施計畫\n{year}年度各管理處經費統計表"
        c.font = _XL_F16
        c.alignment = _XL_A_WRAP

        # 3. Row 2 表號 + 製表日期（K2:L2 合併）
        ws.row_dimensions[2].height = _XL_ROW_H_DATE
        c2 = ws.cell(2, 1)
        c2.value = 'A06'
        c2.font = _XL_F16B
        c2.alignment = _XL_A_CTR
        today = datetime.now()
        date_str = f"製表日期：{today.year - 1911}年{today.month:02d}月{today.day:02d}日"
        ws.merge_cells(start_row=2, start_column=11, end_row=2, end_column=COL_COUNT)
        dc = ws.cell(2, 11)
        dc.value = date_str
        dc.font = _XL_F12
        dc.alignment = _XL_A_RT

        # 4. Row 3 欄頭
        ws.row_dimensions[3].height = _XL_ROW_H_HDR2
        for j in range(COL_COUNT):
            cell = ws.cell(3, j + 1)
            cell.value = _A06_HDR_TEXT[j]
            cell.font = _XL_F14
            cell.alignment = _XL_A_CTR
            cell.border = _A06_HDR_BORDER[j]

        # 5. 資料列
        offices = data.get('offices', [])
        for idx, office in enumerate(offices):
            row = DATA_START + idx
            ws.row_dimensions[row].height = _XL_ROW_H_DATA
            row_values = [
                office.get('office_name', ''),
                float(office.get('planned_area', 0) or 0),
                office.get('planned_budget', 0) or 0,
                office.get('budgeted_cases', 0) or 0,
                float(office.get('budgeted_area', 0) or 0),
                office.get('budgeted_subsidy', 0) or 0,
                office.get('unbudgeted_subsidy', 0) or 0,
                office.get('verified_cases', 0) or 0,
                float(office.get('verified_area', 0) or 0),
                office.get('verified_amount', 0) or 0,
                float(office.get('area_execution_rate', 0) or 0),
                float(office.get('budget_execution_rate', 0) or 0),
            ]
            for ci, val in enumerate(row_values):
                cell = ws.cell(row, ci + 1)
                cell.value = val
                cell.font = _XL_F14
                cell.alignment = _XL_A_CTR
                cell.border = _A06_DATA_BORDER[ci]
                cell.number_format = _A06_NUM_FMT[ci + 1]

        # 6. 最末列外框底線（medium bottom）
        if offices:
            last_row = DATA_START + len(offices) - 1
            for ci in range(COL_COUNT):
                cell = ws.cell(last_row, ci + 1)
                db = _A06_DATA_BORDER[ci]
                cell.border = Border(left=db.left, right=db.right, bottom=_XL_S_M)

        # 7. 備註列（資料末列後空一行；平文字先寫，儲存後再注入 Rich Text）
        note_row = DATA_START + len(offices) + 1
        ws.merge_cells(start_row=note_row, start_column=1, end_row=note_row, end_column=COL_COUNT)
        note_c = ws.cell(note_row, 1)
        note_c.value = _A06_NOTE_TEXT
        note_c.font = _XL_F14
        note_c.alignment = _XL_A_NOTE
        ws.row_dimensions[note_row].height = _A06_ROW_H_NOTE

        # 8. 儲存後注入備註底線 Rich Text
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = self.temp_dir / f"A06_budget_analysis_{year}_{timestamp}.xlsx"
        workbook.save(str(file_path))
        self._inject_note_rich_text(str(file_path), note_row, _A06_NOTE_RUNS)
        return str(file_path)

    @staticmethod
    @staticmethod
    def _inject_note_rich_text(file_path: str, note_row: int, runs: tuple) -> None:
        """
        ZIP 後處理：將備註列的平文字替換為帶底線的 Rich Text（通用）。

        openpyxl 3.1.2 在無 lxml 環境下無法正確寫出 CellRichText，因此先以純文字
        儲存，再直接操作 xlsx ZIP 內的 sheet XML，將 <is><t>...</t></is> 替換成
        帶 <u/> run 的多段格式。

        Args:
            file_path: xlsx 路徑（原址覆蓋）
            note_row:  備註列列號
            runs:      tuple of (underline: bool, text: str)；
                       xml:space="preserve" 依 text 內容自動套用
        """
        import zipfile
        import re
        import os

        _RPR_NORMAL = '<rPr><sz val="14"/><rFont val="微軟正黑體"/></rPr>'
        _RPR_ULINE  = '<rPr><u/><sz val="14"/><rFont val="微軟正黑體"/></rPr>'

        def _run_xml(underline: bool, text: str) -> str:
            rpr = _RPR_ULINE if underline else _RPR_NORMAL
            preserve = '\n' in text or text != text.strip()
            sp = ' xml:space="preserve"' if preserve else ''
            esc = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            return f'<r>{rpr}<t{sp}>{esc}</t></r>'

        rich_is = '<is>' + ''.join(_run_xml(*r) for r in runs) + '</is>'

        with zipfile.ZipFile(file_path, 'r') as zin:
            names = zin.namelist()
            sheet_name = next(n for n in names if n.startswith('xl/worksheets/sheet') and n.endswith('.xml'))
            data = {name: zin.read(name) for name in names}

        sheet_str = data[sheet_name].decode('utf-8')
        pattern = (
            r'(<c\s[^>]*\br="A' + str(note_row) + r'"[^>]*\bt="inlineStr"[^>]*>)'
            r'<is>.*?</is>'
            r'(</c>)'
        )
        new_str, count = re.subn(pattern, r'\1' + rich_is + r'\2', sheet_str, flags=re.DOTALL)
        if count == 0:
            return  # 空資料列情境，找不到備註格，直接略過

        data[sheet_name] = new_str.encode('utf-8')

        tmp_path = file_path + '.tmp'
        with zipfile.ZipFile(tmp_path, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
            for name in names:
                zout.writestr(name, data[name])
        os.replace(tmp_path, file_path)

    # ==================== A04 原民區域統計報表 ====================

    async def generate_a04_aboriginal_report(
        self,
        data: Dict[str, Any],
        year: int
    ) -> str:
        """
        生成 A04 原民區域統計報表 Excel 檔案（規則建構，無範本依賴）

        Args:
            data: 原民區域統計資料（包含 stats 列表）
            year: 統計年度（民國年）

        Returns:
            str: 生成的 Excel 檔案路徑
        """
        COL_COUNT = 5
        DATA_START = 4

        workbook = Workbook()
        ws = workbook.active

        # 1. 欄寬（與 A02-1 相同：全部 24.33）
        for ci, w in _A0203_COL_WIDTHS[COL_COUNT].items():
            ws.column_dimensions[get_column_letter(ci + 1)].width = w

        # 2. Row 1 標題
        ws.row_dimensions[1].height = _XL_ROW_H_TITLE
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=COL_COUNT)
        c = ws.cell(1, 1)
        c.value = f"農業部農田水利署\n推廣管路灌溉設施計畫\n{year}年度原住民地區推動成果統計表"
        c.font = _XL_F16
        c.alignment = _XL_A_WRAP

        # 3. Row 2 表號 + 製表日期（D2:E2 合併）
        ws.row_dimensions[2].height = _XL_ROW_H_DATE
        c2 = ws.cell(2, 1)
        c2.value = 'A07'
        c2.font = _XL_F16B
        c2.alignment = _XL_A_CTR
        today = datetime.now()
        date_str = f"製表日期：{today.year - 1911}年{today.month:02d}月{today.day:02d}日"
        ws.merge_cells(start_row=2, start_column=4, end_row=2, end_column=COL_COUNT)
        dc = ws.cell(2, 4)
        dc.value = date_str
        dc.font = _XL_F12
        dc.alignment = _XL_A_RT

        # 4. Row 3 欄頭（與 A02-1 相同）
        ws.row_dimensions[3].height = _XL_ROW_H_HDR2
        for j in range(COL_COUNT):
            cell = ws.cell(3, j + 1)
            cell.value = _A0203_HDR_TEXT[COL_COUNT][j]
            cell.font = _XL_F14
            cell.alignment = _A0203_HDR_ALIGN[COL_COUNT][j]
            cell.border = _A0203_HDR_BORDER[(COL_COUNT, j)]

        # 5. 資料列
        stats = data.get('stats', [])
        for idx, stat in enumerate(stats):
            row = DATA_START + idx
            ws.row_dimensions[row].height = _XL_ROW_H_DATA
            row_values = [
                stat.get('county') or None,
                stat.get('town') or None,
                stat['grant_count'] if stat.get('grant_count') else None,
                stat['subsidy_area'] if stat.get('subsidy_area') else None,
                stat['subsidy_amount'] if stat.get('subsidy_amount') else None,
            ]
            for ci, val in enumerate(row_values):
                cell = ws.cell(row, ci + 1)
                cell.value = val
                cell.font = _XL_F14
                cell.alignment = _XL_A_CTR
                cell.border = _A0203_DATA_BORDER[(COL_COUNT, ci)]
                cell.number_format = _A07_NUM_FMT[ci + 1]

        # 6. 最末列外框底線（medium bottom）
        if stats:
            last_row = DATA_START + len(stats) - 1
            for ci in range(COL_COUNT):
                cell = ws.cell(last_row, ci + 1)
                db = _A0203_DATA_BORDER[(COL_COUNT, ci)]
                cell.border = Border(left=db.left, right=db.right, bottom=_XL_S_M)

        # 7. 備註列（資料末列後空一行）
        note_row = DATA_START + len(stats) + 1
        ws.merge_cells(start_row=note_row, start_column=1, end_row=note_row, end_column=COL_COUNT)
        note_c = ws.cell(note_row, 1)
        note_c.value = _A07_NOTE_TEXT
        note_c.font = _XL_F14
        note_c.alignment = _XL_A_NOTE
        ws.row_dimensions[note_row].height = _XL_ROW_H_NOTE

        # 8. 儲存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = self.temp_dir / f"A07_aboriginal_{year}_{timestamp}.xlsx"
        workbook.save(str(file_path))
        return str(file_path)

    # ==================== B01 系列推動成果統計報表（管理區內外分組） ====================

    def _generate_a09_a10_report(
        self,
        table_code: str,
        label_col_name: str,
        year: int,
        is_current_year: bool,
        rows: List[List[Any]],
    ) -> str:
        """
        A09/A10 通用報表生成引擎（規則建構，無範本依賴）

        生成結構：
          Row 1: 標題（合併全欄，wrap_text）
          Row 2: 表號 + 製表日期
          Row 3 (HDR1): label 欄垂直合併 rows 3-5；主分組（已編列/已結案/小計）
          Row 4 (HDR2): 事業區域外/事業區域內 子分組
          Row 5 (HDR3): 案件數/面積(公頃)/金額(元) 指標欄
          Row 6+: 資料列
          備註列: 純文字備註（合併全欄）

        Args:
            table_code: 'A09' 或 'A10'
            label_col_name: 標籤欄名稱（'縣 市' 或 '管理處'）
            year: 統計年度（民國年）
            is_current_year: 當年度（16欄）或非當年度（7欄）
            rows: 資料列，每列含 col_count 個值（含 label）

        Returns:
            str: 生成的 Excel 檔案路徑
        """
        from openpyxl.cell.cell import MergedCell
        from datetime import timezone

        col_count  = 16 if is_current_year else 7
        DATA_START = 6
        last_col_letter = get_column_letter(col_count)

        workbook = Workbook()
        ws = workbook.active

        # ── 1. 欄寬 ──────────────────────────────────────────────────────
        for col, w in _A0910_COL_WIDTHS[col_count].items():
            ws.column_dimensions[get_column_letter(col)].width = w

        # ── 2. Row 1 標題 ────────────────────────────────────────────────
        ws.row_dimensions[1].height = _XL_ROW_H_TITLE
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=col_count)
        c = ws.cell(1, 1)
        c.value = (
            f"農業部農田水利署\n推廣管路灌溉設施計畫\n"
            f"{year}年度各{label_col_name.strip()}事業區域內外推動成果統計表"
        )
        c.font = _XL_F16
        c.alignment = _XL_A_WRAP

        # ── 3. Row 2 表號 + 製表日期 ─────────────────────────────────────
        ws.row_dimensions[2].height = _XL_ROW_H_DATE
        c2 = ws.cell(2, 1)
        c2.value = table_code
        c2.font = _XL_F16B
        c2.alignment = _XL_A_CTR
        today = datetime.now(timezone.utc)
        date_str = f"製表日期：{today.year - 1911}年{today.month:02d}月{today.day:02d}日"
        ws.merge_cells(start_row=2, start_column=col_count - 1, end_row=2, end_column=col_count)
        dc = ws.cell(2, col_count - 1)
        dc.value = date_str
        dc.font = _XL_F12
        dc.alignment = _XL_A_RT

        # ── 4. 三層表頭結構定義 ───────────────────────────────────────────
        if is_current_year:
            hdr1_groups = [
                (2,  7,  '已編列', _A0910_FILL_BUDGETED),
                (8,  13, '已結案', _A0910_FILL_COMPLETED),
                (14, 16, '小計',   _A0910_FILL_SUBTOTAL),
            ]
            hdr2_groups = [
                (2,  4,  '事業區域外', _A0910_FILL_BUDGETED,  True),
                (5,  7,  '事業區域內', _A0910_FILL_BUDGETED,  False),
                (8,  10, '事業區域外', _A0910_FILL_COMPLETED, True),
                (11, 13, '事業區域內', _A0910_FILL_COMPLETED, False),
                (14, 16, '小計',      _A0910_FILL_SUBTOTAL,  True),
            ]
            major_starts = {2, 8, 14}
        else:
            hdr1_groups = [
                (2, 7, '已結案', _A0910_FILL_COMPLETED),
            ]
            hdr2_groups = [
                (2, 4, '事業區域外', _A0910_FILL_COMPLETED, True),
                (5, 7, '事業區域內', _A0910_FILL_COMPLETED, False),
            ]
            major_starts = {2}

        for r in range(3, 6):
            ws.row_dimensions[r].height = _XL_ROW_H_HDR2

        # ── 5. Row 3-5 Col 1：垂直合併，顯示 label_col_name ─────────────
        # 先設邊框（左中/右中/上中），再合併（合併後底端格用 _tpl_force_interior_border 注入）
        for r in (3, 4, 5):
            ws.cell(r, 1).border = Border(left=_XL_S_M, right=_XL_S_M, top=_XL_S_M)
        ws.merge_cells(start_row=3, start_column=1, end_row=5, end_column=1)
        label_cell = ws.cell(3, 1)
        label_cell.value = label_col_name
        label_cell.font = _XL_F14
        label_cell.alignment = _XL_A_CTR
        label_cell.border = Border(left=_XL_S_M, right=_XL_S_M, top=_XL_S_M, bottom=_XL_S_M)
        # 強制注入底端格邊框
        self._tpl_force_interior_border(ws, 4, 1, Border(left=_XL_S_M, right=_XL_S_M))
        self._tpl_force_interior_border(ws, 5, 1, Border(left=_XL_S_M, right=_XL_S_M, bottom=_XL_S_M))

        # ── 6. Row 3 (HDR1)：主分組合併欄頭 ─────────────────────────────
        for (sc, ec, text, fill) in hdr1_groups:
            # 先設每格邊框再合併（_tpl_merge_horizontal 模式）
            for col in range(sc, ec + 1):
                is_left  = (col == sc)
                is_right = (col == ec)
                ws.cell(3, col).border = Border(
                    left   = _XL_S_M if is_left else None,
                    right  = _XL_S_M if is_right else None,
                    top    = _XL_S_M,
                    bottom = _XL_S_T,
                )
            ws.merge_cells(start_row=3, start_column=sc, end_row=3, end_column=ec)
            cell = ws.cell(3, sc)
            cell.value = text
            cell.font = _XL_F14
            cell.alignment = _XL_A_CTR
            cell.fill = fill

        # ── 7. Row 4 (HDR2)：子分組合併欄頭 ─────────────────────────────
        for (sc, ec, text, fill, is_major) in hdr2_groups:
            left_side  = _XL_S_M if is_major else _XL_S_T
            # 右側：若此子組緊接另一主分組，則 medium；否則 thin（非最後欄）
            right_col  = ec + 1
            is_last_col = (ec == col_count)
            right_side = _XL_S_M if (is_last_col or right_col in major_starts) else _XL_S_T
            for col in range(sc, ec + 1):
                is_col_left  = (col == sc)
                is_col_right = (col == ec)
                ws.cell(4, col).border = Border(
                    left   = left_side if is_col_left else None,
                    right  = right_side if is_col_right else None,
                    top    = _XL_S_T,
                    bottom = _XL_S_T,
                )
            ws.merge_cells(start_row=4, start_column=sc, end_row=4, end_column=ec)
            cell = ws.cell(4, sc)
            cell.value = text
            cell.font = _XL_F14
            cell.alignment = _XL_A_CTR
            cell.fill = fill

        # ── 8. Row 5 (HDR3)：指標子欄頭（不合併，每格獨立）────────────
        hdr3_texts = ['案件數', '面積\n(公頃)', '金額\n(元)']
        for col in range(2, col_count + 1):
            group_pos = (col - 2) % 3   # 0=案件數, 1=面積, 2=金額
            is_major_left  = col in major_starts
            left_side  = _XL_S_M if is_major_left else (_XL_S_T if group_pos == 0 else None)
            is_last_col    = (col == col_count)
            right_side = _XL_S_M if (is_last_col or col + 1 in major_starts) else (
                         _XL_S_M if group_pos == 2 else None)
            cell = ws.cell(5, col)
            cell.value = hdr3_texts[group_pos]
            cell.font = _XL_F14
            cell.alignment = _XL_A_WRAP
            cell.border = Border(
                left   = left_side,
                right  = right_side,
                top    = _XL_S_T,
                bottom = _XL_S_M,
            )

        # ── 9. 資料列 ─────────────────────────────────────────────────────
        for idx, row_data in enumerate(rows):
            row_num = DATA_START + idx
            ws.row_dimensions[row_num].height = _XL_ROW_H_DATA
            for col_i, val in enumerate(row_data):
                col_num = col_i + 1
                cell = ws.cell(row_num, col_num, value=val)
                cell.font = _XL_F14
                cell.alignment = _XL_A_CTR
                if col_num == 1:
                    cell.border = Border(left=_XL_S_M, right=_XL_S_M, bottom=_XL_S_T)
                else:
                    group_pos  = (col_num - 2) % 3
                    is_maj_l   = col_num in major_starts
                    left_side  = _XL_S_M if is_maj_l else (_XL_S_T if group_pos == 0 else None)
                    is_last    = (col_num == col_count)
                    right_side = _XL_S_M if (is_last or col_num + 1 in major_starts) else (
                                 _XL_S_M if group_pos == 2 else None)
                    cell.border = Border(left=left_side, right=right_side, bottom=_XL_S_T)
                    cell.number_format = _A0910_NUM_FMT[group_pos]

        # ── 10. 最末列外框底線（medium bottom）───────────────────────────
        if rows:
            last_data_row = DATA_START + len(rows) - 1
            for col_num in range(1, col_count + 1):
                cell = ws.cell(last_data_row, col_num)
                if isinstance(cell, MergedCell):
                    continue
                b = cell.border
                cell.border = Border(
                    left   = b.left   if b else None,
                    right  = b.right  if b else None,
                    top    = b.top    if b else None,
                    bottom = _XL_S_M,
                )

        # ── 11. 備註列（與末列間隔一空列）───────────────────────────────
        note_row = DATA_START + len(rows) + 1
        ws.merge_cells(f"A{note_row}:{last_col_letter}{note_row}")
        note_c = ws.cell(note_row, 1)
        note_c.value = _A0910_NOTE_TEXT
        note_c.font = _XL_F14
        note_c.alignment = _XL_A_NOTE
        ws.row_dimensions[note_row].height = _A0910_ROW_H_NOTE

        # ── 12. 儲存 ──────────────────────────────────────────────────────
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        file_path = self.temp_dir / f"{table_code}_{year}_{timestamp}.xlsx"
        workbook.save(str(file_path))
        return str(file_path)

    def _generate_b01_report(
        self,
        template_name: str,
        col_count: int,
        title_text: str,
        date_text: str,
        rows: List[List[Any]],
        filename_prefix: str,
    ) -> str:
        """
        B01 報表通用生成邏輯（範本驅動 + 動態增長）

        架構與 A02 完全一致，但欄位數量不同：
        - B01-1/B01-3: 7欄（縣市 + 管理區內3指標 + 管理區外3指標）
        - B01-2/B01-4: 7欄（管理處 + 管理區內3指標 + 管理區外3指標）
        """
        from openpyxl import load_workbook
        from openpyxl.styles import Border
        from openpyxl.cell.cell import MergedCell

        template_path = settings.get_template_path(template_name)
        if not template_path.exists():
            raise FileNotFoundError(f"範本檔案不存在: {template_path}")

        workbook = load_workbook(str(template_path))
        worksheet = workbook.active

        # 移除 Print Area 定義以避免警告
        if 'Print_Area' in workbook.defined_names:
            del workbook.defined_names['Print_Area']

        DATA_START_ROW = 4
        HEADER_ROW = 3

        # 1. 從範本擷取樣式參考（Row 4）
        col_styles = {}
        frame_bottom_sides = {}
        for col in range(1, col_count + 1):
            ref_cell = worksheet.cell(row=DATA_START_ROW, column=col)
            col_styles[col] = {
                'font': copy(ref_cell.font) if ref_cell.font else None,
                'alignment': copy(ref_cell.alignment) if ref_cell.alignment else None,
                'border': copy(ref_cell.border) if ref_cell.border else None,
                'fill': copy(ref_cell.fill) if ref_cell.fill else None,
                'number_format': ref_cell.number_format,
            }
            # 表頭底部邊框
            header_cell = worksheet.cell(row=HEADER_ROW, column=col)
            if (header_cell.border and header_cell.border.bottom
                    and getattr(header_cell.border.bottom, 'style', None)):
                frame_bottom_sides[col] = header_cell.border.bottom

        # 2. 標題與日期（第1列與第2列）
        worksheet['A1'] = title_text
        last_col_letter = get_column_letter(col_count)
        self._set_cell_value_safe(worksheet, f'{last_col_letter}2', date_text)

        # 3. 清除範例資料（保留 Row 3 表頭和 Row 4 樣式參考）
        max_row = worksheet.max_row
        for row in range(DATA_START_ROW, max_row + 1):
            for col in range(1, col_count + 1):
                cell = worksheet.cell(row=row, column=col)
                # 跳過合併單元格（MergedCell 的 value 是唯讀的）
                if not isinstance(cell, MergedCell):
                    cell.value = None
                    cell.border = Border()
            if row in worksheet.row_dimensions:
                del worksheet.row_dimensions[row]

        # 4. 動態新增資料列 + 應用範本樣式
        for row_idx, row_data in enumerate(rows, start=DATA_START_ROW):
            for col_idx, value in enumerate(row_data, start=1):
                if col_idx > col_count:
                    continue
                cell = worksheet.cell(row=row_idx, column=col_idx, value=value)
                # 應用範本樣式
                style = col_styles.get(col_idx, {})
                if style.get('font'):
                    cell.font = copy(style['font'])
                if style.get('alignment'):
                    cell.alignment = copy(style['alignment'])
                if style.get('border'):
                    cell.border = copy(style['border'])
                if style.get('fill'):
                    cell.fill = copy(style['fill'])
                if style.get('number_format'):
                    cell.number_format = style['number_format']

        # 5. 小計列
        last_data_row = DATA_START_ROW + len(rows) - 1
        subtotal_row = last_data_row + 1
        self._set_cell_value_safe_by_position(worksheet, subtotal_row, 1, "小計")

        # 應用小計列樣式並計算總和公式
        for col in range(1, col_count + 1):
            cell = worksheet.cell(row=subtotal_row, column=col)
            style = col_styles.get(col, {})
            if style.get('font'):
                cell.font = copy(style['font'])
            if style.get('alignment'):
                cell.alignment = copy(style['alignment'])
            if style.get('fill'):
                cell.fill = copy(style['fill'])

            # 數字欄位加總公式（第2欄起為數字）
            if col > 1:
                col_letter = get_column_letter(col)
                sum_formula = f"=SUM({col_letter}{DATA_START_ROW}:{col_letter}{last_data_row})"
                self._set_cell_value_safe_by_position(worksheet, subtotal_row, col, sum_formula)
                if style.get('number_format'):
                    cell.number_format = style['number_format']

            # 底部邊框（表格外框）
            if col in frame_bottom_sides:
                current_border = copy(cell.border) if cell.border else Border()
                cell.border = Border(
                    left=current_border.left,
                    right=current_border.right,
                    top=current_border.top,
                    bottom=frame_bottom_sides[col]
                )

        # 6. 備註（緊跟小計列之後）
        note_row = subtotal_row + 1
        self._set_cell_value_safe_by_position(worksheet, note_row, 1, "註：案件數為有效之有案號案件數")

        # 儲存檔案
        output_filename = f"{filename_prefix}.xlsx"
        output_path = self.temp_dir / output_filename
        workbook.save(str(output_path))
        return str(output_path)

    async def generate_a09_report(self, data: Dict[str, Any], year: int) -> str:
        """生成 A09 各縣市事業區域內外推動成果統計表"""
        is_current_year: bool = data.get('is_current_year', False)
        rows = []
        for s in data.get('stats', []):
            boc = s.get('budgeted_outside_cases', 0) or 0
            boa = float(s.get('budgeted_outside_area', 0) or 0)
            bos = s.get('budgeted_outside_subsidy', 0) or 0
            bic = s.get('budgeted_inside_cases', 0) or 0
            bia = float(s.get('budgeted_inside_area', 0) or 0)
            bis_ = s.get('budgeted_inside_subsidy', 0) or 0
            coc = s.get('completed_outside_cases', 0) or 0
            coa = float(s.get('completed_outside_area', 0) or 0)
            cos_ = s.get('completed_outside_subsidy', 0) or 0
            cic = s.get('completed_inside_cases', 0) or 0
            cia = float(s.get('completed_inside_area', 0) or 0)
            cis = s.get('completed_inside_subsidy', 0) or 0
            row: list = [s.get('county_name', '')]
            if is_current_year:
                row += [boc, boa, bos, bic, bia, bis_]
            row += [coc, coa, cos_, cic, cia, cis]
            if is_current_year:
                row += [boc + bic + coc + cic, boa + bia + coa + cia, bos + bis_ + cos_ + cis]
            rows.append(row)
        return self._generate_a09_a10_report('A09', '縣 市', year, is_current_year, rows)

    async def generate_a10_report(self, data: Dict[str, Any], year: int) -> str:
        """生成 A10 各管理處事業區域內外推動成果統計表"""
        is_current_year: bool = data.get('is_current_year', False)
        rows = []
        for s in data.get('stats', []):
            boc = s.get('budgeted_outside_cases', 0) or 0
            boa = float(s.get('budgeted_outside_area', 0) or 0)
            bos = s.get('budgeted_outside_subsidy', 0) or 0
            bic = s.get('budgeted_inside_cases', 0) or 0
            bia = float(s.get('budgeted_inside_area', 0) or 0)
            bis_ = s.get('budgeted_inside_subsidy', 0) or 0
            coc = s.get('completed_outside_cases', 0) or 0
            coa = float(s.get('completed_outside_area', 0) or 0)
            cos_ = s.get('completed_outside_subsidy', 0) or 0
            cic = s.get('completed_inside_cases', 0) or 0
            cia = float(s.get('completed_inside_area', 0) or 0)
            cis = s.get('completed_inside_subsidy', 0) or 0
            row: list = [s.get('office_name', '')]
            if is_current_year:
                row += [boc, boa, bos, bic, bia, bis_]
            row += [coc, coa, cos_, cic, cia, cis]
            if is_current_year:
                row += [boc + bic + coc + cic, boa + bia + coa + cia, bos + bis_ + cos_ + cis]
            rows.append(row)
        return self._generate_a09_a10_report('A10', '管理處', year, is_current_year, rows)

    async def generate_b01_1_report(self, data: Dict[str, Any], year: int) -> str:
        """生成 B01-1 各縣市管理區內外統計報表（單年度）"""
        today = datetime.now()
        rows = []
        for s in data.get('stats', []):
            rows.append([
                s.get('county_name', ''),
                # 管理區內
                s.get('inside_cases', 0) or 0,
                float(s.get('inside_area', 0) or 0),
                s.get('inside_subsidy', 0) or 0,
                # 管理區外
                s.get('outside_cases', 0) or 0,
                float(s.get('outside_area', 0) or 0),
                s.get('outside_subsidy', 0) or 0,
            ])
        return self._generate_b01_report(
            template_name="B01-1.xlsx",
            col_count=7,
            title_text=f"農業部農田水利署\n推廣管路灌溉設施計畫\n{year}年度各縣市推動成果統計表",
            date_text=f"製表日期：{today.year - 1911}年{today.month:02d}月{today.day:02d}日",
            rows=rows,
            filename_prefix=f"B01-1_{year}",
        )

    async def generate_b01_2_report(self, data: Dict[str, Any], year: int) -> str:
        """生成 B01-2 各管理處管理區內外統計報表（單年度）"""
        today = datetime.now()
        rows = []
        for s in data.get('stats', []):
            rows.append([
                s.get('office_name', ''),
                # 管理區內
                s.get('inside_cases', 0) or 0,
                float(s.get('inside_area', 0) or 0),
                s.get('inside_subsidy', 0) or 0,
                # 管理區外
                s.get('outside_cases', 0) or 0,
                float(s.get('outside_area', 0) or 0),
                s.get('outside_subsidy', 0) or 0,
            ])
        return self._generate_b01_report(
            template_name="B01-2.xlsx",
            col_count=7,
            title_text=f"農業部農田水利署\n推廣管路灌溉設施計畫\n{year}年度各管理處推動成果統計表",
            date_text=f"製表日期：{today.year - 1911}年{today.month:02d}月{today.day:02d}日",
            rows=rows,
            filename_prefix=f"B01-2_{year}",
        )

    async def generate_b01_3_report(self, data: Dict[str, Any], start_year: int, end_year: int) -> str:
        """生成 B01-3 歷年各縣市管理區內外統計報表"""
        today = datetime.now()
        rows = []
        for s in data.get('stats', []):
            rows.append([
                s.get('county_name', ''),
                # 管理區內
                s.get('inside_cases', 0) or 0,
                float(s.get('inside_area', 0) or 0),
                s.get('inside_subsidy', 0) or 0,
                # 管理區外
                s.get('outside_cases', 0) or 0,
                float(s.get('outside_area', 0) or 0),
                s.get('outside_subsidy', 0) or 0,
            ])
        return self._generate_b01_report(
            template_name="B01-3.xlsx",
            col_count=7,
            title_text=f"農業部農田水利署\n推廣管路灌溉設施計畫\n{start_year}年度～{end_year}年度各縣市推動成果統計表",
            date_text=f"製表日期：{today.year - 1911}年{today.month:02d}月{today.day:02d}日",
            rows=rows,
            filename_prefix=f"B01-3_{start_year}-{end_year}",
        )

    async def generate_b01_4_report(self, data: Dict[str, Any], start_year: int, end_year: int) -> str:
        """生成 B01-4 歷年各管理處管理區內外統計報表"""
        today = datetime.now()
        rows = []
        for s in data.get('stats', []):
            rows.append([
                s.get('office_name', ''),
                # 管理區內
                s.get('inside_cases', 0) or 0,
                float(s.get('inside_area', 0) or 0),
                s.get('inside_subsidy', 0) or 0,
                # 管理區外
                s.get('outside_cases', 0) or 0,
                float(s.get('outside_area', 0) or 0),
                s.get('outside_subsidy', 0) or 0,
            ])
        return self._generate_b01_report(
            template_name="B01-4.xlsx",
            col_count=7,
            title_text=f"農業部農田水利署\n推廣管路灌溉設施計畫\n{start_year}年度～{end_year}年度各管理處推動成果統計表",
            date_text=f"製表日期：{today.year - 1911}年{today.month:02d}月{today.day:02d}日",
            rows=rows,
            filename_prefix=f"B01-4_{start_year}-{end_year}",
        )

    async def generate_b03_report(self, data: Dict[str, Any], year: int) -> str:
        """
        生成 B03 各縣市鄉鎮區各類補助項目統計表 Excel（規則建構，19欄 4列標題）

        Args:
            data: B03StatsResponse.dict() 資料
            year: 統計年度（民國年）

        Returns:
            str: 生成的 Excel 檔案路徑
        """
        COL_COUNT = 19
        DATA_START = 5  # Row 1 主標題, Row 2 代號+日期, Row 3 父標題, Row 4 子標題

        workbook = Workbook()
        ws = workbook.active

        # 1. 欄寬
        for col, w in _B03_COL_WIDTHS.items():
            ws.column_dimensions[get_column_letter(col)].width = w

        # 2. Row 1 主標題（合併 A1:S1）
        ws.row_dimensions[1].height = _XL_ROW_H_TITLE
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=COL_COUNT)
        c1 = ws.cell(1, 1)
        c1.value = f"農業部農田水利署\n推廣管路灌溉設施計畫\n{year}年度各縣市鄉鎮區各類補助項目統計表"
        c1.font = _XL_F16
        c1.alignment = _XL_A_WRAP

        # 3. Row 2 代號 + 製表日期
        ws.row_dimensions[2].height = _XL_ROW_H_DATE
        c2 = ws.cell(2, 1)
        c2.value = 'B03'
        c2.font = _XL_F16B  # type: ignore[attr-defined]
        c2.alignment = _XL_A_CTR
        today = datetime.now()
        date_str = f"製表日期：{today.year - 1911}年{today.month:02d}月{today.day:02d}日"
        ws.merge_cells(start_row=2, start_column=16, end_row=2, end_column=COL_COUNT)
        dc = ws.cell(2, 16)
        dc.value = date_str
        dc.font = _XL_F12
        dc.alignment = _XL_A_RT

        # 4. Row 3 父標題層 指定高度，不共用
        ws.row_dimensions[3].height = 45

        def _mhdr(col, end_col, end_row, text, wrap=False):
            """合併並寫入父標題格，並補齊合併範圍邊緣格的 border"""
            if end_col > col or end_row > 3:
                ws.merge_cells(start_row=3, start_column=col, end_row=end_row, end_column=end_col)
            is_left = col == 1
            is_right = end_col == COL_COUNT
            btm3 = _XL_S_T if end_row == 3 else _XL_S_M
            # Row 3：整行補 top border；首/末欄設 left/right
            for ci in range(col, end_col + 1):
                ws.cell(3, ci).border = Border(
                    top=_XL_S_M,
                    bottom=btm3,
                    left=(_XL_S_M if is_left else _XL_S_T) if ci == col else None,
                    right=(_XL_S_M if is_right else _XL_S_T) if ci == end_col else None,
                )
            # Row 4（跨行）：整行補 bottom border；首/末欄設 left/right
            if end_row > 3:
                for ci in range(col, end_col + 1):
                    ws.cell(end_row, ci).border = Border(
                        bottom=_XL_S_M,
                        left=(_XL_S_M if is_left else _XL_S_T) if ci == col else None,
                        right=(_XL_S_M if is_right else _XL_S_T) if ci == end_col else None,
                    )
            # 值和樣式只寫在 top-left 格
            c = ws.cell(3, col)
            c.value = text
            c.font = _XL_F14
            c.alignment = _XL_A_WRAP if wrap else _XL_A_CTR

        _mhdr(1, 2, 3, '地點')                                      # A3:B3
        _mhdr(3, 3, 4, '灌溉型式')                                   # C3:C4
        _mhdr(4, 4, 4, '補助面積\n(公頃)', wrap=True)                 # D3:D4
        _mhdr(5, 5, 4, '補助案件數\n(已結案)', wrap=True)             # E3:E4
        _mhdr(6, 6, 4, '農戶配合款\n(元)', wrap=True)                 # F3:F4
        _mhdr(7, 12, 3, '補助經費(元)')                               # G3:L3
        _mhdr(13, 13, 4, '工程經費\n合計(元)', wrap=True)             # M3:M4
        _mhdr(14, 15, 3, '調蓄設施蓄水池*')                           # N3:O3
        _mhdr(16, 16, 3, '動力設施')                                    # P3 only
        _mhdr(17, 19, 3, '每公頃工程單價\n(田間管路設施部分)', wrap=True)  # Q3:S3

        # 5. Row 4 子標題層
        ws.row_dimensions[4].height = _XL_ROW_H_HDR2
        sub_headers = {
            1: '縣市', 2: '鄉鎮區',
            7: '田間管路\n設施(元)', 8: '調蓄\n設施(元)', 9: '動力\n設施(元)',
            10: '調控\n設備(元)', 11: '設計費\n(元)', 12: '總計(元)',
            14: '噸', 15: '座', 16: '抽水機\n(臺)',
            17: '補助款\n(元)', 18: '百分比%', 19: '總工程費\n(元)',
        }
        for col, text in sub_headers.items():
            c = ws.cell(4, col)
            c.value = text
            c.font = _XL_F14
            c.alignment = _XL_A_WRAP
            c.border = Border(
                left=_XL_S_M if col == 1 else _XL_S_T,
                right=_XL_S_M if col == COL_COUNT else _XL_S_T,
                top=_XL_S_T, bottom=_XL_S_M
            )

        # 6. 資料列
        rows = data.get('rows', [])
        for idx, row in enumerate(rows):
            r = DATA_START + idx
            ws.row_dimensions[r].height = _XL_ROW_H_DATA
            vals = [
                row.get('county_name', ''),
                row.get('town_name', ''),
                row.get('irrigation_type', ''),
                float(row.get('total_area', 0) or 0),
                int(row.get('completed_cases', 0) or 0),
                int(row.get('farmer_contribution', 0) or 0),
                int(row.get('pipeline_subsidy', 0) or 0),
                int(row.get('storage_subsidy', 0) or 0),
                int(row.get('power_subsidy', 0) or 0),
                int(row.get('control_subsidy', 0) or 0),
                int(row.get('design_fee_subsidy', 0) or 0),
                int(row.get('total_subsidy', 0) or 0),
                int(row.get('total_engineering', 0) or 0),
                int(row.get('storage_tonnage', 0) or 0),
                int(row.get('storage_count', 0) or 0),
                int(row.get('pump_count', 0) or 0),
                int(row.get('subsidy_per_ha', 0) or 0),
                float(row.get('pipeline_ratio', 0) or 0),
                int(row.get('engineering_per_ha', 0) or 0),
            ]
            for ci, val in enumerate(vals):
                cell = ws.cell(r, ci + 1)
                cell.value = val
                cell.font = _XL_F14
                cell.alignment = _XL_A_CTR
                cell.number_format = _B03_NUM_FMT[ci + 1]
                cell.border = Border(
                    left=_XL_S_M if ci == 0 else _XL_S_T,
                    right=_XL_S_M if ci == COL_COUNT - 1 else _XL_S_T,
                    bottom=_XL_S_T
                )

        # 7. 全表合計列
        total_row = DATA_START + len(rows)
        ws.row_dimensions[total_row].height = _XL_ROW_H_TOTAL
        total_vals = [
            '合計', '',
            '',
            float(data.get('total_area', 0) or 0),
            int(data.get('total_cases', 0) or 0),
            int(data.get('total_farmer_contribution', 0) or 0),
            int(data.get('total_pipeline_subsidy', 0) or 0),
            int(data.get('total_storage_subsidy', 0) or 0),
            int(data.get('total_power_subsidy', 0) or 0),
            int(data.get('total_control_subsidy', 0) or 0),
            int(data.get('total_design_fee_subsidy', 0) or 0),
            int(data.get('total_subsidy', 0) or 0),
            int(data.get('total_engineering', 0) or 0),
            int(data.get('total_storage_tonnage', 0) or 0),
            int(data.get('total_storage_count', 0) or 0),
            int(data.get('total_pump_count', 0) or 0),
            '', '', '',  # per-ha 合計欄不顯示
        ]
        for ci, val in enumerate(total_vals):
            cell = ws.cell(total_row, ci + 1)
            cell.value = val
            cell.font = _XL_F14
            cell.alignment = _XL_A_CTR
            cell.number_format = _B03_NUM_FMT[ci + 1]
            cell.border = Border(
                left=_XL_S_M if ci == 0 else _XL_S_T,
                right=_XL_S_M if ci == COL_COUNT - 1 else _XL_S_T,
                bottom=_XL_S_M
            )

        # 8. 備註列
        note_row = total_row + 2
        ws.merge_cells(start_row=note_row, start_column=1, end_row=note_row, end_column=COL_COUNT)
        note_c = ws.cell(note_row, 1)
        note_c.value = _B03_NOTE_TEXT
        note_c.font = _XL_F14
        note_c.alignment = _XL_A_NOTE
        ws.row_dimensions[note_row].height = _XL_ROW_H_NOTE

        # 9. 儲存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = self.temp_dir / f"B03_county_town_subsidy_{year}_{timestamp}.xlsx"
        workbook.save(str(file_path))
        return str(file_path)

    def cleanup_temp_files(self, max_age_hours: int = 24):
        """清理超過指定時間的臨時檔案"""
        import time

        current_time = time.time()
        max_age_seconds = max_age_hours * 3600

        for file_path in self.temp_dir.glob("*.xls*"):
            if current_time - file_path.stat().st_mtime > max_age_seconds:
                try:
                    file_path.unlink()
                except OSError:
                    pass  # 忽略刪除失敗的檔案