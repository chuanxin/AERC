from tortoise import fields, models


class Category(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    parent = fields.ForeignKeyField("models.Category", related_name="children", null=True)
    slug = fields.CharField(max_length=100, unique=True)
    sort_order = fields.IntField(default=0)

    class Meta:
        table = "categories"


class Auction(models.Model):
    id = fields.IntField(pk=True)
    seller = fields.ForeignKeyField("models.User", related_name="auctions")
    title = fields.CharField(max_length=300)
    description = fields.TextField(null=True)
    category = fields.ForeignKeyField("models.Category", related_name="auctions", null=True)

    starting_price = fields.DecimalField(max_digits=12, decimal_places=2)
    current_price = fields.DecimalField(max_digits=12, decimal_places=2)
    reserve_price = fields.DecimalField(max_digits=12, decimal_places=2, null=True)
    bid_increment = fields.DecimalField(max_digits=10, decimal_places=2)
    bid_count = fields.IntField(default=0)

    # draft | active | ended | sold | cancelled
    status = fields.CharField(max_length=20, default="draft")

    start_time = fields.DatetimeField()
    end_time = fields.DatetimeField()
    auto_extend = fields.BooleanField(default=True)
    extend_minutes = fields.IntField(default=5)

    winner = fields.ForeignKeyField("models.User", related_name="won_auctions", null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "auctions"


class AuctionImage(models.Model):
    id = fields.IntField(pk=True)
    auction = fields.ForeignKeyField("models.Auction", related_name="images", on_delete=fields.CASCADE)
    url = fields.CharField(max_length=500)
    sort_order = fields.IntField(default=0)
    is_primary = fields.BooleanField(default=False)

    class Meta:
        table = "auction_images"
