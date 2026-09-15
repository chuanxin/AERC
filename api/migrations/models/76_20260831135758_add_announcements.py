"""040 公告（最新消息）系統化管理：建立兩張資料表與初始公告類型。

seed 刻意**不指定 id**：以顯式主鍵插入會使 announcement_types_id_seq 不前進，
第一次經 API 新增類型時 nextval 回傳 1、與既有列撞 PK——那正是 AERC-0417
（users_id_seq 落後造成 PK 衝突被誤判為 email 重複）的同型陷阱。
匯入腳本（scripts/import_announcements.py）需要對應公告類型時以 name 查 id，
不得假設它是 1。

初始四種類型中，「系統公告」「停機公告」「其他」的顏色逐值取自
dry-farm/src/components/Dashboard.vue 的 getTypeColor()——使用者對
「藍色＝系統公告、橘色＝停機」已有辨識習慣，換色即為破壞使用者空間。
"""

from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "announcement_types" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(20) NOT NULL UNIQUE,
    "color" VARCHAR(30) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "announcement_types"."name" IS '類型名稱（例：系統公告）';
COMMENT ON COLUMN "announcement_types"."color" IS '列表標示顏色（Vuetify 色名或 hex）';
COMMENT ON TABLE "announcement_types" IS '公告類型';

CREATE TABLE IF NOT EXISTS "announcements" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(200) NOT NULL,
    "content_markdown" TEXT,
    "publish_date" DATE NOT NULL,
    "status" VARCHAR(20) NOT NULL DEFAULT 'draft',
    "is_pinned" BOOL NOT NULL DEFAULT False,
    "published_at" TIMESTAMPTZ,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_by_id" INT REFERENCES "users" ("id") ON DELETE SET NULL,
    "type_id" INT NOT NULL REFERENCES "announcement_types" ("id") ON DELETE RESTRICT
);
COMMENT ON COLUMN "announcements"."content_markdown" IS '詳細內容的 Markdown 原文——唯一儲存形式，呈現用 HTML 於讀取時渲染';
COMMENT ON COLUMN "announcements"."publish_date" IS '發布日期（顯示與排序用；前端以民國年月日呈現）';
COMMENT ON COLUMN "announcements"."created_by_id" IS '建立者；SET_NULL 不用 CASCADE——刪帳號不得連帶抹掉其發過的公告';
COMMENT ON COLUMN "announcements"."type_id" IS '公告類型；RESTRICT 為「使用中的類型不可刪」的資料庫層保證';
COMMENT ON TABLE "announcements" IS '公告（最新消息）';

CREATE INDEX IF NOT EXISTS "idx_announcements_list"
    ON "announcements" ("status", "is_pinned" DESC, "publish_date" DESC, "id" DESC);

INSERT INTO "announcement_types" ("name", "color") VALUES
    ('系統公告', 'blue'),
    ('停機公告', 'deep-orange'),
    ('宣導', 'teal'),
    ('其他', 'grey')
ON CONFLICT ("name") DO NOTHING;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "announcements";
DROP TABLE IF EXISTS "announcement_types";"""
