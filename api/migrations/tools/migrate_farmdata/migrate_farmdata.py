import csv
import os
import psycopg2
from psycopg2.extras import execute_values, Json
from dotenv import load_dotenv
from typing import List, Dict, Any, Tuple
import logging
from datetime import datetime

# Load environment variables from .env file in the current directory
# Assumes the script is run from the AERC project root
load_dotenv()

# 設置詳細的日誌記錄
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MigrationReporter:
    """遷移報告器 - 追蹤成功和失敗的記錄"""
    
    def __init__(self):
        self.total_rows = 0
        self.successful_rows = 0
        self.failed_rows = []
        self.skipped_rows = []
        self.validation_errors = []
        self.database_errors = []
        
    def add_total_row(self):
        """增加總行數"""
        self.total_rows += 1
        
    def add_successful_row(self):
        """增加成功行數"""
        self.successful_rows += 1
        
    def add_failed_row(self, row_data: Dict, error_type: str, error_message: str, row_number: int = None):
        """添加失敗的行"""
        self.failed_rows.append({
            'row_number': row_number,
            'row_data': row_data,
            'error_type': error_type,
            'error_message': error_message,
            'timestamp': datetime.now().isoformat()
        })
        
    def add_skipped_row(self, row_data: Dict, reason: str, row_number: int = None):
        """添加跳過的行"""
        self.skipped_rows.append({
            'row_number': row_number,
            'row_data': row_data,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        })
        
    def add_validation_error(self, field: str, value: Any, error: str, row_number: int = None):
        """添加驗證錯誤"""
        self.validation_errors.append({
            'row_number': row_number,
            'field': field,
            'value': value,
            'error': error,
            'timestamp': datetime.now().isoformat()
        })
        
    def add_database_error(self, error_message: str, affected_rows: int = None):
        """添加資料庫錯誤"""
        self.database_errors.append({
            'error_message': error_message,
            'affected_rows': affected_rows,
            'timestamp': datetime.now().isoformat()
        })
        
    def generate_report(self) -> Dict[str, Any]:
        """生成完整的遷移報告"""
        success_rate = (self.successful_rows / self.total_rows * 100) if self.total_rows > 0 else 0
        
        return {
            'summary': {
                'total_rows_processed': self.total_rows,
                'successful_rows': self.successful_rows,
                'failed_rows_count': len(self.failed_rows),
                'skipped_rows_count': len(self.skipped_rows),
                'success_rate_percentage': round(success_rate, 2),
                'validation_errors_count': len(self.validation_errors),
                'database_errors_count': len(self.database_errors)
            },
            'failed_rows': self.failed_rows,
            'skipped_rows': self.skipped_rows,
            'validation_errors': self.validation_errors,
            'database_errors': self.database_errors
        }
        
    def save_failed_data_to_csv(self, filename: str = None):
        """將失敗的資料保存到 CSV 檔案"""
        if not filename:
            filename = f'failed_migration_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            
        if not self.failed_rows and not self.skipped_rows:
            logger.info("沒有失敗或跳過的資料需要保存")
            return
            
        all_failed_data = []
        
        # 合併失敗和跳過的資料
        for failed in self.failed_rows:
            row_data = failed['row_data'].copy()
            row_data['_migration_status'] = 'FAILED'
            row_data['_error_type'] = failed['error_type']
            row_data['_error_message'] = failed['error_message']
            row_data['_row_number'] = failed['row_number']
            all_failed_data.append(row_data)
            
        for skipped in self.skipped_rows:
            row_data = skipped['row_data'].copy()
            row_data['_migration_status'] = 'SKIPPED'
            row_data['_error_type'] = 'VALIDATION'
            row_data['_error_message'] = skipped['reason']
            row_data['_row_number'] = skipped['row_number']
            all_failed_data.append(row_data)
            
        if all_failed_data:
            # 獲取所有可能的欄位名稱
            all_fieldnames = set()
            for row in all_failed_data:
                all_fieldnames.update(row.keys())
            
            fieldnames = sorted(list(all_fieldnames))
            
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(all_failed_data)
                    
                logger.info(f"失敗的資料已保存到: {filename}")
                
            except Exception as e:
                logger.error(f"保存失敗資料到 CSV 時發生錯誤: {e}")

    def save_detailed_report(self, filename: str = None):
        """保存詳細的遷移報告，包括重複記錄的統計"""
        if not filename:
            filename = f'detailed_migration_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
            
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("📊 詳細資料遷移報告\n")
                f.write("=" * 80 + "\n\n")
                
                # 總體統計
                f.write("📈 總體統計:\n")
                f.write(f"   總處理行數: {self.total_rows}\n")
                f.write(f"   成功匯入: {self.successful_rows}\n")
                f.write(f"   失敗記錄: {len(self.failed_rows)}\n")
                f.write(f"   跳過記錄: {len(self.skipped_rows)}\n")
                success_rate = (self.successful_rows / self.total_rows * 100) if self.total_rows > 0 else 0
                f.write(f"   成功率: {success_rate:.2f}%\n\n")
                
                # 跳過記錄的詳細分析
                if self.skipped_rows:
                    f.write("⏭️ 跳過記錄分析:\n")
                    skip_reasons = {}
                    for skipped in self.skipped_rows:
                        reason = skipped['reason']
                        skip_reasons[reason] = skip_reasons.get(reason, 0) + 1
                    
                    for reason, count in skip_reasons.items():
                        f.write(f"   - {reason}: {count} 筆\n")
                    f.write("\n")
                
                # 驗證錯誤統計
                if self.validation_errors:
                    f.write("⚠️ 驗證錯誤統計:\n")
                    validation_stats = {}
                    for error in self.validation_errors:
                        field = error['field']
                        validation_stats[field] = validation_stats.get(field, 0) + 1
                    
                    for field, count in validation_stats.items():
                        f.write(f"   - {field}: {count} 個錯誤\n")
                    f.write("\n")
                
                # 數據匯入落差分析
                expected_success = self.total_rows - len(self.skipped_rows) - len(self.failed_rows)
                actual_success = self.successful_rows
                discrepancy = expected_success - actual_success
                
                f.write("🔍 數據匯入落差分析:\n")
                f.write(f"   預期成功匯入: {expected_success} 筆\n")
                f.write(f"   實際成功匯入: {actual_success} 筆\n")
                f.write(f"   落差: {discrepancy} 筆\n")
                if discrepancy > 0:
                    f.write(f"   說明: 這 {discrepancy} 筆記錄可能因為唯一約束衝突而被資料庫自動跳過\n")
                f.write("\n")
                
                f.write("=" * 80 + "\n")
                
            logger.info(f"詳細報告已保存到: {filename}")
            
        except Exception as e:
            logger.error(f"保存詳細報告時發生錯誤: {e}")

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        db_url = "postgresql://{user}:{password}@{host}:{port}/{dbname}".format(
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host="localhost",
            port="5433",
            dbname=os.getenv("POSTGRES_DB")
        )
        conn = psycopg2.connect(db_url)
        logger.info("資料庫連線成功")
        return conn
    except Exception as e:
        logger.error(f"資料庫連線失敗: {e}")
        return None

