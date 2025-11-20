"""
密碼政策服務模組

實作密碼安全政策：
- 三代不重複
- 密碼歷史記錄
- 審計追蹤
"""

from typing import Optional
from src.database.models import Users, PasswordHistory
from src.auth.users import verify_password, get_password_hash


class PasswordPolicyService:
    """密碼政策服務"""

    # 政策配置
    PASSWORD_HISTORY_GENERATIONS = 3  # 三代不重複
    MAX_HISTORY_RECORDS = 10  # 最多保留 10 筆歷史記錄

    @classmethod
    async def validate_password_not_reused(
        cls,
        user_id: int,
        new_password: str,
        generations: int = PASSWORD_HISTORY_GENERATIONS
    ) -> tuple[bool, Optional[str]]:
        """
        檢查新密碼是否與最近 N 代密碼重複

        Args:
            user_id: 使用者 ID
            new_password: 新密碼（明文）
            generations: 檢查幾代（預設 3）

        Returns:
            tuple[bool, Optional[str]]: (是否可用, 錯誤訊息)
            - (True, None): 密碼可用
            - (False, "錯誤訊息"): 密碼重複
        """
        # 取得使用者當前密碼
        user = await Users.get(id=user_id)
        if user.password and verify_password(new_password, user.password):
            return False, "新密碼不得與當前密碼相同"

        # 取得最近 N 代歷史密碼
        recent_passwords = await PasswordHistory.filter(
            user_id=user_id
        ).order_by("-changed_at").limit(generations)

        # 檢查是否與任一歷史密碼相同
        for idx, history in enumerate(recent_passwords, 1):
            if verify_password(new_password, history.password_hash):
                return False, f"新密碼不得與最近 {generations} 次使用過的密碼相同"

        return True, None

    @classmethod
    async def record_password_change(
        cls,
        user_id: int,
        old_password_hash: str,
        change_method: str = "password_reset",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> None:
        """
        記錄密碼變更歷史

        Args:
            user_id: 使用者 ID
            old_password_hash: 舊密碼的 hash
            change_method: 變更方式 (password_reset, user_change, admin_reset)
            ip_address: 來源 IP
            user_agent: User Agent
        """
        # 創建歷史記錄
        await PasswordHistory.create(
            user_id=user_id,
            password_hash=old_password_hash,
            change_method=change_method,
            changed_by_ip=ip_address,
            user_agent=user_agent
        )

        # 清理過期記錄（保留最近 N 筆）
        await cls.cleanup_old_history(user_id, keep=cls.MAX_HISTORY_RECORDS)

    @classmethod
    async def cleanup_old_history(
        cls,
        user_id: int,
        keep: int = MAX_HISTORY_RECORDS
    ) -> int:
        """
        清理過期的密碼歷史記錄

        Args:
            user_id: 使用者 ID
            keep: 保留最近幾筆記錄

        Returns:
            int: 刪除的記錄數
        """
        # 取得所有歷史記錄（按時間倒序）
        all_history = await PasswordHistory.filter(
            user_id=user_id
        ).order_by("-changed_at").all()

        # 如果記錄數超過保留數量，刪除舊記錄
        if len(all_history) > keep:
            records_to_delete = all_history[keep:]
            delete_ids = [record.id for record in records_to_delete]

            deleted_count = await PasswordHistory.filter(
                id__in=delete_ids
            ).delete()

            return deleted_count

        return 0

    @classmethod
    async def change_password(
        cls,
        user_id: int,
        new_password: str,
        change_method: str = "password_reset",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        generations: int = PASSWORD_HISTORY_GENERATIONS
    ) -> tuple[bool, Optional[str]]:
        """
        變更密碼（包含三代不重複檢查和歷史記錄）

        Args:
            user_id: 使用者 ID
            new_password: 新密碼（明文）
            change_method: 變更方式
            ip_address: 來源 IP
            user_agent: User Agent
            generations: 檢查幾代不重複

        Returns:
            tuple[bool, Optional[str]]: (是否成功, 錯誤訊息)
        """
        # 1. 檢查三代不重複
        is_valid, error_msg = await cls.validate_password_not_reused(
            user_id, new_password, generations
        )
        if not is_valid:
            return False, error_msg

        # 2. 取得使用者和舊密碼
        user = await Users.get(id=user_id)
        old_password_hash = user.password

        # 3. 更新為新密碼
        user.password = get_password_hash(new_password)
        await user.save()

        # 4. 記錄歷史（只在有舊密碼時記錄）
        if old_password_hash:
            await cls.record_password_change(
                user_id=user_id,
                old_password_hash=old_password_hash,
                change_method=change_method,
                ip_address=ip_address,
                user_agent=user_agent
            )

        return True, None

    @classmethod
    async def get_password_history_count(cls, user_id: int) -> int:
        """
        取得使用者密碼歷史記錄數量

        Args:
            user_id: 使用者 ID

        Returns:
            int: 歷史記錄數量
        """
        return await PasswordHistory.filter(user_id=user_id).count()
