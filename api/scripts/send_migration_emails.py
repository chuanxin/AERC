"""
批次發送帳號轉移驗證信

用法:
    cd /Users/cxin/dev/AERC
    python api/scripts/send_migration_emails.py [--dry-run] [--limit N]

參數:
    --dry-run: 測試模式，僅列出符合條件的使用者，不實際發送
    --limit N: 限制發送數量（測試用）

篩選條件:
    - is_active = False
    - email IS NOT NULL AND email != ''
    - email_verified = False
"""

import asyncio
import argparse
import os
import sys

# 設定 Python 路徑以便 import 專案模組
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tortoise import Tortoise
from src.database.models import Users
from src.services.email_service import EmailService
from src.database.config import TORTOISE_ORM


async def main(dry_run: bool = False, limit: int = None):
    """
    主程式：批次發送帳號轉移驗證信

    Args:
        dry_run: 是否為測試模式
        limit: 限制發送數量
    """
    # 初始化資料庫連接
    print("🔌 正在連接資料庫...")
    await Tortoise.init(config=TORTOISE_ORM)
    print("✅ 資料庫連接成功\n")

    # 查詢符合條件的使用者
    print("🔍 查詢待轉移的帳號...")
    query = Users.filter(
        is_active=False,
        email_verified=False
    ).exclude(
        email=""  # 排除空字串
    ).prefetch_related('office')  # 預先載入 office 關聯

    if limit:
        query = query.limit(limit)

    users = await query.all()

    print(f"📋 找到 {len(users)} 位待轉移帳號的使用者\n")

    if len(users) == 0:
        print("⚠️  沒有符合條件的使用者，程式結束")
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
        print("⚠️  DRY-RUN 模式，未發送任何郵件")
        print("💡 若要實際發送，請移除 --dry-run 參數")
        await Tortoise.close_connections()
        return

    # 確認是否繼續
    confirm = input(f"\n⚠️  即將發送 {len(users)} 封郵件，是否繼續？ (yes/no): ")
    if confirm.lower() not in ['yes', 'y']:
        print("❌ 使用者取消操作")
        await Tortoise.close_connections()
        return

    # 發送郵件
    print(f"\n📧 開始發送郵件...\n")
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
                print("✅ 成功")
            else:
                failed_count += 1
                failed_users.append((user.username, user.email, "發送失敗"))
                print("❌ 失敗")
        except Exception as e:
            failed_count += 1
            failed_users.append((user.username, user.email, str(e)))
            print(f"❌ 錯誤: {str(e)}")

        # 每發送 10 封休息 1 秒（避免 SMTP 限制）
        if idx % 10 == 0:
            await asyncio.sleep(1)

    # 顯示統計結果
    print("\n" + "=" * 80)
    print("📊 發送統計:")
    print(f"  ✅ 成功: {success_count}")
    print(f"  ❌ 失敗: {failed_count}")
    print(f"  📈 總計: {len(users)}")
    print("=" * 80)

    # 顯示失敗清單
    if failed_users:
        print("\n❌ 失敗清單:")
        print("-" * 80)
        for username, email, error in failed_users:
            print(f"  {username} ({email}) - {error}")
        print("-" * 80)

    # 關閉資料庫連接
    await Tortoise.close_connections()
    print("\n✅ 程式執行完成")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="批次發送帳號轉移驗證信",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  # 測試模式（不實際發送）
  python api/scripts/send_migration_emails.py --dry-run

  # 測試模式，只列出前 5 位使用者
  python api/scripts/send_migration_emails.py --dry-run --limit 5

  # 實際發送給所有符合條件的使用者
  python api/scripts/send_migration_emails.py

  # 實際發送，但限制 10 位使用者（測試用）
  python api/scripts/send_migration_emails.py --limit 10
        """
    )
    parser.add_argument("--dry-run", action="store_true", help="測試模式，不實際發送郵件")
    parser.add_argument("--limit", type=int, help="限制發送數量（測試用）")
    args = parser.parse_args()

    asyncio.run(main(dry_run=args.dry_run, limit=args.limit))