def validate_row_data(row: Dict[str, str], row_number: int, reporter: MigrationReporter) -> Tuple[bool, Dict[str, Any]]:
    """驗證單行資料的有效性 - 僅檢查必要欄位存在性"""
    validation_result = {
        'is_valid': True,
        'processed_data': {},
        'errors': []
    }
    
    # 檢查必要欄位
    required_fields = ['Long', 'Lat', 'MapNo', 'Section', 'LandNo']
    missing_fields = []
    
    for field in required_fields:
        if not row.get(field) or str(row.get(field)).strip() == '':
            missing_fields.append(field)
            reporter.add_validation_error(field, row.get(field), "必要欄位缺失或為空", row_number)
    
    if missing_fields:
        validation_result['is_valid'] = False
        validation_result['errors'].append(f"缺少必要欄位: {', '.join(missing_fields)}")
        return validation_result['is_valid'], validation_result
    
    # 處理經緯度 - 只檢查格式，不檢查範圍
    try:
        longitude = float(row['Long'])
        latitude = float(row['Lat'])
        
        validation_result['processed_data']['geom'] = f"POINT({longitude} {latitude})"
        validation_result['processed_data']['longitude'] = longitude
        validation_result['processed_data']['latitude'] = latitude
            
    except (ValueError, TypeError) as e:
        reporter.add_validation_error('Long/Lat', f"{row.get('Long')}, {row.get('Lat')}", f"經緯度格式錯誤: {e}", row_number)
        validation_result['is_valid'] = False
        validation_result['errors'].append(f"經緯度格式錯誤: {e}")
        return validation_result['is_valid'], validation_result
    
    # 處理年份 - 只檢查格式，不檢查範圍
    if row.get('ApplyYear'):
        try:
            apply_year = int(row['ApplyYear'])
            validation_result['processed_data']['apply_year'] = apply_year
        except (ValueError, TypeError):
            # 年份格式錯誤不影響整體驗證，設為 None 即可
            validation_result['processed_data']['apply_year'] = None
    else:
        validation_result['processed_data']['apply_year'] = None
    
    # 處理面積數據 - 只檢查格式，不檢查範圍
    area_fields = ['FarmArea', 'BuildArea', 'FinalArea']
    meta_data = {}
    
    for field in area_fields:
        if row.get(field):
            try:
                area_value = float(row[field])
                meta_data[field.lower()] = area_value
            except (ValueError, TypeError):
                # 面積格式錯誤不影響整體驗證，設為 None 即可
                meta_data[field.lower()] = None
        else:
            meta_data[field.lower()] = None
                
    validation_result['processed_data']['meta_data'] = meta_data
    
    # 處理其他欄位
    validation_result['processed_data']['map_no'] = str(row.get('MapNo', '')).strip()
    validation_result['processed_data']['applicant_name'] = str(row.get('Name', '')).strip()
    validation_result['processed_data']['land_section'] = str(row.get('Section', '')).strip()
    validation_result['processed_data']['land_number'] = str(row.get('LandNo', '')).strip()
    validation_result['processed_data']['land_type'] = str(row.get('LandType', '')).strip()
    validation_result['processed_data']['application_status'] = str(row.get('ApplicationStatus', '')).strip()
    
    return validation_result['is_valid'], validation_result

