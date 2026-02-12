from tortoise import fields, models


class Bid(models.Model):
    """Append-only bid log. Never delete bids."""

    id = fields.IntField(pk=True)
    auction = fields.ForeignKeyField("models.Auction", related_name="bids")
    user = fields.ForeignKeyField("models.User", related_name="bids")
    amount = fields.DecimalField(max_digits=12, decimal_places=2)
    is_winning = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "bids"
        indexes = [
            ("auction_id", "amount"),
        ]
