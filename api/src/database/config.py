import os

TORTOISE_ORM = {
    "connections": {"default": os.environ.get("DATABASE_URL")},
    "apps": {
        "models": {
            "models": [
                "src.database.models", "src.database.geo_models", "src.database.audit_models", "aerich.models"
            ],
            "default_connection": "default"
        }
    },
    # 使用預設的 timezone-aware datetime，確保資料庫一致性
    # 密碼原則的日期計算在服務層局部處理（轉 naive 後計算）
    "use_tz": True,
    "timezone": "UTC"
}