def check_existing_records(conn, data_to_check: List[Dict]) -> set:
    """檢查哪些記錄已經存在於資料庫中"""
    if not data_to_check:
        return set()
    
    logger.info(f"開始檢查 {len(data_to_check)} 筆記錄是否已存在")
    
    existing_keys = set()
    batch_size = 1000  # 每次查詢 1000 筆記錄
    
    for i in range(0, len(data_to_check), batch_size):
        batch = data_to_check[i:i+batch_size]
        
        # 構建檢查查詢
        check_conditions = []
        check_params = []
        
        for data in batch:
            check_conditions.append(
                "(source_system = %s AND source_id = %s AND land_section = %s AND land_number = %s)"
            )
            check_params.extend([
                'legacy_farmdata',
                data['map_no'],
                data['land_section'],
                data['land_number']
            ])
        
        query = f"""
            SELECT source_system, source_id, land_section, land_number
            FROM grant_locations 
            WHERE {' OR '.join(check_conditions)}
        """
        
        try:
            with conn.cursor() as cur:
                cur.execute(query, check_params)
                existing_records = cur.fetchall()
                
                # 轉換為便於比對的格式
                for record in existing_records:
                    key = f"{record[0]}_{record[1]}_{record[2]}_{record[3]}"
                    existing_keys.add(key)
                    
            logger.info(f"批次 {i//batch_size + 1}/{(len(data_to_check) + batch_size - 1)//batch_size}: 檢查了 {len(batch)} 筆記錄")
                    
        except Exception as e:
            logger.error(f"檢查現有記錄時發生錯誤 (批次 {i//batch_size + 1}): {e}")
            # 繼續處理下一個批次，不中斷整個流程
            continue
    
    logger.info(f"檢查完成，發現 {len(existing_keys)} 筆已存在的記錄")
    return existing_keys

