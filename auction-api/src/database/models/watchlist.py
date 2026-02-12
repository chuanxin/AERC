from tortoise import fields, models


class Watchlist(models.Model):
    user = fields.ForeignKeyField("models.User", related_name="watchlist")
    auction = fields.ForeignKeyField("models.Auction", related_name="watchers")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "watchlist"
        unique_together = (("user", "auction"),)
