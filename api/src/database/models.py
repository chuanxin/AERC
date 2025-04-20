from tortoise import fields, models


class Users(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=20, unique=True)
    full_name = fields.CharField(max_length=50, null=True)
    email = fields.CharField(max_length=255, null=True)
    password = fields.CharField(max_length=128, null=True)

    is_active = fields.BooleanField(default=True)
    role = fields.CharField(max_length=50, default="user")  # 角色: admin, manager, user 等
    department = fields.CharField(max_length=100, null=True)  # 部門/單位
    permissions = fields.JSONField(null=True)  # 特定權限設定(JSON格式)

    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)


class Notes(models.Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=225)
    content = fields.TextField()
    author = fields.ForeignKeyField("models.Users", related_name="note")
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}, {self.author_id} on {self.created_at}"