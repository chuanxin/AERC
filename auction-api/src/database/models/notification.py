from tortoise import fields, models


class Notification(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="notifications")
    # bid_outbid | auction_won | auction_ended | payment_received
    type = fields.CharField(max_length=50)
    title = fields.CharField(max_length=200)
    body = fields.TextField()
    is_read = fields.BooleanField(default=False)
    reference_id = fields.IntField(null=True)  # auction_id or payment_id
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "notifications"
