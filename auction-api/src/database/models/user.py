from tortoise import fields, models


class User(models.Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255, unique=True)
    username = fields.CharField(max_length=100, unique=True)
    password_hash = fields.CharField(max_length=255)
    role = fields.CharField(max_length=20, default="buyer")  # buyer | seller | admin
    is_active = fields.BooleanField(default=True)
    is_verified = fields.BooleanField(default=False)
    avatar_url = fields.CharField(max_length=500, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "users"


class SellerProfile(models.Model):
    id = fields.IntField(pk=True)
    user = fields.OneToOneField("models.User", related_name="seller_profile")
    display_name = fields.CharField(max_length=200)
    description = fields.TextField(null=True)
    rating = fields.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_sales = fields.IntField(default=0)
    verified_at = fields.DatetimeField(null=True)

    class Meta:
        table = "seller_profiles"
