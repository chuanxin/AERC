"""
完整對齊舊版 SQL 的歷史案件遷移腳本

設計原則：
1. 完全對齊舊版 SQL 的所有欄位定義
2. all_steps_data 包含完整的 4 區塊：steps, legacy_data, metadata, pay_detail
3. 支援迭代修正和測試
"""

import pymssql
import psycopg2
from psycopg2.extras import Json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date, time
from collections import defaultdict
import logging
from dotenv import load_dotenv
import os
import hashlib

load_dotenv()

# 日誌設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'migration_legacy_complete_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LegacyGrantMigration:
    """
    完整對齊舊版 SQL 的歷史案件遷移器
    """

    def __init__(self, mssql_host: str, mssql_user: str, mssql_password: str, mssql_database: str, pg_conn_str: str):
        self.mssql_conn = pymssql.connect(
            server=mssql_host,
            user=mssql_user,
            password=mssql_password,
            database=mssql_database
        )
        self.pg_conn = psycopg2.connect(pg_conn_str)
        self.stats = {
            'total_cases': 0,
            'success_cases': 0,
            'failed_cases': 0,
            'skipped_cases': 0
        }

        # 快取資料
        self.land_data_cache = {}    # 地段代碼對照表
        self.office_id_cache = {}    # 單位 ID 對照表
        self.section_mapping = {}    # Section code to name mapping
        self.county_mapping = {}     # City_Code -> county_id
        self.town_mapping = {}       # (county_id, town_name) -> town_id
        self.section_info_cache = {} # Section -> (Town_Id, City_Code, Indigenous)
        self.crop_category_mapping = {}  # crop_name -> category_name

        # 載入快取
        self._load_land_data_cache()
        self._load_office_cache()
        self._load_section_mapping()
        self._load_county_mapping()
        self._load_town_mapping()
        self._load_section_info_cache()
        self._load_crop_category_mapping()

    def _load_land_data_cache(self):
        """載入地段代碼對照表到快取"""
        logger.info("載入地段代碼對照表...")
        cursor = self.mssql_conn.cursor()
        cursor.execute("""
            SELECT
                Section_Code,
                City,
                Town,
                Section,
                Subsection
            FROM LandData
        """)

        for row in cursor.fetchall():
            section_code, city, town, section, subsection = row
            if section_code:
                self.land_data_cache[section_code] = {
                    'city': city or '',
                    'town': town or '',
                    'section': section or '',
                    'subsection': subsection or ''
                }

        logger.info(f"載入 {len(self.land_data_cache)} 個地段代碼")

    def _load_office_cache(self):
        """載入單位 ID 對照表"""
        logger.info("載入單位對照表...")
        cursor = self.pg_conn.cursor()
        cursor.execute("SELECT id, name FROM offices")

        for office_id, office_name in cursor.fetchall():
            self.office_id_cache[office_name] = office_id

        logger.info(f"載入 {len(self.office_id_cache)} 個單位")

    def _load_section_mapping(self):
        """載入 section mapping（如果 temp_section_mapping 表存在）"""
        try:
            cursor = self.pg_conn.cursor()
            cursor.execute("""
                SELECT section_id, section
                FROM temp_section_mapping
            """)
            for section_id, section_name in cursor.fetchall():
                self.section_mapping[section_id] = section_name
            logger.info(f"載入 {len(self.section_mapping)} 個 section mapping")
        except Exception as e:
            logger.warning(f"temp_section_mapping 表不存在或無法讀取: {e}")
            self.section_mapping = {}

    def _load_county_mapping(self):
        """載入縣市映射（City_Code -> county_id）"""
        logger.info("載入縣市對照表...")
        cursor = self.pg_conn.cursor()
        cursor.execute("""
            SELECT id, land_code
            FROM counties
            WHERE land_code IS NOT NULL
        """)
        
        for county_id, land_code in cursor.fetchall():
            self.county_mapping[land_code] = county_id
        
        logger.info(f"載入 {len(self.county_mapping)} 個縣市映射")

    def _load_town_mapping(self):
        """載入鄉鎮映射（(county_id, town_name) -> town_id）"""
        logger.info("載入鄉鎮對照表...")
        cursor = self.pg_conn.cursor()
        cursor.execute("""
            SELECT id, county_id, name
            FROM towns
        """)
        
        for town_id, county_id, town_name in cursor.fetchall():
            self.town_mapping[(county_id, town_name)] = town_id
        
        logger.info(f"載入 {len(self.town_mapping)} 個鄉鎮映射")

    def _load_section_info_cache(self):
        """載入地段資訊快取（Section -> Town_Id, City_Code, Indigenous）"""
        logger.info("載入地段資訊快取...")
        cursor = self.mssql_conn.cursor(as_dict=True)
        
        # 從 Common.dbo.Section 和 Common.dbo.Town 聯合查詢
        cursor.execute("""
            SELECT 
                s.Section_Id,
                s.Town_Id,
                t.Town,
                t.City_Code,
                s.Indigenous
            FROM Common.dbo.Section s
            LEFT JOIN Common.dbo.Town t ON s.Town_Id = t.Town_Id
        """)
        
        for row in cursor.fetchall():
            section_id = row['Section_Id']
            if section_id:
                self.section_info_cache[section_id] = {
                    'town_id': row['Town_Id'],
                    'town_name': row['Town'] or '',
                    'city_code': row['City_Code'],
                    'indigenous': row['Indigenous'] or 0
                }
        
        logger.info(f"載入 {len(self.section_info_cache)} 個地段資訊")

    def _get_land_county_town(self, section_id: int, indigenous: int = 0) -> Dict[str, Any]:
        """獲取土地的縣市和鄉鎮 ID
        
        參數:
            section_id: 地段代碼
            indigenous: 原住民地區標記（0 或 1）
            
        返回:
            {'county_id': int, 'town_id': int, 'is_aboriginal': bool, 'section_code': str}
        """
        if not section_id or section_id not in self.section_info_cache:
            return {'county_id': None, 'town_id': None, 'is_aboriginal': False, 'section_code': '0000'}
        
        section_info = self.section_info_cache[section_id]
        city_code = section_info.get('city_code')
        town_name = section_info.get('town_name')
        section_code = section_info.get('section_code', '0000')
        
        # 獲取縣市 ID
        county_id = self.county_mapping.get(city_code) if city_code else None
        
        # 獲取鄉鎮 ID
        town_id = None
        if county_id and town_name:
            town_id = self.town_mapping.get((county_id, town_name))
        
        # 轉換 Indigenous 為布林值
        is_aboriginal = bool(indigenous)
        
        return {
            'county_id': county_id,
            'town_id': town_id,
            'is_aboriginal': is_aboriginal,
            'section_code': section_code  # 補零後的 Section_Code (4 位)
        }

    def _load_county_mapping(self):
        """載入縣市映射（City_Code -> county_id）"""
        logger.info("載入縣市對照表...")
        cursor = self.pg_conn.cursor()
        cursor.execute("""
            SELECT id, land_code
            FROM counties
            WHERE land_code IS NOT NULL
        """)
        
        for county_id, land_code in cursor.fetchall():
            self.county_mapping[land_code] = county_id
        
        logger.info(f"載入 {len(self.county_mapping)} 個縣市映射")

    def _load_town_mapping(self):
        """載入鄉鎮映射（(county_id, town_name) -> town_id）"""
        logger.info("載入鄉鎮對照表...")
        cursor = self.pg_conn.cursor()
        cursor.execute("""
            SELECT id, county_id, name
            FROM towns
        """)
        
        for town_id, county_id, town_name in cursor.fetchall():
            self.town_mapping[(county_id, town_name)] = town_id
        
        logger.info(f"載入 {len(self.town_mapping)} 個鄉鎮映射")

    def _load_section_info_cache(self):
        """載入地段資訊快取（Section -> Town_Id, City_Code, Town名稱, Section_Code）"""
        logger.info("載入地段資訊快取...")
        cursor = self.mssql_conn.cursor(as_dict=True)
        
        # 從 Common.dbo.Section 和 Common.dbo.Town 聯合查詢，包含 Section_Code
        cursor.execute("""
            SELECT 
                s.Section_Id,
                s.Section_Code,
                s.Town_Id,
                t.Town,
                t.City_Code
            FROM Common.dbo.Section s
            LEFT JOIN Common.dbo.Town t ON s.Town_Id = t.Town_Id
        """)
        
        for row in cursor.fetchall():
            section_id = row['Section_Id']
            if section_id:
                # 將 Section_Code 補零到 4 位
                section_code = row.get('Section_Code')
                section_code_str = str(section_code).zfill(4) if section_code else '0000'
                
                self.section_info_cache[section_id] = {
                    'town_id': row['Town_Id'],
                    'town_name': row['Town'] or '',
                    'city_code': row['City_Code'],
                    'section_code': section_code_str  # 補零後的 Section_Code
                }
        
        logger.info(f"載入 {len(self.section_info_cache)} 個地段資訊")

    def _load_crop_category_mapping(self):
        """載入作物分類映射（crop_name -> category_name）"""
        logger.info("載入作物分類對照表...")
        cursor = self.pg_conn.cursor()
        cursor.execute("""
            SELECT 
                cn.name,
                cc.name as category_name
            FROM crop_names cn
            LEFT JOIN crop_categories cc ON cn.category_id = cc.id
        """)
        
        for crop_name, category_name in cursor.fetchall():
            if crop_name:
                self.crop_category_mapping[crop_name] = category_name or '未分類'
        
        logger.info(f"載入 {len(self.crop_category_mapping)} 個作物分類映射")

    def extract_from_mssql(self, limit: int = None, year_from: int = 100) -> List[Dict]:
        """
        從 MSSQL 提取歷史案件資料（完整版本）

        Returns:
            List[case_data] - 每個 case_data 包含所有必要資訊
        """
        logger.info(f"開始從 MSSQL 提取資料（民國 {year_from} 年以後）...")

        # 主查詢：提取 CaseDetail 所有欄位
        top_clause = f"TOP {limit}" if limit else ""
        cases_query = f"""
        SELECT {top_clause}
            EventNo,
            MapNo,
            Fid,
            ApplyYear,
            ApplyUnit,
            IANum,
            Gold,
            IdNo,
            Name,
            CityCode,
            Addr,
            Phone,
            Tel,
            IsMember,
            Step,
            DesId,
            Designer_Name,
            Complete,
            PDate,
            IsIndigenous,
            EndTypeCNS,
            FTpeCNS,
            CatalogCNS,
            landTown,
            landCity,
            buildarea,
            farmarea,
            finalarea,
            Indigenous
        FROM CaseDetail
        WHERE ApplyYear >= {year_from}
          AND Complete = 1
        ORDER BY EventNo, MapNo DESC
        """

        cursor = self.mssql_conn.cursor(as_dict=True)
        cursor.execute(cases_query)

        cases = []
        for row in cursor.fetchall():
            case_data = dict(row)

            # 提取土地資料
            case_data['lands'] = self._extract_lands(row['MapNo'])

            # 提取現場勘查資料
            case_data['examine_data'] = self._extract_examine_data(row['MapNo'])

            # 提取 step4 補助項目資料
            case_data['step4_items'] = self._extract_step4_subsidy_items(row['MapNo'])

            # 提取 pay_detail 資料（從多個表）
            case_data['pay_detail'] = self._extract_pay_detail(row['MapNo'])

            cases.append(case_data)

        logger.info(f"提取 {len(cases)} 個案件")
        return cases

    def _extract_lands(self, map_no: int) -> List[Dict]:
        """提取土地資料（包含作物資訊）"""
        cursor = self.mssql_conn.cursor(as_dict=True)
        cursor.execute("""
            SELECT
                Section,
                LandNo,
                LandType,
                Long,
                Lat,
                FarmArea,
                BuildArea,
                FinalArea
            FROM FarmData
            WHERE MapNo = %s
            ORDER BY Section, LandNo
        """, (map_no,))

        lands = [dict(row) for row in cursor.fetchall()]

        # 為每筆土地提取作物資料
        for land in lands:
            land['crops'] = self._extract_crops(map_no, land.get('LandNo'))

        return lands

    def _extract_examine_data(self, map_no: int) -> Dict:
        """
        從 Examine 表提取現場勘查資料

        參數:
            map_no: MapNo

        返回:
            {
                'result': str,  # 'notComply', 'Comply'
                'e_date': str,  # 勘查日期
                'reason': str,  # 不符原因
                'remarks': str, # 備註
                'inspector': str  # 勘查人員姓名
            }
        """
        cursor = self.mssql_conn.cursor(as_dict=True)

        # 查詢 Examine 表，並 JOIN Common.Admin 取得勘查人員姓名
        cursor.execute("""
            SELECT
                e.Result,
                e.EDate,
                e.Reason,
                e.Note,
                e.Examiner,
                a.Name as ExaminerName
            FROM Examine e
            LEFT JOIN Common.dbo.Admin a ON e.Examiner = a.Admin_Id
            WHERE e.MapNo = %s
        """, (map_no,))

        row = cursor.fetchone()
        if not row:
            return {
                'result': '',
                'e_date': '',
                'reason': '',
                'remarks': '',
                'inspector': ''
            }

        result_code = row.get('Result')
        e_date = row.get('EDate')
        reason = row.get('Reason') or ''
        note = row.get('Note') or ''
        examiner_name = row.get('ExaminerName') or ''

        # 組合 Reason + Note
        combined_text = f"{reason} {note}".strip()

        # 轉換 Result 代碼
        if result_code == 0:
            result_str = 'notComply'
            reason_text = combined_text
            remarks_text = ''
        elif result_code in (1, 2):
            result_str = 'Comply'
            reason_text = ''
            remarks_text = combined_text
        else:
            result_str = ''
            reason_text = ''
            remarks_text = ''

        # 格式化日期（如果有）
        date_str = ''
        if e_date:
            try:
                if isinstance(e_date, str):
                    date_str = e_date
                else:
                    date_str = e_date.strftime('%Y-%m-%d')
            except:
                date_str = str(e_date) if e_date else ''

        return {
            'result': result_str,
            'e_date': date_str,
            'reason': reason_text,
            'remarks': remarks_text,
            'inspector': examiner_name
        }

    def _extract_step4_subsidy_items(self, map_no: int) -> List[Dict]:
        """
        從 Pay 表提取 step4 補助項目資料

        ItemCode 分類:
        1: 田間管路設施費 (step4 不包含)
        2: 規劃設計費 (step4 不包含)
        3: 水源設施費
        4: 調控設施費
        5: 動力設備費
        6: 蓄水設備費

        參數:
            map_no: MapNo

        返回:
            補助項目列表
        """
        cursor = self.mssql_conn.cursor(as_dict=True)

        # 查詢 Pay 表中的 step4 相關項目 (ItemCode = 3, 4, 5, 6)
        cursor.execute("""
            SELECT
                ItemCode,
                ApplyUnit,
                FarmerMoney,
                PayMoney,
                Total
            FROM Pay
            WHERE MapNo = %s AND ItemCode IN (3, 4, 5, 6)
            ORDER BY ItemCode
        """, (map_no,))

        pay_records = cursor.fetchall()
        all_items = []

        for pay_record in pay_records:
            item_code = pay_record.get('ItemCode')
            apply_unit = pay_record.get('ApplyUnit')
            farmer_money = float(pay_record.get('FarmerMoney') or 0)
            pay_money = float(pay_record.get('PayMoney') or 0)  # 補助款
            total = float(pay_record.get('Total') or 0)  # 總價 = PayMoney + FarmerMoney

            # ItemCode = 4: 調控設施費，需要查詢明細
            if item_code == 4:
                items = self._extract_control_facility_items(
                    map_no, apply_unit, farmer_money, pay_money, total
                )
                all_items.extend(items)
            # ItemCode = 6: 調蓄設施費，需要查詢明細
            elif item_code == 6:
                items = self._extract_storage_facility_items(
                    map_no, apply_unit, farmer_money, pay_money, total
                )
                all_items.extend(items)
            # ItemCode = 5: 動力設備費，需要查詢明細
            elif item_code == 5:
                items = self._extract_power_equipment_items(
                    map_no, apply_unit, farmer_money, pay_money, total
                )
                all_items.extend(items)
            # ItemCode = 3: 其他設施，目前只記錄總額
            else:
                type_label_map = {
                    3: "水源設施"
                }
                all_items.append({
                    'type_code': str(item_code),
                    'type_label': type_label_map.get(item_code, ''),
                    'name': type_label_map.get(item_code, ''),
                    'quantity': 1,
                    'unit_price': int(total),
                    'total_amount': int(total),
                    'subsidy_amount': int(pay_money),
                    'self_paid_amount': int(farmer_money),
                    'funding_source': str(apply_unit)  # 直接使用 ApplyUnit 代碼
                })

        return all_items

    def _extract_control_facility_items(
        self, map_no: int, apply_unit: int, farmer_money: float, pay_money: float, total: float
    ) -> List[Dict]:
        """
        提取調控設施明細（ItemCode = 4）

        資料流向: MapNo → CntrlFac.CFNo → CntrlMat (清單)

        參數:
            map_no: MapNo
            apply_unit: 補助來源代碼
            farmer_money: 自費總金額
            pay_money: 補助總金額
            total: 總金額 (PayMoney + FarmerMoney)

        返回:
            調控設施項目列表
        """
        cursor = self.mssql_conn.cursor(as_dict=True)

        # 1. 透過 MapNo 取得 CFNo
        cursor.execute("""
            SELECT CFNo
            FROM CntrlFac
            WHERE MapNo = %s
        """, (map_no,))

        cf_record = cursor.fetchone()
        if not cf_record:
            # 沒有明細，返回總額項目
            return [{
                'type_code': '4',
                'type_label': '調節控制設施',
                'name': '調節控制設施',
                'quantity': 1,
                'unit_price': int(total),
                'total_amount': int(total),
                'subsidy_amount': int(pay_money),
                'self_paid_amount': int(farmer_money),
                'funding_source': str(apply_unit),  # 直接使用 ApplyUnit 代碼
                'control_type': '未分類'  # 無明細時預設為未分類
            }]

        cf_no = cf_record['CFNo']

        # 2. 透過 CFNo 取得 CntrlMat 清單，JOIN CntrlList 取得調控類型
        cursor.execute("""
            SELECT
                cm.MatName,
                cm.MatAmtAply,
                cm.MatPriceAply,
                cm.CntrlCode,
                cl.CntrlCNS
            FROM CntrlMat cm
            LEFT JOIN CntrlList cl ON cm.CntrlCode = cl.CntrlCode
            WHERE cm.CFNo = %s
        """, (cf_no,))

        mat_records = cursor.fetchall()
        if not mat_records:
            # 沒有明細，返回總額項目
            return [{
                'type_code': '4',
                'type_label': '調節控制設施',
                'name': '調節控制設施',
                'quantity': 1,
                'unit_price': int(total),
                'total_amount': int(total),
                'subsidy_amount': int(pay_money),
                'self_paid_amount': int(farmer_money),
                'funding_source': str(apply_unit),  # 直接使用 ApplyUnit 代碼
                'control_type': '未分類'  # 無明細時預設為未分類
            }]

        # 3. 建立明細項目並分配補助/自費金額
        items = []
        total_mat_amount = sum(
            float(mat.get('MatAmtAply') or 0) * float(mat.get('MatPriceAply') or 0)
            for mat in mat_records
        )

        # 累計已分配金額，用於最後一項調整
        accumulated_subsidy = 0
        accumulated_self_paid = 0

        for idx, mat in enumerate(mat_records):
            quantity = float(mat.get('MatAmtAply') or 0)
            unit_price = float(mat.get('MatPriceAply') or 0)
            mat_total = quantity * unit_price
            is_last_item = (idx == len(mat_records) - 1)

            # 按比例分配補助和自費金額
            if total_mat_amount > 0:
                if is_last_item:
                    # 最後一項：用總金額減去已分配金額，確保總和正確
                    mat_subsidy_int = int(pay_money) - accumulated_subsidy
                    mat_self_paid_int = int(farmer_money) - accumulated_self_paid
                else:
                    # 前面的項目：正常按比例分配並四捨五入
                    ratio = mat_total / total_mat_amount
                    mat_subsidy_int = int(round(pay_money * ratio))
                    mat_self_paid_int = int(round(farmer_money * ratio))
                    accumulated_subsidy += mat_subsidy_int
                    accumulated_self_paid += mat_self_paid_int
            else:
                mat_subsidy_int = 0
                mat_self_paid_int = 0

            items.append({
                'type_code': '4',
                'type_label': '調節控制設施',
                'name': mat.get('MatName') or '',
                'quantity': int(quantity),
                'unit_price': int(unit_price),
                'total_amount': int(mat_total),
                'subsidy_amount': mat_subsidy_int,
                'self_paid_amount': mat_self_paid_int,
                'funding_source': str(apply_unit),  # 直接使用 ApplyUnit 代碼
                'control_type': mat.get('CntrlCNS') or '未分類'  # 從 CntrlList 取得調控類型
            })

        return items

    def _extract_storage_facility_items(
        self, map_no: int, apply_unit: int, farmer_money: float, pay_money: float, total: float
    ) -> List[Dict]:
        """
        提取調蓄設施明細（ItemCode = 6）

        資料流向: MapNo → PoolApply.ApplyUnit, Pool (清單) → PoolTypeList.PtypeCNS

        參數:
            map_no: MapNo
            apply_unit: 補助來源代碼（來自 Pay.ApplyUnit）
            farmer_money: 自費總金額
            pay_money: 補助總金額
            total: 總金額

        返回:
            調蓄設施項目列表
        """
        cursor = self.mssql_conn.cursor(as_dict=True)

        # 1. 查詢 PoolApply 取得 ApplyUnit（補助來源）
        cursor.execute("""
            SELECT ApplyUnit
            FROM PoolApply
            WHERE MapNo = %s
        """, (map_no,))

        pool_apply = cursor.fetchone()
        # 優先使用 PoolApply.ApplyUnit，若無則使用 Pay.ApplyUnit
        funding_source = pool_apply['ApplyUnit'] if pool_apply else apply_unit

        # 2. 透過 MapNo 取得 Pool 清單
        cursor.execute("""
            SELECT
                p.PoolWeight,
                p.PtypeCode,
                p.PoolPrice,
                pt.PtypeCNS
            FROM Pool p
            LEFT JOIN PoolTypeList pt ON p.PtypeCode = pt.PtypeCode
            WHERE p.MapNo = %s
        """, (map_no,))

        pool_records = cursor.fetchall()
        if not pool_records:
            # 沒有明細，返回總額項目
            return [{
                'type_code': '6',
                'type_label': '調蓄設施',
                'name': '調蓄設施',
                'quantity': 1,
                'unit_price': int(total),
                'total_amount': int(total),
                'subsidy_amount': int(pay_money),
                'self_paid_amount': int(farmer_money),
                'funding_source': str(funding_source),
                'storage_type': '',
                'tonnage': 0,
                'original_subsidy_price': int(total)
            }]

        # 3. 建立明細項目並分配補助/自費金額
        items = []
        total_pool_amount = sum(
            float(pool.get('PoolPrice') or 0)
            for pool in pool_records
        )

        # 累計已分配金額，用於最後一項調整
        accumulated_subsidy = 0
        accumulated_self_paid = 0

        for idx, pool in enumerate(pool_records):
            tonnage = int(pool.get('PoolWeight') or 0)
            unit_price = float(pool.get('PoolPrice') or 0)
            storage_type = pool.get('PtypeCNS') or ''
            is_last_item = (idx == len(pool_records) - 1)

            # 組合 name: "鋁合金-10噸"
            name = f"{storage_type}-{tonnage}噸" if storage_type and tonnage else storage_type or '調蓄設施'

            # 按比例分配補助和自費金額
            if total_pool_amount > 0:
                if is_last_item:
                    # 最後一項：用總金額減去已分配金額，確保總和正確
                    pool_subsidy_int = int(pay_money) - accumulated_subsidy
                    pool_self_paid_int = int(farmer_money) - accumulated_self_paid
                else:
                    # 前面的項目：正常按比例分配並四捨五入
                    ratio = unit_price / total_pool_amount
                    pool_subsidy_int = int(round(pay_money * ratio))
                    pool_self_paid_int = int(round(farmer_money * ratio))
                    accumulated_subsidy += pool_subsidy_int
                    accumulated_self_paid += pool_self_paid_int
            else:
                pool_subsidy_int = 0
                pool_self_paid_int = 0

            items.append({
                'type_code': '6',
                'type_label': '調蓄設施',
                'name': name,
                'quantity': 1,  # 每項設備數量固定為 1
                'unit_price': int(unit_price),
                'total_amount': int(unit_price),  # quantity=1，所以 total = unit_price
                'subsidy_amount': pool_subsidy_int,
                'self_paid_amount': pool_self_paid_int,
                'funding_source': str(funding_source),
                'storage_type': storage_type,
                'tonnage': tonnage,
                'original_subsidy_price': int(unit_price)  # 與 unit_price 相同
            })

        return items

    def _extract_power_equipment_items(
        self, map_no: int, apply_unit: int, farmer_money: float, pay_money: float, total: float
    ) -> List[Dict]:
        """
        提取動力設備明細（ItemCode = 5）

        資料流向: MapNo → EngApply.ApplyUnit, Engine (清單) → EngineList.EngCNS

        參數:
            map_no: MapNo
            apply_unit: 補助來源代碼（來自 Pay.ApplyUnit）
            farmer_money: 自費總金額
            pay_money: 補助總金額
            total: 總金額

        返回:
            動力設備項目列表
        """
        cursor = self.mssql_conn.cursor(as_dict=True)

        # 1. 查詢 EngApply 取得 ApplyUnit（補助來源）
        cursor.execute("""
            SELECT ApplyUnit
            FROM EngApply
            WHERE MapNo = %s
        """, (map_no,))

        eng_apply = cursor.fetchone()
        # 優先使用 EngApply.ApplyUnit，若無則使用 Pay.ApplyUnit
        funding_source = eng_apply['ApplyUnit'] if eng_apply else apply_unit

        # 2. 透過 MapNo 取得 Engine 清單
        cursor.execute("""
            SELECT
                e.EngCode,
                e.EngPrice,
                el.EngCNS
            FROM Engine e
            LEFT JOIN EngineList el ON e.EngCode = el.EngCode
            WHERE e.MapNo = %s
        """, (map_no,))

        engine_records = cursor.fetchall()
        if not engine_records:
            # 沒有明細，返回總額項目
            return [{
                'type_code': '5',
                'type_label': '動力設備',
                'name': '動力設備',
                'quantity': 1,
                'unit_price': int(total),
                'total_amount': int(total),
                'subsidy_amount': int(pay_money),
                'self_paid_amount': int(farmer_money),
                'funding_source': str(funding_source),
                'original_subsidy_price': int(total)
            }]

        # 3. 建立明細項目並分配補助/自費金額
        items = []
        total_engine_amount = sum(
            float(engine.get('EngPrice') or 0)
            for engine in engine_records
        )

        # 累計已分配金額，用於最後一項調整
        accumulated_subsidy = 0
        accumulated_self_paid = 0

        for idx, engine in enumerate(engine_records):
            unit_price = float(engine.get('EngPrice') or 0)
            name = engine.get('EngCNS') or '動力設備'
            is_last_item = (idx == len(engine_records) - 1)

            # 按比例分配補助和自費金額
            if total_engine_amount > 0:
                if is_last_item:
                    # 最後一項：用總金額減去已分配金額，確保總和正確
                    engine_subsidy_int = int(pay_money) - accumulated_subsidy
                    engine_self_paid_int = int(farmer_money) - accumulated_self_paid
                else:
                    # 前面的項目：正常按比例分配並四捨五入
                    ratio = unit_price / total_engine_amount
                    engine_subsidy_int = int(round(pay_money * ratio))
                    engine_self_paid_int = int(round(farmer_money * ratio))
                    accumulated_subsidy += engine_subsidy_int
                    accumulated_self_paid += engine_self_paid_int
            else:
                engine_subsidy_int = 0
                engine_self_paid_int = 0

            items.append({
                'type_code': '5',
                'type_label': '動力設備',
                'name': name,
                'quantity': 1,  # 每項設備數量固定為 1
                'unit_price': int(unit_price),
                'total_amount': int(unit_price),  # quantity=1，所以 total = unit_price
                'subsidy_amount': engine_subsidy_int,
                'self_paid_amount': engine_self_paid_int,
                'funding_source': str(funding_source),
                'original_subsidy_price': int(unit_price)  # 與 unit_price 相同
            })

        return items

    def _extract_step5_pipes(self, map_no: int) -> List[Dict]:
        """
        提取 Step5 管路材料清單（pipes 陣列）

        資料來源:
        1. PigingConf（L1/L2 主管材料）
        2. FarmerSys → FarmerSysM（其他材料）

        主管組材料（L1, L2 及 FarmerSysM 中的主管組）將合併排序，order 從 1 開始

        參數:
            map_no: MapNo

        返回:
            管路材料列表
        """
        cursor = self.mssql_conn.cursor(as_dict=True)
        main_pipe_materials = []  # 主管組材料
        other_materials = []       # 其他材料

        # 1. 先查詢 PigingConf 取得 L1/L2 主管材料
        cursor.execute("""
            SELECT L1, L1Mat, L1Spec, L1Amount, L1Price,
                   L2, L2Mat, L2Spec, L2Amount, L2Price
            FROM PigingConf
            WHERE MapNo = %s
        """, (map_no,))

        piging = cursor.fetchone()
        if piging:
            # L1 主管（如果有資料）
            if piging.get('L1Mat') and piging.get('L1Amount'):
                l1_mat = piging.get('L1Mat', '').strip()
                l1_spec = piging.get('L1Spec')
                l1_amount = int(piging.get('L1Amount') or 0)
                l1_price = int(piging.get('L1Price') or 0)
                l1_total = l1_amount * l1_price

                main_pipe_materials.append({
                    'order': 0,  # 臨時值，稍後重新排序
                    'pomno': None,
                    'spec1': str(int(l1_spec)) if l1_spec else '',
                    'spec2': '',
                    'spec3': '',
                    'module': '主管',
                    'groupId': 1,
                    'matname': l1_mat,
                    'mattype': '',  # 不自動判斷材質
                    'itemunit': 'm',
                    'matprice': l1_price,
                    'groupName': '主管組',
                    'matamount': l1_amount,
                    'module_id': 1,
                    'totalPrice': l1_total,
                    'description': '主管管材(L1)',
                    'specification': str(int(l1_spec)) if l1_spec else '',
                    '_source': 'L1'  # 標記來源
                })

            # L2 主管（如果有資料）
            if piging.get('L2Mat') and piging.get('L2Amount'):
                l2_mat = piging.get('L2Mat', '').strip()
                l2_spec = piging.get('L2Spec')
                l2_amount = int(piging.get('L2Amount') or 0)
                l2_price = int(piging.get('L2Price') or 0)
                l2_total = l2_amount * l2_price

                main_pipe_materials.append({
                    'order': 1,  # 臨時值，稍後重新排序
                    'pomno': None,
                    'spec1': str(int(l2_spec)) if l2_spec else '',
                    'spec2': '',
                    'spec3': '',
                    'module': '主管',
                    'groupId': 1,
                    'matname': l2_mat,
                    'mattype': '',  # 不自動判斷材質
                    'itemunit': 'm',
                    'matprice': l2_price,
                    'groupName': '主管組',
                    'matamount': l2_amount,
                    'module_id': 1,
                    'totalPrice': l2_total,
                    'description': '主管管材(L2)',
                    'specification': str(int(l2_spec)) if l2_spec else '',
                    '_source': 'L2'  # 標記來源
                })

        # 2. 查詢 FarmerSys + FarmerSysM 取得其他材料清單
        cursor.execute("""
            SELECT
                fsm.POMNo,
                fsm.ModuleNo,
                fsm.ModuleCNS,
                fsm.MatGroupID,
                fsm.MatOrder,
                fsm.MatGroupCNS,
                fsm.MName,
                fsm.Spec,
                fsm.Spec1,
                fsm.SpecName1,
                fsm.Spec2,
                fsm.SpecName2,
                fsm.Spec3,
                fsm.SpecName3,
                fsm.ItemUnit,
                fsm.SysPrice,
                fsm.Note,
                fsm.Amount,
                fsm.TotalPrice
            FROM FarmerSys fs
            INNER JOIN FarmerSysM fsm ON fs.FarSysNo = fsm.FarSysNo
            WHERE fs.MapNo = %s
            ORDER BY fsm.MatGroupID, fsm.MatOrder
        """, (map_no,))

        material_records = cursor.fetchall()

        for mat in material_records:
            # 組合規格字串
            spec1_str = str(mat.get('Spec1') or mat.get('Spec') or '')
            spec2_str = str(mat.get('Spec2') or '')
            spec3_str = str(mat.get('Spec3') or '')

            # 取得材料名稱
            mat_name = (mat.get('MName') or '').strip()

            # 從 Note 欄位提取描述
            note = mat.get('Note') or ''
            description = note.strip() if note else mat.get('ModuleCNS', '')

            # 取得分組名稱
            group_name = mat.get('MatGroupCNS') or ''

            pipe_item = {
                'order': int(mat.get('MatOrder') or 0),
                'pomno': int(mat.get('POMNo')) if mat.get('POMNo') else None,
                'spec1': spec1_str,
                'spec2': spec2_str,
                'spec3': spec3_str,
                'module': mat.get('ModuleCNS') or '',
                'groupId': int(mat.get('MatGroupID') or 0),
                'matname': mat_name,
                'mattype': '',  # 不自動判斷材質，直接使用資料庫內容
                'itemunit': mat.get('ItemUnit') or '',
                'matprice': int(mat.get('SysPrice') or 0),
                'groupName': group_name,
                'matamount': int(mat.get('Amount') or 0),
                'module_id': int(mat.get('ModuleNo') or 0),
                'totalPrice': int(mat.get('TotalPrice') or 0),
                'description': description,
                'specification': spec1_str  # 主要規格
            }

            # 判斷是否屬於主管組
            if '主管' in group_name:
                main_pipe_materials.append(pipe_item)
            else:
                other_materials.append(pipe_item)

        # 3. 合併並重新排序
        # 主管組材料（包括 L1, L2 及 FarmerSysM 中的主管組）從 order=1 開始
        for idx, item in enumerate(main_pipe_materials, start=1):
            item['order'] = idx

        # 合併所有材料：主管組在前，其他材料在後
        pipes = main_pipe_materials + other_materials

        return pipes

    def _extract_step5_config(self, map_no: int) -> Dict:
        """
        提取 Step5 配置資訊

        資料來源: PigingConf, EndType, Pay

        參數:
            map_no: MapNo

        返回:
            配置資訊字典
        """
        cursor = self.mssql_conn.cursor(as_dict=True)

        config = {
            'mainPipeLength': 0,
            'mainPipe2Length': 0,
            'mainPipeDiameterId': None,
            'mainPipeQuantity': 0,
            'mainPipeUnitPrice': 0,
            'mainPipe2DiameterId': None,
            'mainPipe2Quantity': 0,
            'mainPipe2UnitPrice': 0,
            'fieldLength': 0,
            'fieldWidth': 0,
            'irrigationTypeId': None,
            'irrigationType': None,
            'workPrice': 0,
            'designFee': 0,
            'totalAmount': 0,
            'subsidyAmount': 0,
            'selfPaidAmount': 0
        }

        # 1. 查詢 PigingConf（主管資訊 + 田區尺寸）
        cursor.execute("""
            SELECT L1, L1Mat, L1Spec, L1Amount, L1Price,
                   L2, L2Mat, L2Spec, L2Amount, L2Price,
                   WorkPrice, Cblock
            FROM PigingConf
            WHERE MapNo = %s
        """, (map_no,))

        piging = cursor.fetchone()
        if piging:
            config['mainPipeLength'] = int(piging.get('L1') or 0)
            config['mainPipeMaterial'] = piging.get('L1Mat') or ''
            config['mainPipeDiameterId'] = int(piging.get('L1Spec') or 0) if piging.get('L1Spec') else None
            config['mainPipeQuantity'] = int(piging.get('L1Amount') or 0)
            config['mainPipeUnitPrice'] = int(piging.get('L1Price') or 0)
            config['mainPipe2Length'] = int(piging.get('L2') or 0)
            config['mainPipe2Material'] = piging.get('L2Mat') or ''
            config['mainPipe2DiameterId'] = int(piging.get('L2Spec') or 0) if piging.get('L2Spec') else None
            config['mainPipe2Quantity'] = int(piging.get('L2Amount') or 0)
            config['mainPipe2UnitPrice'] = int(piging.get('L2Price') or 0)
            config['workPrice'] = int(piging.get('WorkPrice') or 0)

            # 解析 Cblock（格式：74x51）為 fieldLength x fieldWidth
            cblock = piging.get('Cblock') or ''
            if 'x' in cblock or 'X' in cblock:
                parts = cblock.replace('X', 'x').split('x')
                if len(parts) == 2:
                    try:
                        config['fieldLength'] = float(parts[0].strip())
                        config['fieldWidth'] = float(parts[1].strip())
                    except (ValueError, AttributeError):
                        pass

        # 2. 查詢 EndType（設施型式 + 灌溉類型 + 噴頭/支管間距）JOIN FacTypeList
        cursor.execute("""
            SELECT
                et.FacType,
                et.EndTypeCode,
                et.SL,
                et.SS,
                ftl.FTpeCNS
            FROM EndType et
            LEFT JOIN FacTypeList ftl ON et.FacType = ftl.FacType
            WHERE et.MapNo = %s
        """, (map_no,))

        endtype = cursor.fetchone()
        if endtype:
            end_type_code = int(endtype.get('EndTypeCode') or 0)

            # 設施型式（installationType）
            config['installationType'] = endtype.get('FTpeCNS') or ''

            # 根據 EndTypeCode 映射 irrigationTypeId 和子類型
            if end_type_code in [1, 3]:
                # EndTypeCode 1 或 3：直接使用
                config['irrigationTypeId'] = end_type_code
                if end_type_code == 1:
                    config['irrigationType'] = '穿孔管系統'
                elif end_type_code == 3:
                    config['irrigationType'] = '微噴灌系統'
                config['sprinklerSubtypeId'] = None
                config['dripperSubtypeId'] = None
            elif end_type_code == 6:
                # EndTypeCode 6 → irrigationTypeId=2, sprinklerSubtypeId=6
                config['irrigationTypeId'] = 2
                config['irrigationType'] = '噴頭系統'
                config['sprinklerSubtypeId'] = 6
                config['dripperSubtypeId'] = None
            elif end_type_code == 2:
                # EndTypeCode 2 → irrigationTypeId=2, sprinklerSubtypeId=2
                config['irrigationTypeId'] = 2
                config['irrigationType'] = '噴頭系統'
                config['sprinklerSubtypeId'] = 2
                config['dripperSubtypeId'] = None
            elif end_type_code == 7:
                # EndTypeCode 7 → irrigationTypeId=4, dripperSubtypeId=7
                config['irrigationTypeId'] = 4
                config['irrigationType'] = '滴灌系統'
                config['sprinklerSubtypeId'] = None
                config['dripperSubtypeId'] = 7
            elif end_type_code == 8:
                # EndTypeCode 8 → irrigationTypeId=4, dripperSubtypeId=8
                config['irrigationTypeId'] = 4
                config['irrigationType'] = '滴灌系統'
                config['sprinklerSubtypeId'] = None
                config['dripperSubtypeId'] = 8
            else:
                # 其他情況：使用原始值
                config['irrigationTypeId'] = end_type_code if end_type_code else None
                config['sprinklerSubtypeId'] = None
                config['dripperSubtypeId'] = None

            # SL = 支管間距, SS = 噴頭間距（不取整數）
            config['branchPipeSpacing_SL'] = float(endtype.get('SL') or 0) if endtype.get('SL') else 0
            config['sprinklerSpacing_SS'] = float(endtype.get('SS') or 0) if endtype.get('SS') else 0

        # 3. 查詢 Pay（金額資訊）
        cursor.execute("""
            SELECT ItemCode, FarmerMoney, PayMoney, Total
            FROM Pay
            WHERE MapNo = %s AND ItemCode IN (1, 2)
        """, (map_no,))

        pay_records = cursor.fetchall()
        # 先收集所有資料
        item1_pay_money = 0
        design_fee = 0
        for pay in pay_records:
            item_code = pay.get('ItemCode')
            if item_code == 1:  # 田間管路設施費
                config['totalAmount'] = int(pay.get('Total') or 0)
                item1_pay_money = int(pay.get('PayMoney') or 0)
                config['selfPaidAmount'] = int(pay.get('FarmerMoney') or 0)
            elif item_code == 2:  # 規劃設計費
                design_fee = int(pay.get('Total') or 0)
                config['designFee'] = design_fee
        
        # subsidyAmount = item_code 1 的 PayMoney + designFee
        config['subsidyAmount'] = item1_pay_money + design_fee

        return config

    def _get_funding_source_name(self, apply_unit: int) -> str:
        """
        取得補助來源名稱

        參數:
            apply_unit: 補助來源代碼

        返回:
            補助來源名稱
        """
        # TODO: 需要建立補助來源對照表
        # 目前簡單處理
        return self._get_office_name(apply_unit)

    def _extract_crops(self, map_no: int, land_no: str) -> List[Dict]:
        """
        從 MSSQL 底層資料表提取作物資料

        參考 LiugongReport_Crop view 的資料表關聯邏輯，但移除 ApplyUnit=17 限制
        資料表關聯: Farm → FarmCrop → Common.dbo.Crop

        參數:
            map_no: MapNo
            land_no: 地號（LandNo）

        返回:
            作物資料列表: [{'crop_code': int, 'crop_name': str, 'farm_area': float, ...}]
        """
        if not land_no:
            return []

        cursor = self.mssql_conn.cursor(as_dict=True)

        # 使用底層資料表，參考 LiugongReport_Crop view 的邏輯
        cursor.execute("""
            SELECT
                fc.CropCode,
                c.Crop as CropName,
                f.FarmArea,
                f.BuildArea
            FROM Farm f
            INNER JOIN FarmCrop fc ON f.FNo = fc.FNo
            INNER JOIN Common.dbo.Crop c ON fc.CropCode = c.Crop_Id
            WHERE f.MapNo = %s AND f.LandNo = %s
        """, (map_no, land_no))

        crops = []
        for row in cursor.fetchall():
            crops.append({
                'crop_code': row.get('CropCode'),
                'crop_name': row.get('CropName') or '',
                'farm_area': float(row.get('FarmArea') or 0),
                'build_area': float(row.get('BuildArea') or 0)
            })

        return crops

    def _extract_pay_detail(self, map_no: int) -> Dict:
        """
        提取 pay_detail 資料（從多個表計算）

        包含：
        - pipe_facility: 管路設施費用
        - control_facility: 調控設施費用
        - power_facility: 動力設備費用
        - storage_facility: 調蓄設施費用
        - design_fee: 設計費
        - 工作費: 工作費用
        """
        cursor = self.mssql_conn.cursor(as_dict=True)

        pay_detail = {
            'mapno': map_no,
            'amount': 0,
            'self_raised': 0,
            'pipe_facility': 0,
            'control_facility': 0,
            'power_facility': 0,
            'storage_facility': 0,
            'water_source_facility': 0,
            'design_fee': 0,
            '工作費': 0,
            '設施費總計': 0
        }

        try:
            # 1. 調蓄設施 (PoolMapping)
            cursor.execute("""
                SELECT SUM(poolprice) as total
                FROM PoolMapping
                WHERE mapno = %s
            """, (map_no,))
            row = cursor.fetchone()
            pay_detail['storage_facility'] = float(row['total'] or 0) if row else 0

            # 2. 動力設備 (EngineMapping)
            cursor.execute("""
                SELECT SUM(engprice) as total
                FROM EngineMapping
                WHERE mapno = %s
            """, (map_no,))
            row = cursor.fetchone()
            pay_detail['power_facility'] = float(row['total'] or 0) if row else 0

            # 3. 調控設施 (ControlMapping)
            cursor.execute("""
                SELECT SUM(matpriceaply * matamtaply) as total
                FROM ControlMapping
                WHERE mapno = %s
            """, (map_no,))
            row = cursor.fetchone()
            pay_detail['control_facility'] = float(row['total'] or 0) if row else 0

            # 4. 管路設施 + 工作費 (MainPipeMapping + FacilityMaterials)
            # 4.1 主管材料費
            cursor.execute("""
                SELECT (l1amount * l1price) as pipe_cost, workprice
                FROM MainPipeMapping
                WHERE mapno = %s
            """, (map_no,))
            row = cursor.fetchone()
            if row:
                pay_detail['pipe_facility'] += float(row['pipe_cost'] or 0)
                pay_detail['工作費'] = float(row['workprice'] or 0)

            # 4.2 其他設施材料費
            cursor.execute("""
                SELECT fm.farsysno
                FROM FacilityMapping fm
                WHERE fm.mapno = %s
            """, (map_no,))
            row = cursor.fetchone()
            if row:
                farsysno = row['farsysno']
                cursor.execute("""
                    SELECT SUM(totalprice) as total
                    FROM FacilityMaterials
                    WHERE farsysno = %s
                """, (farsysno,))
                mat_row = cursor.fetchone()
                if mat_row:
                    pay_detail['pipe_facility'] += float(mat_row['total'] or 0)

            # 5. 計算總金額和設計費
            facility_total = (
                pay_detail['pipe_facility'] +
                pay_detail['工作費']
            )
            pay_detail['design_fee'] = round(facility_total * 0.02)

            pay_detail['amount'] = (
                facility_total +
                pay_detail['design_fee'] +
                pay_detail['control_facility'] +
                pay_detail['power_facility'] +
                pay_detail['storage_facility']
            )

            pay_detail['設施費總計'] = facility_total

        except Exception as e:
            logger.warning(f"提取 pay_detail (MapNo: {map_no}) 失敗: {e}")

        return pay_detail

    def transform_to_legacy_format(self, case_data: Dict) -> Tuple[Dict[str, Any], List[Dict]]:
        """
        轉換成舊版 SQL 的完整格式

        Returns:
            (grant_data_with_version, land_locations)
        """
        # 1. 準備 grants 表資料（完全對齊舊版 SQL）
        # 從 Addr 欄位解析縣市、鄉鎮、詳細地址
        parsed_addr = self._parse_address(case_data['Addr'] or '')

        grant_data = {
            'sn': case_data['EventNo'],  # ← EventNo 直接對應 sn
            'case_number': str(case_data['IANum']),
            'year': case_data['ApplyYear'],  # ← 民國年，不轉換
            'applicant_name': case_data['Name'] or '',
            'applicant_id': case_data['IdNo'] or '未提供',  # 預設值
            'applicant_phone': case_data['Phone'] or case_data['Tel'] or '未提供',
            'address': parsed_addr['address'] or '未提供',  # ← 從 Addr 解析的詳細地址
            'undertracker': case_data['Designer_Name'] or '未設定',  # ← Designer_Name
            'received_date': date.today(),  # ← CURRENT_DATE
            'received_time': datetime.now().time(),  # ← CURRENT_TIME
            'status': self._get_status(case_data['Complete'], case_data['ApplyYear']),
            'status_detail': '舊系統轉入',  # ← 固定值
            'current_step': case_data['Step'],  # ← Step，不固定為 9
            'county': parsed_addr['county'] or '未提供',  # ← 優先從 Addr 解析
            'town': parsed_addr['town'] or '未提供',     # ← 優先從 Addr 解析
            'village': '',
            'office_id': case_data['ApplyUnit'],  # 1:1 映射
            'office': self._get_office_name(case_data['ApplyUnit']),
            'is_legacy': True,
            'is_disaster_case': False,
            'created_by_id': 1
        }

        # 2. 準備 all_steps_data（完整的 4 區塊結構）
        all_steps_data = self._build_complete_all_steps_data(case_data)

        # 3. 準備 grant_versions 資料
        version_data = {
            'version': case_data['MapNo'],  # ← MapNo
            'data_schema_version': 'legacy',  # ← 固定值
            'comment': self._build_comment(case_data),
            'all_steps_data_hash': self._build_hash(case_data)
        }

        return {
            'grant': grant_data,
            'version': version_data,
            'all_steps_data': all_steps_data
        }

    def _parse_address(self, addr: str) -> Dict[str, str]:
        """
        從地址字串解析縣市、鄉鎮、詳細地址

        格式: "[county] [town] [addr]" 以空格拆分
        例如: "臺中市 東勢區 中正路123號" → {'county': '臺中市', 'town': '東勢區', 'address': '中正路123號'}

        參數:
            addr: 原始地址字串（以空格分隔）

        返回:
            {'county': str, 'town': str, 'address': str}
        """
        if not addr:
            return {'county': '', 'town': '', 'address': ''}

        # 以空格拆分地址
        parts = addr.split(' ', 2)  # 最多拆分為 3 個部分
        
        if len(parts) >= 3:
            # 完整格式: county town address
            return {
                'county': parts[0].strip(),
                'town': parts[1].strip(),
                'address': parts[2].strip()
            }
        elif len(parts) == 2:
            # 只有 2 個部分: county town
            return {
                'county': parts[0].strip(),
                'town': parts[1].strip(),
                'address': ''
            }
        elif len(parts) == 1:
            # 只有 1 個部分: 全部當作 county
            return {
                'county': parts[0].strip(),
                'town': '',
                'address': ''
            }
        else:
            return {'county': '', 'town': '', 'address': ''}

    def _get_status(self, complete: int, apply_year: int) -> str:
        """
        舊版 SQL 的 status 邏輯
        """
        if complete == 1:
            return 'completed'
        elif apply_year == 114:
            return 'inactive'
        else:
            return 'archived'

    def _get_office_name(self, apply_unit: int) -> str:
        """單位代碼轉單位名稱（1:1 映射）"""
        for name, office_id in self.office_id_cache.items():
            if office_id == apply_unit:
                return name
        return f'未知單位_{apply_unit}'

    def _build_complete_all_steps_data(self, case_data: Dict) -> Dict:
        """
        建立完整的 all_steps_data 結構（4 區塊）

        包含：
        1. steps: {0, 1, 2, 3, 4, 5, 6, 7, 8} - 完整步驟資料（新格式）
        2. legacy_data: 原始 MSSQL 欄位
        3. metadata: 匯入元資料
        4. pay_detail: 補助金額明細
        """
        # 計算總設施面積
        total_facility_area = int(case_data.get('finalarea') or 0)
        total_facility_area_ha = round(total_facility_area / 10000, 4) if total_facility_area else 0
        
        return {
            # 區塊 1: steps（新格式）
            "steps": {
                "0": {
                    "id": None,  # 將在插入後更新
                    "valid": True,
                    "status": "draft",
                    "_caseNumber": str(case_data['IANum']),
                    "case_number": str(case_data['IANum']),
                    "current_step": 0,
                    "applicant_name": case_data['Name'] or '',
                    "applicant_id": case_data['IdNo'] or '',
                    "address": case_data['Addr'] or '',
                    "phone": case_data['Phone'] or case_data['Tel'] or ''
                },
                "1": {
                    "id": None,
                    "valid": True,
                    "status": "draft",
                    "_caseNumber": str(case_data['IANum']),
                    "case_number": str(case_data['IANum']),
                    "current_step": 1,
                    "applicant_name": case_data['Name'] or '',
                    "applicant_id": case_data['IdNo'] or '',
                    "address": case_data['Addr'] or '',
                    "phone": case_data['Phone'] or case_data['Tel'] or ''
                },
                "2": {
                    "id": None,
                    "lands": self._build_lands_with_crops(case_data['lands'], case_data.get('Indigenous', 0)),
                    "valid": True,
                    "status": "draft",
                    "_caseNumber": str(case_data['IANum']),
                    "case_number": str(case_data['IANum']),
                    "current_step": 2,
                    "totalFacilityArea": total_facility_area,
                    "totalFacilityAreaHa": total_facility_area_ha
                },
                "3": self._build_step3_data(case_data),
                "4": self._build_step4_data(case_data),
                "5": self._build_step5_data(case_data),
                "6": {},
                "7": {},
                "8": {}
            },

            # 區塊 2: legacy_data（所有原始欄位）
            "legacy_data": {
                "EventNo": case_data['EventNo'],
                "MapNo": case_data['MapNo'],
                "Fid": str(case_data['Fid']) if case_data.get('Fid') else '',
                "original_apply_year": case_data['ApplyYear'],
                "apply_unit": case_data['ApplyUnit'],
                "IA_number": case_data['IANum'],
                "gold_amount": case_data['Gold'] or 0,
                "city_code": case_data['CityCode'] or '',
                "is_member": case_data['IsMember'] or 0,
                "designer_id": str(case_data['DesId']) if case_data.get('DesId') else '',
                "designer_name": case_data['Designer_Name'] or '未設定',
                "irrigation_type": case_data['EndTypeCNS'] or '',
                "facility_type": case_data['FTpeCNS'] or '',
                "catalog_type": case_data['CatalogCNS'] or '',
                "build_area": case_data['buildarea'] or 0,
                "farm_area": case_data['farmarea'] or 0,
                "final_area": case_data['finalarea'] or 0
            },

            # 區塊 3: metadata
            "metadata": {
                "source": "legacy_system",
                "imported_at": datetime.now().isoformat(),
                "original_complete_status": case_data['Complete'],
                "original_step": case_data['Step'],
                "original_county": case_data['landCity'] or '',
                "original_town": case_data['landTown'] or '',
                "city_code": case_data['CityCode'] or '',
                "is_member": case_data['IsMember'] or 0
            },

            # 區塊 4: pay_detail
            "pay_detail": case_data['pay_detail']
        }

    def _build_step3_data(self, case_data: Dict) -> Dict:
        """
        建立 step3 (現場勘查) 資料

        參數:
            case_data: 案件資料（包含 examine_data）

        返回:
            step3 格式化資料
        """
        examine = case_data.get('examine_data', {})

        # 判斷 valid 狀態
        # 有勘查結果且不是 notComply 則為 valid
        is_valid = bool(examine.get('result')) and examine.get('result') != 'notComply'

        return {
            "id": None,  # 將在插入後更新
            "valid": is_valid,
            "reason": examine.get('reason', ''),
            "status": "draft",
            "remarks": examine.get('remarks', ''),
            "inspector": examine.get('inspector', ''),
            "_caseNumber": str(case_data['IANum']),
            "case_number": str(case_data['IANum']),
            "current_step": 3,
            "inspectionDate": examine.get('e_date', ''),
            "inspectionResult": examine.get('result', '')
        }

    def _build_step4_data(self, case_data: Dict) -> Dict:
        """
        建立 step4 (補助項目) 資料

        參數:
            case_data: 案件資料（包含 step4_items）

        返回:
            step4 格式化資料
        """
        items = case_data.get('step4_items', [])

        # ItemCode 對應 type 映射
        type_map = {
            '3': 'waterSource',  # 水源設施
            '4': 'control',      # 調節控制設施
            '5': 'power',        # 動力設備
            '6': 'storage'       # 調蓄設施
        }

        # 格式化為前端 facilities 格式
        facilities = []
        for item in items:
            item_code = item.get('type_code', '')
            facility = {
                'name': item.get('name', ''),
                'type': type_map.get(item_code, 'waterSource'),
                'typeLabel': item.get('type_label', ''),
                'quantity': item.get('quantity', 0),
                'unitPrice': item.get('unit_price', 0),
                'totalPrice': item.get('total_amount', 0),
                'subsidyAmount': item.get('subsidy_amount', 0),
                'selfPaidAmount': item.get('self_paid_amount', 0),
                'fundingSourceId': int(item.get('funding_source', 0)),
                'remark': ''  # 歷史資料無備註
            }

            # 添加類型特定欄位
            if facility['type'] == 'storage':
                facility['storageType'] = item.get('storage_type', '')
                facility['tonnage'] = item.get('tonnage', 0)
                facility['originalSubsidyPrice'] = item.get('original_subsidy_price', facility['unitPrice'])
            elif facility['type'] == 'power':
                facility['originalSubsidyPrice'] = item.get('original_subsidy_price', facility['unitPrice'])
            elif facility['type'] == 'control':
                facility['controlType'] = item.get('control_type', '')  # 從 CntrlList.CntrlCNS 取得

            facilities.append(facility)

        # 判斷 valid 狀態
        is_valid = len(facilities) > 0

        return {
            "id": None,  # 將在插入後更新
            "valid": is_valid,
            "status": "draft",
            "facilities": facilities,
            "_caseNumber": str(case_data['IANum']),
            "case_number": str(case_data['IANum']),
            "current_step": 4,
            # 頂層表單欄位（歷史資料為空）
            "controlName": "",
            "controlType": "",
            "storageType": "",
            "storageRemark": "",
            "storageSource": "",
            "powerEquipment": "",
            "storageTonnage": "",
            "controlQuantity": 0,
            "fundingSourceId": 0,
            "controlUnitPrice": ""
        }

    def _build_step5_data(self, case_data: Dict) -> Dict:
        """
        建立 step5 (田間管路) 資料

        參數:
            case_data: 案件資料（包含 MapNo）

        返回:
            step5 格式化資料
        """
        map_no = case_data.get('MapNo')

        # 提取管路材料清單
        pipes = self._extract_step5_pipes(map_no)

        # 提取配置資料
        config = self._extract_step5_config(map_no)

        # 判斷 valid 狀態（有 pipes 或有配置資料）
        is_valid = len(pipes) > 0 or any(config.values())

        return {
            "id": None,  # 將在插入後更新
            "valid": is_valid,
            "status": "draft",
            "pipes": pipes,
            "_caseNumber": str(case_data['IANum']),
            "case_number": str(case_data['IANum']),
            "current_step": 5,
            # 配置欄位（從 config 字典中提取，使用正確的鍵名）
            "mainPipeLength": config.get('mainPipeLength', 0),
            "mainPipeDiameterId": config.get('mainPipeDiameterId'),
            "mainPipeQuantity": config.get('mainPipeQuantity', 0),  # L1Amount - 主管1數量
            "mainPipeUnitPrice": config.get('mainPipeUnitPrice', 0),  # L1Price - 主管1單價
            "branchPipeLength": config.get('mainPipe2Length', 0),  # L2 = 分支管
            "branchPipeDiameterId": config.get('mainPipe2DiameterId'),  # L2Spec
            "mainPipe2Quantity": config.get('mainPipe2Quantity', 0),  # L2Amount - 主管2數量
            "mainPipe2UnitPrice": config.get('mainPipe2UnitPrice', 0),  # L2Price - 主管2單價
            # 設施型式與灌溉型式
            "installationType": config.get('installationType', ''),  # FacTypeList.FTpeCNS
            "irrigationType": str(config.get('irrigationType') or ''),  # 根據 EndTypeCode 映射
            "irrigationTypeId": config.get('irrigationTypeId'),  # 灌溉類型 ID
            "sprinklerSubtypeId": config.get('sprinklerSubtypeId'),  # 噴頭子類型 ID
            "dripperSubtypeId": config.get('dripperSubtypeId'),  # 滴灌子類型 ID
            # 田區資訊
            "fieldLength": config.get('fieldLength', 0),  # 從 Cblock 解析
            "fieldWidth": config.get('fieldWidth', 0),   # 從 Cblock 解析
            "sprinklerSpacing_SS": config.get('sprinklerSpacing_SS', 0),  # EndType.SS 噴頭間距
            "branchPipeSpacing_SL": config.get('branchPipeSpacing_SL', 0),  # EndType.SL 支管間距
            "workFee": config.get('workPrice', 0),  # 田間管路工作費
            "designFee": config.get('designFee', 0),
            "subsidyAmount": config.get('subsidyAmount', 0),
            "selfPaidAmount": config.get('selfPaidAmount', 0),
            "totalAmount": config.get('totalAmount', 0)
        }

    def _build_lands_with_crops(self, lands: List[Dict], indigenous: int = 0) -> List[Dict]:
        """
        建立包含作物資訊的土地資料列表（用於 step2）

        參數:
            lands: 土地資料列表（來自 _extract_lands）
            indigenous: 案件的原住民地區標記（0 或 1）

        返回:
            格式化的土地資料列表，包含作物資訊（新格式）
        """
        import time
        import random
        import string
        
        formatted_lands = []

        for land in lands:
            section_id = land.get('Section')
            
            # 獲取縣市、鄉鎮 ID 和原住民地區標記
            county_town_info = self._get_land_county_town(section_id, indigenous)
            
            # 生成唯一 ID
            timestamp = int(time.time() * 1000)
            random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))
            land_id = f"land_{timestamp}_{random_str}"
            
            # 解析地號（假設格式為 "XXXX-YYYY" 或 "XXXX"）
            land_number_str = land.get('LandNo') or ''
            if '-' in land_number_str:
                land_main, land_sub = land_number_str.split('-', 1)
            else:
                land_main = land_number_str
                land_sub = '0000'
            
            # 格式化作物資料
            crops_formatted = []
            for crop in land.get('crops', []):
                crop_name = crop.get('crop_name', '')
                crop_category = self.crop_category_mapping.get(crop_name, '')
                crops_formatted.append({
                    'name': crop_name,
                    'category': crop_category
                })
            
            # 計算面積（公頃）
            farm_area = float(land.get('FarmArea') or 0)
            final_area = float(land.get('FinalArea') or 0)
            farm_area_ha = round(farm_area / 10000, 4) if farm_area else 0
            facility_area_ha = round(final_area / 10000, 4) if final_area else 0
            
            formatted_land = {
                'id': land_id,
                'crops': crops_formatted,
                'owners': [],  # 舊系統無業主資料
                'landSec': county_town_info['section_code'],  # 使用 Section_Code (已補零)
                'ownerId': '',
                'cropName': '',
                'landArea': str(int(farm_area)),
                'landTown': county_town_info['town_id'],
                'latitude': str(land.get('Lat')) if land.get('Lat') else '',
                'longitude': str(land.get('Long')) if land.get('Long') else '',
                'ownerArea': '',
                'ownerName': '',
                'ownerTown': '',
                'landAreaHa': str(farm_area_ha),
                'landCounty': county_town_info['county_id'],
                'landNumber': land_number_str,
                'isReapplied': False,
                'landSecName': self._get_section_name(section_id),
                'ownerCounty': '',
                'ownerShare1': '',
                'ownerShare2': '',
                'cropCategory': '',
                'facilityArea': str(int(final_area)),
                'ownerVillage': '',
                'landNumberSub': land_sub.zfill(4),
                'certificateDay': '',
                'facilityAreaHa': str(facility_area_ha),
                'landNumberMain': land_main.zfill(4),
                'certificateYear': '',
                'certificateMonth': '',
                'isAboriginalArea': county_town_info['is_aboriginal'],
                'isIrrigationArea': False,
                'hasAgriculturalCertificate': False
            }
            formatted_lands.append(formatted_land)

        return formatted_lands

    def _build_comment(self, case_data: Dict) -> str:
        """建立 comment"""
        if not case_data['IdNo']:
            return f"舊系統資料轉入 - MapNo: {case_data['MapNo']}, EventNo: {case_data['EventNo']} (未提供身份證號)"
        else:
            return f"舊系統資料轉入 - MapNo: {case_data['MapNo']}, EventNo: {case_data['EventNo']}"

    def _build_hash(self, case_data: Dict) -> str:
        """建立 all_steps_data_hash"""
        hash_data = {
            'EventNo': case_data['EventNo'],
            'MapNo': case_data['MapNo'],
            'IANum': case_data['IANum'],
            'Name': case_data['Name'],
            'finalarea': case_data['finalarea'],
            'landCity': case_data['landCity'],
            'landTown': case_data['landTown']
        }
        return hashlib.md5(str(hash_data).encode()).hexdigest()

    def _build_land_locations(self, case_data: Dict, grant_id: int) -> List[Dict]:
        """
        建立 grant_locations 資料

        參數:
            case_data: 案件資料
            grant_id: grants 表的主鍵 ID

        返回:
            grant_locations 資料列表
        """
        land_locations = []

        for land in case_data['lands']:
            section_id = land.get('Section')
            section_name = self._get_section_name(section_id)
            
            # 獲取補零後的 Section_Code
            county_town_info = self._get_land_county_town(section_id, case_data.get('Indigenous', 0))
            section_code_str = county_town_info['section_code']

            # 整合作物資訊到 meta_data
            crops_info = land.get('crops', [])

            location = {
                'source_system': 'mssql_legacy',
                'source_id': str(grant_id),  # ← 修正：使用 grants.id 而非 case_number
                'apply_year': case_data['ApplyYear'],  # 民國年
                'applicant_name': case_data['Name'] or '',
                'land_section': section_code_str,  # ← 使用補零後的 Section_Code
                'land_number': land.get('LandNo') or '',
                'land_type': str(land.get('LandType') or ''),
                'case_status': self._get_status(case_data['Complete'], case_data['ApplyYear']),
                'case_number': str(case_data['IANum']),
                'comment': f"從 MSSQL 遷移（MapNo: {case_data['MapNo']}）",
                'meta_data': {
                    'farm_area': float(land.get('FarmArea') or 0),
                    'build_area': float(land.get('BuildArea') or 0),
                    'final_area': float(land.get('FinalArea') or 0),
                    'county': case_data.get('landCity'),
                    'town': case_data.get('landTown'),
                    'apply_unit': case_data['ApplyUnit'],
                    'map_no': case_data['MapNo'],
                    'section_id': section_id,  # 保留原始 Section_Id 供参考
                    'section_code': section_code_str,  # 補零後的 Section_Code
                    'crops': crops_info  # ← 加入作物資訊
                }
            }

            # 加入經緯度
            if land.get('Long') and land.get('Lat'):
                try:
                    lon = float(land['Long'])
                    lat = float(land['Lat'])
                    location['geom'] = f"POINT({lon} {lat})"
                except (ValueError, TypeError):
                    pass

            land_locations.append(location)

        return land_locations

    def _get_section_name(self, section_code: int) -> str:
        """地段代碼轉地段名稱"""
        if not section_code:
            return ''

        # 優先使用 section_mapping
        if section_code in self.section_mapping:
            return self.section_mapping[section_code]

        # 退回使用 land_data_cache
        land_info = self.land_data_cache.get(section_code)
        if land_info:
            city = land_info['city']
            town = land_info['town']
            section = land_info['section']
            return f"{city}{town}-{section}".strip()

        return str(section_code)

    def load_to_postgresql(self, transformed_data: Dict, case_data: Dict, case_number: str) -> bool:
        """
        載入資料到 PostgreSQL

        參數:
            transformed_data: 轉換後的資料（grant, version, all_steps_data）
            case_data: 原始案件資料（用於建立 land_locations）
            case_number: 案件編號（用於日誌）

        返回:
            成功返回 True，失敗或跳過返回 False
        """
        try:
            cursor = self.pg_conn.cursor()

            # 1. 檢查案件是否已存在（by sn）
            grant = transformed_data['grant']
            cursor.execute("""
                SELECT id FROM grants
                WHERE sn = %s AND is_legacy = true
            """, (grant['sn'],))

            existing = cursor.fetchone()
            if existing:
                logger.warning(f"案件 sn={grant['sn']} 已存在（ID: {existing[0]}），跳過")
                self.stats['skipped_cases'] += 1
                return False

            # 2. 插入 grants 表
            cursor.execute("""
                INSERT INTO grants (
                    sn, case_number, year, applicant_name, applicant_id,
                    applicant_phone, address, undertracker, received_date, received_time,
                    status, status_detail, current_step, county, town, village, office, office_id,
                    is_legacy, is_disaster_case, created_by_id, created_at, modified_at
                ) VALUES (
                    %(sn)s, %(case_number)s, %(year)s, %(applicant_name)s, %(applicant_id)s,
                    %(applicant_phone)s, %(address)s, %(undertracker)s, %(received_date)s, %(received_time)s,
                    %(status)s, %(status_detail)s, %(current_step)s, %(county)s, %(town)s, %(village)s, %(office)s, %(office_id)s,
                    %(is_legacy)s, %(is_disaster_case)s, %(created_by_id)s, NOW(), NOW()
                )
                RETURNING id
            """, grant)

            grant_id = cursor.fetchone()[0]

            # 2.5. 更新 all_steps_data 中的 grant ID
            all_steps_data = transformed_data['all_steps_data']
            for step_key in ['0', '1', '2', '3', '4', '5']:
                if step_key in all_steps_data['steps'] and 'id' in all_steps_data['steps'][step_key]:
                    all_steps_data['steps'][step_key]['id'] = grant_id

            # 2.6. 建立 grant_locations 資料（現在有 grant_id 了）
            land_locations = self._build_land_locations(case_data, grant_id)

            # 3. 插入 grant_versions 表
            version_data = transformed_data['version']
            cursor.execute("""
                INSERT INTO grant_versions (
                    grant_id, version, all_steps_data, all_steps_data_hash,
                    comment, data_schema_version, created_by_id, created_at, modified_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
                )
                RETURNING id
            """, (
                grant_id,
                version_data['version'],
                Json(transformed_data['all_steps_data']),
                version_data['all_steps_data_hash'],
                version_data['comment'],
                version_data['data_schema_version'],
                grant['created_by_id']
            ))

            version_id = cursor.fetchone()[0]

            # 4. 更新 grants 表的 active_version_id
            cursor.execute("""
                UPDATE grants
                SET active_version_id = %s
                WHERE id = %s
            """, (version_id, grant_id))

            # 5. 插入 grant_locations 表
            land_success_count = 0
            for land_loc in land_locations:
                try:
                    if land_loc.get('geom'):
                        cursor.execute("""
                            INSERT INTO grant_locations (
                                source_system, source_id, geom, apply_year, applicant_name,
                                land_section, land_number, land_type, case_status, case_number,
                                comment, meta_data, created_at, updated_at
                            ) VALUES (
                                %(source_system)s, %(source_id)s, ST_GeomFromText(%(geom)s, 4326),
                                %(apply_year)s, %(applicant_name)s, %(land_section)s, %(land_number)s,
                                %(land_type)s, %(case_status)s, %(case_number)s, %(comment)s,
                                %(meta_data)s::jsonb, NOW(), NOW()
                            )
                            ON CONFLICT (source_system, source_id, land_section, land_number) DO NOTHING
                        """, {**land_loc, 'meta_data': Json(land_loc['meta_data'])})
                    else:
                        cursor.execute("""
                            INSERT INTO grant_locations (
                                source_system, source_id, apply_year, applicant_name,
                                land_section, land_number, land_type, case_status, case_number,
                                comment, meta_data, created_at, updated_at
                            ) VALUES (
                                %(source_system)s, %(source_id)s, %(apply_year)s, %(applicant_name)s,
                                %(land_section)s, %(land_number)s, %(land_type)s, %(case_status)s,
                                %(case_number)s, %(comment)s, %(meta_data)s::jsonb, NOW(), NOW()
                            )
                            ON CONFLICT (source_system, source_id, land_section, land_number) DO NOTHING
                        """, {**land_loc, 'meta_data': Json(land_loc['meta_data'])})

                    land_success_count += 1
                except Exception as e:
                    logger.warning(f"土地資料插入失敗: {e}")

            self.pg_conn.commit()
            self.stats['success_cases'] += 1

            logger.info(f"✅ 成功遷移案件: sn={grant['sn']}, EventNo={grant['sn']}, MapNo={version_data['version']} (grant_id: {grant_id}, 土地筆數: {land_success_count}/{len(land_locations)})")
            return True

        except Exception as e:
            self.pg_conn.rollback()
            self.stats['failed_cases'] += 1
            logger.error(f"❌ 遷移失敗: sn={grant.get('sn', 'unknown')} - {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def migrate(self, limit: int = None, year_from: int = 100):
        """執行完整的遷移流程"""
        logger.info("=" * 80)
        logger.info("開始完整對齊舊版 SQL 的遷移（Legacy Schema）")
        logger.info(f"民國 {year_from} 年以後的案件")
        logger.info("=" * 80)

        # 1. Extract
        cases = self.extract_from_mssql(limit, year_from)
        self.stats['total_cases'] = len(cases)

        # 2. Transform + Load
        for i, case_data in enumerate(cases, 1):
            case_number = str(case_data['IANum'])
            logger.info(f"處理 {i}/{len(cases)}: EventNo={case_data['EventNo']}, IANum={case_number}, MapNo={case_data['MapNo']}")

            try:
                transformed = self.transform_to_legacy_format(case_data)
                self.load_to_postgresql(transformed, case_data, case_number)
            except Exception as e:
                logger.error(f"處理案件 EventNo={case_data['EventNo']} 時發生錯誤: {e}")
                self.stats['failed_cases'] += 1

        # 3. 報告
        self._print_summary()

    def _print_summary(self):
        """列印遷移摘要"""
        logger.info("")
        logger.info("=" * 80)
        logger.info("遷移完成摘要")
        logger.info("=" * 80)
        logger.info(f"總案件數: {self.stats['total_cases']}")
        logger.info(f"成功遷移: {self.stats['success_cases']}")
        logger.info(f"跳過（重複）: {self.stats['skipped_cases']}")
        logger.info(f"失敗: {self.stats['failed_cases']}")

        success_rate = (self.stats['success_cases'] / self.stats['total_cases'] * 100) if self.stats['total_cases'] > 0 else 0
        logger.info(f"成功率: {success_rate:.2f}%")
        logger.info("=" * 80)

    def close(self):
        """關閉資料庫連線"""
        self.mssql_conn.close()
        self.pg_conn.close()


# ========== 主程式 ==========

def main():
    """主程式入口"""

    # MSSQL 連線參數
    mssql_host = "host.docker.internal"
    mssql_user = "SA"
    mssql_password = "YourStrong!Passw0rd"
    mssql_database = "dryfarm"

    # PostgreSQL 連線字串
    pg_conn_str = "postgresql://{user}:{password}@{host}:{port}/{dbname}".format(
        user=os.getenv("POSTGRES_USER", "hello_fastapi"),
        password=os.getenv("POSTGRES_PASSWORD", "hello_fastapi"),
        host="db",  # Docker network
        port="5432",
        dbname=os.getenv("POSTGRES_DB", "hello_fastapi_dev")
    )

    print("=" * 80)
    print("完整對齊舊版 SQL 的遷移配置")
    print("=" * 80)
    print(f"MSSQL: {mssql_host}:1433 / {mssql_database}")
    print(f"PostgreSQL: db:5432 / {os.getenv('POSTGRES_DB', 'hello_fastapi_dev')}")
    print("=" * 80)

    # 執行遷移
    migrator = LegacyGrantMigration(
        mssql_host=mssql_host,
        mssql_user=mssql_user,
        mssql_password=mssql_password,
        mssql_database=mssql_database,
        pg_conn_str=pg_conn_str
    )

    try:
        # 測試模式：只遷移 10 筆（民國 105 年以後）
        migrator.migrate(limit=100, year_from=105)

        # 正式遷移：所有資料（民國 100 年以後）
        # migrator.migrate(year_from=100)

    finally:
        migrator.close()


if __name__ == "__main__":
    main()
