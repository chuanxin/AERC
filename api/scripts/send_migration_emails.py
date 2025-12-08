r"""
批次發送帳號轉移驗證信

用法:
    # 開發環境
    cd /Users/cxin/dev/AERC
    python api/scripts/send_migration_emails.py [--dry-run] [--limit N]

    # 生產環境
    cd C:\AERC\AERC-Deploy
    runtime\.venv\Scripts\python.exe app\api\scripts\send_migration_emails.py [--dry-run] [--limit N]

參數:
    --dry-run: 測試模式，僅列出符合條件的使用者，不實際發送
    --limit N: 限制發送數量（測試用）
    --env-file PATH: 指定 .env 文件路徑（可選，預設自動偵測）

篩選條件:
    - is_active = False
    - email IS NOT NULL AND email != ''
    - email_verified = False
"""

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
# Tortoise, Models, EmailService 等需要在載入 .env 後才能 import


def load_env_file(env_path: Path = None):
    """
    載入 .env 文件中的環境變數

    Args:
        env_path: .env 文件路徑，若未指定則自動搜尋

    Note:
        在 Docker 環境中，環境變數已透過 docker-compose.yml 載入，
        此函數會偵測並跳過載入。
    """
    # 檢查是否已有必要的環境變數（Docker 環境）
    required_vars = [
        "DATABASE_URL",
        "MAIL_USERNAME",
        "MAIL_PASSWORD",
        "MAIL_SERVER",
        "FRONTEND_URL"
    ]

    existing_vars = [var for var in required_vars if os.environ.get(var)]
    if len(existing_vars) == len(required_vars):
        print("[INFO] 環境變數已存在（Docker 環境），跳過載入 .env")
        return True

    if env_path is None:
        # 自動偵測 .env 位置
        # 1. 檢查 api 目錄的父目錄（開發環境: AERC/.env）
        dev_env = api_dir.parent / ".env"
        # 2. 檢查生產環境路徑（C:\AERC\AERC-Deploy\.env）
        if "AERC-Deploy" in str(api_dir):
            # 生產環境: app/api -> AERC-Deploy
            prod_env = api_dir.parent.parent / ".env"
        else:
            prod_env = None

        # 優先使用生產環境
        if prod_env and prod_env.exists():
            env_path = prod_env
        elif dev_env.exists():
            env_path = dev_env
        else:
            print(f"[WARN] 找不到 .env 文件")
            print(f"  嘗試的路徑:")
            print(f"    - {dev_env}")
            if prod_env:
                print(f"    - {prod_env}")
            print(f"  請確保環境變數已設定或使用 --env-file 參數指定路徑")
            return False

    if not env_path.exists():
        print(f"[ERROR] .env 文件不存在: {env_path}")
        return False

    print(f"[INFO] 載入環境變數: {env_path}")

    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                # 跳過空行和註解
                if not line or line.startswith('#'):
                    continue

                # 解析 KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()

                    # 移除引號
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    # 只設定尚未存在的環境變數（不覆蓋已設定的）
                    if key not in os.environ:
                        os.environ[key] = value

        print(f"[OK] 環境變數載入成功")

        # 驗證必要的環境變數（required_vars 已在函數開頭定義）
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        if missing_vars:
            print(f"[WARN] 缺少以下環境變數: {', '.join(missing_vars)}")
            return False

        return True

    except Exception as e:
        print(f"[ERROR] 載入 .env 文件失敗: {e}")
        return False


