"""041：security_audit_logs 新增 target_username（被影響者帳號名稱）。

為什麼需要：`resource_id` 只存數字 id，而 `DELETE /users/{id}` 是硬刪除
（routes/users.py → crud/users.py 的 `Users.filter(id=...).delete()`）。
帳號一刪，稽核紀錄就只剩一個無法還原的孤兒數字，與稽核日誌「資源被刪除後
仍應保留完整軌跡」的設計意圖直接牴觸（FR-013）。

欄位形狀沿用 TD-012b 已處方的設計（varchar(20)，與 actor_username 對稱），
本次成為它的第一個使用者；日後稽核 middleware 上線時改為統一填入即可。

編號為 78 而非 aerich 自動產生的 77：77 已被 042 的
77_20260909031500_add_sso_identities.py 佔用且已套用到 dev DB。
本 migration 為手寫，未經 `aerich migrate` 產生。

nullable 且不建索引：既有 30 個稽核呼叫點不傳此參數、寫入 NULL，行為完全不變；
FR-013 要的是「可辨識」而非「可高效查詢」。
"""

from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE security_audit_logs ADD COLUMN target_username VARCHAR(20);
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE security_audit_logs DROP COLUMN target_username;
    """
