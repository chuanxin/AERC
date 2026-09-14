"""042 US3：auth_tokens 新增 external_id（綁定票據所屬的入口身分）。

為什麼需要：綁定票據在「憑證驗證通過、查無對應關係、以電子郵件找到唯一候選帳號」時核發，
使用者隨後以帳號密碼登入、再持票據呼叫 POST /sso/bind 建立對應關係。建立對應關係需要
兩個值——候選帳號（`auth_tokens.user_id` 已有）與**入口身分**。後者在核發當下已由
憑證驗證確立，但原本的 auth_tokens 沒有任何欄位承載它，綁定端點無從得知要綁哪個入口身分。

替代方案皆已否決：
  - 塞進 token 字串本身（`uuid.external_id`）：token 會出現在網址，把入口識別暴露進
    瀏覽歷史；且讓 token 欄位同時承擔「查詢鍵」與「業務資料」兩種語意
  - 借用 user_agent 等既有欄位：語意錯置，日後必然被誤讀
  - 另建票據表：欄位與 auth_tokens 高度重疊，過期／撤銷語意得重寫一次

nullable 且不建索引：既有 token 類型不使用此欄位、寫入 NULL，行為完全不變；
綁定時以 token 值（unique）查詢，不以本欄位查詢。

長度 64 對齊 sso_identities.external_id。本 migration 為手寫。
"""

from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "auth_tokens" ADD COLUMN "external_id" VARCHAR(64);
        COMMENT ON COLUMN "auth_tokens"."external_id" IS '入口平台帳號識別（僅 sso_binding 使用）';
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "auth_tokens" DROP COLUMN "external_id";
    """
