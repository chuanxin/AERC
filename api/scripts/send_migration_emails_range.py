import asyncio
import argparse
import os
import sys
from pathlib import Path

# 設定 Python 路徑以便 import 專案模組
script_dir = Path(__file__).resolve().parent
api_dir = script_dir.parent
sys.path.insert(0, str(api_dir))

# NOTE: 不要在這裡 import 需要環境變數的模組

def load_env_file(env_path: Path = None):
    # ... (這部分保持原本的邏輯不變，為了節省篇幅省略顯示) ...
    # 檢查是否已有必要的環境變數（Docker 環境）
    required_vars = ["DATABASE_URL", "MAIL_USERNAME", "MAIL_PASSWORD", "MAIL_SERVER", "FRONTEND_URL"]
    existing_vars = [var for var in required_vars if os.environ.get(var)]
    if len(existing_vars) == len(required_vars):
        return True
    
    if env_path is None:
        dev_env = api_dir.parent / ".env"
        if "AERC-Deploy" in str(api_dir):
            prod_env = api_dir.parent.parent / ".env"
        else:
            prod_env = None
        if prod_env and prod_env.exists():
            env_path = prod_env
        elif dev_env.exists():
            env_path = dev_env
        else:
            return False

    if not env_path.exists():
        return False

    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line: continue
                key, value = line.split('=', 1)
                if key.strip() not in os.environ:
                    os.environ[key.strip()] = value.strip().strip("'").strip('"')
        return True
    except Exception:
        return False


async def main(dry_run: bool = False, limit: int = None, id_range: list = None):
    """
    Args:
        id_range: [start_id, end_id] 包含起始與結束
    """
    from tortoise import Tortoise
    from src.database.models import Users
    from src.services.email_service import EmailService
    from src.database.config import TORTOISE_ORM

    print("[INFO] 正在連接資料庫...")
    await Tortoise.init(config=TORTOISE_ORM)
    print("[OK] 資料庫連接成功\n")

    print("[INFO] 查詢待轉移的帳號...")
    
    # 1. 基礎篩選條件
    query = Users.filter(
        is_active=False,
        email_verified=False
    ).exclude(
        email=""
    )

    # 2. 加入 ID 範圍篩選 (如果有指定)
    if id_range:
        start_id, end_id = id_range
        print(f"[FILTER] 指定 ID 範圍: {start_id} ~ {end_id}")
        # gte = Greater Than or Equal (>=), lte = Less Than or Equal (<=)
        query = query.filter(id__gte=start_id, id__lte=end_id)

    # 加入排序與 Limit
    query = query.order_by('id')
    
    if limit:
        query = query.limit(limit)

    users = await query.all()

    print(f"[INFO] 找到 {len(users)} 位符合條件的使用者\n")

    if len(users) == 0:
        print("[WARN] 沒有符合條件的使用者，程式結束")
        await Tortoise.close_connections()
        return

    # 顯示使用者清單
    print("=" * 90)
    print(f"{'序號':<6} {'ID':<6} {'帳號':<15} {'姓名':<15} {'Email':<30} {'單位':<20}")
    print("=" * 90)
    for idx, user in enumerate(users, 1):
        # 為了安全，檢查 user 是否有 office 關聯，避免報錯
        await user.fetch_related('office')
        office_name = user.office.short_name if user.office else "無"
        print(f"{idx:<6} {user.id:<6} {user.username:<15} {user.full_name or '-':<15} {user.email:<30} {office_name:<20}")
    print("=" * 90)
    print()

    if dry_run:
        print("[WARN] DRY-RUN 模式，未發送任何郵件")
        await Tortoise.close_connections()
        return

    confirm = input(f"\n[WARN] 即將發送 {len(users)} 封郵件，是否繼續？ (yes/no): ")
    if confirm.lower() not in ['yes', 'y']:
        print("[CANCEL] 使用者取消操作")
        await Tortoise.close_connections()
        return

    # 發送郵件邏輯
    print(f"\n[INFO] 開始發送郵件...\n")
    email_service = EmailService()
    success_count = 0
    failed_count = 0

    for idx, user in enumerate(users, 1):
        try:
            print(f"[{idx}/{len(users)}] ID:{user.id} 發送給 {user.email}...", end=" ")
            success = await email_service.send_account_migration_email(user)
            if success:
                success_count += 1
                print("[OK]")
            else:
                failed_count += 1
                print("[FAILED]")
        except Exception as e:
            failed_count += 1
            print(f"[ERROR] {str(e)}")
        
        if idx % 10 == 0: await asyncio.sleep(1)

    print(f"\n[STATS] 成功: {success_count}, 失敗: {failed_count}")
    await Tortoise.close_connections()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="批次發送帳號轉移驗證信")
    
    parser.add_argument("--dry-run", action="store_true", help="測試模式")
    parser.add_argument("--limit", type=int, help="限制數量")
    parser.add_argument("--env-file", type=str, help=".env 路徑")
    
    # 新增 Range 參數：接收兩個整數 (nargs=2)
    parser.add_argument("--range", type=int, nargs=2, metavar=('START', 'END'), help="ID 範圍 (例如: --range 100 200)")

    args = parser.parse_args()

    # 載入環境變數
    env_path = Path(args.env_file) if args.env_file else None
    if not load_env_file(env_path):
        sys.exit(1)

    asyncio.run(main(
        dry_run=args.dry_run, 
        limit=args.limit, 
        id_range=args.range  # 傳入 ID 範圍
    ))