async def main(dry_run: bool = False, limit: int = None):
    """
    主程式：批次發送帳號轉移驗證信

    Args:
        dry_run: 是否為測試模式
        limit: 限制發送數量
    """
    # 在函數內部 import（確保環境變數已載入）
    from tortoise import Tortoise
    from src.database.models import Users
    from src.services.email_service import EmailService
    from src.database.config import TORTOISE_ORM

    # 初始化資料庫連接
    print("[INFO] 正在連接資料庫...")
    await Tortoise.init(config=TORTOISE_ORM)
    print("[OK] 資料庫連接成功\n")

    # 查詢符合條件的使用者
    print("[INFO] 查詢待轉移的帳號...")
    query = Users.filter(
        is_active=False,
        email_verified=False
    ).exclude(
        email=""  # 排除空字串
    ).prefetch_related('office')  # 預先載入 office 關聯

    if limit:
        query = query.limit(limit)

    users = await query.all()

    print(f"[INFO] 找到 {len(users)} 位待轉移帳號的使用者\n")

    if len(users) == 0:
        print("[WARN] 沒有符合條件的使用者，程式結束")
        await Tortoise.close_connections()
        return

    # 顯示使用者清單
    print("=" * 80)
    print(f"{'序號':<6} {'帳號':<15} {'姓名':<15} {'Email':<30} {'單位':<20}")
    print("=" * 80)
    for idx, user in enumerate(users, 1):
        office_name = user.office.short_name if user.office else "無"
        print(f"{idx:<6} {user.username:<15} {user.full_name or '-':<15} {user.email:<30} {office_name:<20}")
    print("=" * 80)
    print()

    if dry_run:
        print("[WARN] DRY-RUN 模式，未發送任何郵件")
        print("[TIP] 若要實際發送，請移除 --dry-run 參數")
        await Tortoise.close_connections()
        return

    # 確認是否繼續
    confirm = input(f"\n[WARN] 即將發送 {len(users)} 封郵件，是否繼續？ (yes/no): ")
    if confirm.lower() not in ['yes', 'y']:
        print("[CANCEL] 使用者取消操作")
        await Tortoise.close_connections()
        return

    # 發送郵件
    print(f"\n[INFO] 開始發送郵件...\n")
    email_service = EmailService()
    success_count = 0
    failed_count = 0
    failed_users = []

    for idx, user in enumerate(users, 1):
        try:
            print(f"[{idx}/{len(users)}] 正在發送給 {user.email} ({user.username})...", end=" ")
            success = await email_service.send_account_migration_email(user)

            if success:
                success_count += 1
                print("[OK]")
            else:
                failed_count += 1
                failed_users.append((user.username, user.email, "發送失敗"))
                print("[FAILED]")
        except Exception as e:
            failed_count += 1
            failed_users.append((user.username, user.email, str(e)))
            print(f"[ERROR] {str(e)}")

        # 每發送 10 封休息 1 秒（避免 SMTP 限制）
        if idx % 10 == 0:
            await asyncio.sleep(1)

    # 顯示統計結果
    print("\n" + "=" * 80)
    print("[STATS] 發送統計:")
    print(f"  - 成功: {success_count}")
    print(f"  - 失敗: {failed_count}")
    print(f"  - 總計: {len(users)}")
    print("=" * 80)

    # 顯示失敗清單
    if failed_users:
        print("\n[FAILED] 失敗清單:")
        print("-" * 80)
        for username, email, error in failed_users:
            print(f"  {username} ({email}) - {error}")
        print("-" * 80)

    # 關閉資料庫連接
    await Tortoise.close_connections()
    print("\n[OK] 程式執行完成")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="批次發送帳號轉移驗證信",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  開發環境:
    # 測試模式（不實際發送）
    python api/scripts/send_migration_emails.py --dry-run

    # 測試模式，只列出前 5 位使用者
    python api/scripts/send_migration_emails.py --dry-run --limit 5

    # 實際發送給所有符合條件的使用者
    python api/scripts/send_migration_emails.py

  生產環境:
    # 測試模式
    cd C:\\AERC\\AERC-Deploy
    runtime\\.venv\\Scripts\\python.exe app\\api\\scripts\\send_migration_emails.py --dry-run

    # 實際發送（限制 10 位測試）
    runtime\\.venv\\Scripts\\python.exe app\\api\\scripts\\send_migration_emails.py --limit 10

    # 指定 .env 路徑
    runtime\\.venv\\Scripts\\python.exe app\\api\\scripts\\send_migration_emails.py --env-file C:\\AERC\\AERC-Deploy\\.env
        """
    )
    parser.add_argument("--dry-run", action="store_true", help="測試模式，不實際發送郵件")
    parser.add_argument("--limit", type=int, help="限制發送數量（測試用）")
    parser.add_argument("--env-file", type=str, help="指定 .env 文件路徑（可選）")
    args = parser.parse_args()

    # 載入環境變數
    env_file_path = Path(args.env_file) if args.env_file else None
    if not load_env_file(env_file_path):
        print("\n[ERROR] 環境變數載入失敗，無法繼續執行")
        print("[TIP] 請確認 .env 文件存在，或使用 --env-file 參數指定路徑")
        sys.exit(1)

    print()  # 空行分隔
    asyncio.run(main(dry_run=args.dry_run, limit=args.limit))
