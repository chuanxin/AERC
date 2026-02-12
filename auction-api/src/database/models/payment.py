from tortoise import fields, models


class Payment(models.Model):
    id = fields.IntField(pk=True)
    auction = fields.ForeignKeyField("models.Auction", related_name="payments")
    buyer = fields.ForeignKeyField("models.User", related_name="payments_made")
    seller = fields.ForeignKeyField("models.User", related_name="payments_received")
    amount = fields.DecimalField(max_digits=12, decimal_places=2)
    platform_fee = fields.DecimalField(max_digits=10, decimal_places=2)
    # pending | paid | refunded | failed
    status = fields.CharField(max_length=20, default="pending")
    payment_method = fields.CharField(max_length=50, null=True)
    gateway_tx_id = fields.CharField(max_length=200, null=True)
    paid_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "payments"
