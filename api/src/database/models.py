from tortoise import fields, models


class Users(models.Model):
    """系統使用者資料表"""
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=20, unique=True, description="使用者帳號")
    full_name = fields.CharField(max_length=50, null=True, description="使用者姓名")
    email = fields.CharField(max_length=255, null=True, description="電子郵件")
    password = fields.CharField(max_length=128, null=True, description="密碼")

    office = fields.ForeignKeyField("models.Offices", related_name="user", null=True, description="所屬單位/管理處")
    job_title = fields.CharField(max_length=50, null=True, description="職稱")

    is_active = fields.BooleanField(default=True, description="是否啟用")
    role = fields.CharField(max_length=50, default="user", description="角色: admin, manager, user 等")
    permissions = fields.JSONField(null=True, description="特定權限設定(JSON格式)")
    last_login = fields.DatetimeField(null=True, description="最後登入時間")

    created_at = fields.DatetimeField(auto_now_add=True, description="建立時間")
    modified_at = fields.DatetimeField(auto_now=True, description="修改時間")

    class Meta:
        table = "users"
        table_description = "使用者資料表"
    
    def __str__(self):
        return f"{self.username} ({self.full_name})"
    
# class Notes(models.Model):
#     id = fields.IntField(pk=True)
#     title = fields.CharField(max_length=225)
#     content = fields.TextField()
#     author = fields.ForeignKeyField("models.Users", related_name="note")
#     created_at = fields.DatetimeField(auto_now_add=True)
#     modified_at = fields.DatetimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.title}, {self.author_id} on {self.created_at}"
    
class Offices(models.Model):
    """單位/管理處資料表"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True, description="單位名稱")
    short_name = fields.CharField(max_length=10, unique=True, description="單位縮寫")
    code = fields.CharField(max_length=10, unique=True, description="單位代碼")
    
    class Meta:
        table = "offices"
        table_description = "單位/管理處資料表"
    
    def __str__(self):
        return self.name
    

class Grants(models.Model):
    """補助申請案件資料表"""
    id = fields.IntField(pk=True)
    sn = fields.IntField(description="流水號，每年每管理處內唯一")
    case_number = fields.CharField(max_length=20, description="案件編號")
    year = fields.IntField(description="申請年度")
    
    # 申請人資訊
    applicant_name = fields.CharField(max_length=50, description="申請人姓名")
    applicant_id = fields.CharField(max_length=10, description="申請人身分證字號")
    applicant_phone = fields.CharField(max_length=20, description="申請人電話")
    
    # 申請人地址
    # county = fields.ForeignKeyField("models.County", related_name="grant", description="縣市")
    # town = fields.ForeignKeyField("models.Town", related_name="grant", description="鄉鎮市區")
    # village = fields.ForeignKeyField("models.Village", related_name="grant", null=True, description="村里")
    address = fields.CharField(max_length=255, description="詳細地址")
    
    # 管理處與承辦人
    office = fields.ForeignKeyField("models.Offices", related_name="grant", null=True, description="管理處")
    manager = fields.CharField(max_length=50, description="承辦人姓名")
    
    # 申請、收件日期
    received_date = fields.DateField(description="收件日期")
    received_time = fields.TimeField(description="收件時間")
    
    # 案件狀態
    status = fields.CharField(max_length=20, default="draft", description="案件狀態: draft, submitted, reviewing, approved, rejected, completed")
    status_detail = fields.CharField(max_length=50, null=True, description="狀態詳情")
    current_step = fields.IntField(default=1, description="目前步驟")
    
    # 時間戳記
    created_at = fields.DatetimeField(auto_now_add=True, description="建立時間")
    modified_at = fields.DatetimeField(auto_now=True, description="修改時間")
    created_by = fields.ForeignKeyField("models.Users", related_name="created_grants", description="建立者")
    modified_by = fields.ForeignKeyField("models.Users", related_name="modified_grants", description="修改者")
    
    class Meta:
        table = "grants"
        table_description = "補助申請案件資料表"
        unique_together = ("year", "office_id", "sn")
    
    @classmethod
    async def generate_sn(cls, year: int, office_id: int) -> int:
        """
        取得下一個流水號
        :param year: 申請年度
        :param office_id: 管理處ID
        :return: 下一個流水號
        """
        key = (year, office_id)

        last_grant = await cls.filter(year=year, office_id=office_id).order_by("-sn").first()
        latest_sn = last_grant.sn if last_grant else 0

        # 更新類別內的 SN 記錄
        cls.sn_registry[key] = latest_sn + 1
        return cls.sn_registry[key]
    
    def generate_case_number(self):
        """根據 year + office_id + SN 產生完整案件編號"""
        return f"{self.year}-{self.office_id.id}-{str(self.sn).zfill(4)}"

    async def save(self, *args, **kwargs):
        """在存入資料時，自動產生 SN 與 case_number"""
        if not self.sn:  # 如果 SN 尚未設定，則自動產生
            self.sn = await self.generate_sn(self.year, self.office_id.id)
        self.case_number = self.generate_case_number()  # 確保 case_number 正確
        await super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.case_number} - {self.applicant_name}"