def migrate_farm_data(conn, reporter: MigrationReporter):
    """Migrates legacy data from FarmData.csv to the grant_locations table."""
    csv_path = "/Users/cxin/dev/gemini/FarmData.csv"
    
    if not os.path.exists(csv_path):
        error_msg = f"Error: {csv_path} not found."
        logger.error(error_msg)
        reporter.add_database_error(error_msg)
        return

    logger.info(f"開始讀取 CSV 檔案: {csv_path}")
    
    valid_data_to_insert = []
    row_number = 0
    
    try:
        with open(csv_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                row_number += 1
                reporter.add_total_row()
                
                # 驗證資料
                is_valid, validation_result = validate_row_data(row, row_number, reporter)
                
                if not is_valid:
                    reporter.add_skipped_row(
                        row, 
                        f"資料驗證失敗: {'; '.join(validation_result.get('errors', []))}", 
                        row_number
                    )
                    continue
                
                # 準備插入資料
                processed_data = validation_result['processed_data']
                
                insert_data = (
                    'legacy_farmdata',
                    processed_data['map_no'],
                    processed_data['geom'],
                    processed_data.get('apply_year'),
                    processed_data['applicant_name'],
                    processed_data['land_section'],
                    processed_data['land_number'],
                    processed_data['land_type'],
                    'legacy_imported',
                    processed_data['application_status'],
                    Json(processed_data['meta_data'])
                )
                
                valid_data_to_insert.append({
                    'insert_data': insert_data,
                    'original_row': row,
                    'row_number': row_number,
                    'processed_data': processed_data
                })
                
    except Exception as e:
        error_msg = f"讀取 CSV 檔案時發生錯誤: {e}"
        logger.error(error_msg)
        reporter.add_database_error(error_msg)
        return

    if not valid_data_to_insert:
        logger.warning("沒有有效的資料可以遷移")
        return

    logger.info(f"準備插入 {len(valid_data_to_insert)} 筆有效資料")
    
    # 由於我們在 INSERT 時使用 ON CONFLICT DO NOTHING，可以跳過預先檢查現有記錄
    # 這樣可以大幅提升處理大量資料的效率
    final_data_to_insert = valid_data_to_insert
    
    logger.info(f"跳過重複檢查，直接進行批次插入 {len(final_data_to_insert)} 筆資料")
    
    if not final_data_to_insert:
        logger.info("所有資料都已存在，沒有新資料需要插入")
        return
    
    # 批量插入資料 - 改為逐條插入以準確追蹤每筆記錄
    total_inserted = 0
    total_skipped_duplicates = 0
    
    logger.info("開始逐條插入記錄以追蹤重複資料...")
    
    for i, item in enumerate(final_data_to_insert):
        try:
            with conn.cursor() as cur:
                cur.execute("BEGIN;")
                
                # 逐條插入以準確追蹤
                cur.execute(
                    """
                    INSERT INTO grant_locations (
                        source_system, source_id, geom, apply_year, applicant_name, 
                        land_section, land_number, land_type, case_status, comment, meta_data
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (source_system, source_id, land_section, land_number) DO NOTHING
                    """,
                    item['insert_data']
                )
                
                if cur.rowcount > 0:
                    # 成功插入
                    cur.execute("COMMIT;")
                    reporter.add_successful_row()
                    total_inserted += 1
                else:
                    # 重複記錄，被跳過
                    cur.execute("ROLLBACK;")
                    reporter.add_skipped_row(
                        item['original_row'],
                        "記錄與現有資料重複（唯一約束衝突）",
                        item['row_number']
                    )
                    total_skipped_duplicates += 1
                
                # 每 1000 筆記錄顯示進度
                if (i + 1) % 1000 == 0:
                    logger.info(f"已處理 {i + 1}/{len(final_data_to_insert)} 筆記錄，成功插入 {total_inserted} 筆，跳過重複 {total_skipped_duplicates} 筆")
                    
        except Exception as e:
            try:
                with conn.cursor() as cur:
                    cur.execute("ROLLBACK;")
            except:
                pass
                
            # 檢查是否為重複鍵錯誤
            error_str = str(e).lower()
            if any(phrase in error_str for phrase in ['unique constraint', 'duplicate key', 'already exists']):
                reporter.add_skipped_row(
                    item['original_row'],
                    f"記錄與現有資料重複: {str(e)}",
                    item['row_number']
                )
                total_skipped_duplicates += 1
            else:
                # 其他類型的錯誤標記為失敗
                reporter.add_failed_row(
                    item['original_row'],
                    'DATABASE_ERROR',
                    str(e),
                    item['row_number']
                )
    
    logger.info(f"總共成功插入 {total_inserted} 筆記錄，跳過 {total_skipped_duplicates} 筆重複記錄")

def print_migration_report(report: Dict[str, Any]):
    """印出詳細的遷移報告"""
    summary = report['summary']
    
    print("\n" + "="*80)
    print("📊 資料遷移報告")
    print("="*80)
    
    print(f"📈 總體統計:")
    print(f"   總處理行數: {summary['total_rows_processed']}")
    print(f"   成功行數: {summary['successful_rows']}")
    print(f"   失敗行數: {summary['failed_rows_count']}")
    print(f"   跳過行數: {summary['skipped_rows_count']}")
    print(f"   成功率: {summary['success_rate_percentage']}%")
    print(f"   驗證錯誤數: {summary['validation_errors_count']}")
    print(f"   資料庫錯誤數: {summary['database_errors_count']}")
    
    if report['failed_rows']:
        print(f"\n❌ 失敗的記錄 ({len(report['failed_rows'])} 筆):")
        for i, failed in enumerate(report['failed_rows'][:5]):  # 只顯示前5筆
            print(f"   {i+1}. 行號 {failed['row_number']}: {failed['error_type']} - {failed['error_message']}")
        if len(report['failed_rows']) > 5:
            print(f"   ... 還有 {len(report['failed_rows']) - 5} 筆失敗記錄")
    
    if report['skipped_rows']:
        print(f"\n⏭️  跳過的記錄 ({len(report['skipped_rows'])} 筆):")
        skip_reasons = {}
        for skipped in report['skipped_rows']:
            reason = skipped['reason']
            skip_reasons[reason] = skip_reasons.get(reason, 0) + 1
        
        for reason, count in skip_reasons.items():
            print(f"   - {reason}: {count} 筆")
    
    if report['validation_errors']:
        print(f"\n⚠️  驗證錯誤統計 ({len(report['validation_errors'])} 個):")
        validation_stats = {}
        for error in report['validation_errors']:
            field = error['field']
            validation_stats[field] = validation_stats.get(field, 0) + 1
        
        for field, count in validation_stats.items():
            print(f"   - {field}: {count} 個錯誤")
    
    print("\n" + "="*80)

def main():
    """Main function to run the migration."""
    logger.info("開始執行資料遷移...")
    
    # 初始化報告器
    reporter = MigrationReporter()
    
    # 建立資料庫連線
    conn = get_db_connection()
    if not conn:
        logger.error("無法建立資料庫連線，終止遷移")
        return
    
    try:
        # 執行遷移
        migrate_farm_data(conn, reporter)
        
        # 生成報告
        report = reporter.generate_report()
        
        # 印出報告
        print_migration_report(report)
        
        # 保存失敗的資料
        reporter.save_failed_data_to_csv()
        
        # 保存詳細的遷移報告
        reporter.save_detailed_report()
        
        # 保存完整報告到 JSON 檔案
        import json
        report_filename = f'migration_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        try:
            with open(report_filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            logger.info(f"完整報告已保存到: {report_filename}")
        except Exception as e:
            logger.error(f"保存報告時發生錯誤: {e}")
        
        logger.info("資料遷移完成")
        
    finally:
        conn.close()
        logger.info("資料庫連線已關閉")

if __name__ == "__main__":
    main()