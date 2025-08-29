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
    }
}