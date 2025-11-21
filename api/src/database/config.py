import os

TORTOISE_ORM = {
    "connections": {"default": os.environ.get("DATABASE_URL")},
    "apps": {
        "models": {
            "models": [
                "src.database.models", "src.database.geo_models", "aerich.models"
            ],
            "default_connection": "default"
        }
    },
    # 使用 naive datetime (UTC) 避免時區混用問題
    "use_tz": False,
    "timezone": "UTC"
}