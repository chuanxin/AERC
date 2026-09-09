"""042 智慧灌溉入口平台 SSO 整合：建立入口身分 ↔ AERC 帳號對應表。

無資料回填——本表從空表開始，對應關係於功能上線後逐一產生。

**一對一由資料庫層保證，兩個方向都要**：
  external_id UNIQUE  → 一個入口身分只能對應一個 AERC 帳號
  user_id     UNIQUE  → 一個 AERC 帳號只能被一個入口身分對應
應用層的預檢只負責提供友善訊息；並發競態下預檢會漏，約束才是真正的防線。

**on_delete=CASCADE 的理由**：DELETE /users/{id} 是硬刪除（crud/users.py:45）。
帳號被刪除後殘留的對應關係會讓下一個持有該入口身分的請求指向不存在的帳號，
CASCADE 使對應關係隨帳號消滅，不留孤兒。

⚠️ 編號說明：041-fix-permission-authz 的 plan.md 也宣告使用編號 77
（77_..._add_audit_target_username.py）。041 於本 migration 建立時（2026-09-09）
尚未實作、無分支，故 042 取用 77；041 實作時請改用 78。
"""

from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "sso_identities" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "external_id" VARCHAR(64) NOT NULL UNIQUE,
    "bound_method" VARCHAR(13) NOT NULL,
    "bound_at" TIMESTAMPTZ NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "bound_by_id" INT REFERENCES "users" ("id") ON DELETE SET NULL,
    "user_id" INT NOT NULL UNIQUE REFERENCES "users" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "sso_identities"."external_id" IS '入口平台的帳號識別';
COMMENT ON COLUMN "sso_identities"."bound_method" IS '對應關係的建立方式';
COMMENT ON COLUMN "sso_identities"."bound_at" IS '對應關係建立時間（UTC）';
COMMENT ON COLUMN "sso_identities"."bound_by_id" IS '執行者，僅 admin_rebound 時有值';
COMMENT ON COLUMN "sso_identities"."user_id" IS '對應的 AERC 帳號';
COMMENT ON TABLE "sso_identities" IS '入口身分與 AERC 帳號對應表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "sso_identities";"""
