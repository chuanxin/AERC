from src.config.settings import DATABASE_URL

TORTOISE_ORM = {
    "connections": {
        "default": DATABASE_URL,
    },
    "apps": {
        "models": {
            "models": [
                "src.database.models.user",
                "src.database.models.auction",
                "src.database.models.bid",
                "src.database.models.payment",
                "src.database.models.notification",
                "src.database.models.watchlist",
                "aerich.models",
            ],
            "default_connection": "default",
        },
    },
    "timezone": "Asia/Taipei",
}
