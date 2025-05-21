from tortoise import fields, models
from enum import Enum



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

class GrantStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class GrantTypes(str, Enum):
    FARMING = "farming"
    IRRIGATION = "irrigation"
    EQUIPMENT = "equipment"
    TECHNOLOGY = "technology"
    RESEARCH = "research"
    OTHER = "other"

class Grants(models.Model):
    """補助申請案件資料表"""
    # Initialize the sn_registry
    sn_registry = {}

    id = fields.IntField(pk=True)
    sn = fields.IntField(description="流水號，每年每管理處內唯一")
    case_number = fields.CharField(max_length=20, description="案件編號")
    year = fields.IntField(description="申請年度")
    
    # 申請人資訊
    applicant_name = fields.CharField(max_length=50, description="申請人姓名")
    applicant_id = fields.CharField(max_length=10, description="申請人身分證字號")
    applicant_phone = fields.CharField(max_length=20, description="申請人電話")
    
    # 申請人地址
    county = fields.CharField(max_length=30, description="縣市")
    town = fields.CharField(max_length=30, description="鄉鎮市區")
    village = fields.CharField(max_length=30, null=True, description="村里")
    address = fields.CharField(max_length=255, description="詳細地址")
    
    # 管理處與承辦人
    # office = fields.ForeignKeyField("models.Offices", related_name="grant", null=True, description="管理處")
    office = fields.CharField(max_length=50, description="管理處名稱")
    office_id = fields.IntField(null=True, description="管理處ID", index=False)
    undertracker = fields.CharField(max_length=50, description="承辦人姓名")
    
    # 申請、收件日期
    received_date = fields.DateField(description="收件日期")
    received_time = fields.TimeField(description="收件時間")
    
    # 案件狀態
    status = fields.CharField(max_length=20, default="draft", description="案件狀態: 0:完成申請人資料, 1:完成土地資料, 2:完成灌溉調控設施, 3:完成田間管路, 4:完成現場勘查, 5:完成補助申請資料, 6:完成結案申報, 7:完成測試合格的時間, 8:完成撥款作業, 9:完成撥款, 99:駁回申請")
    status_detail = fields.CharField(max_length=50, null=True, description="狀態詳情")
    current_step = fields.IntField(default=1, description="目前步驟")
    bulletin = fields.CharField(max_length=20, null=True, description="公告狀態: 0:已受理, 1:審查中, 2:審查通過 3:結案流程 4:撥款作業 5:撥款完成")
    bulletin_sys = fields.CharField(max_length=20, null=True, description="公告狀態(系統): 0:申請人資料, 1:現場勘查, 2:補助申請資料 3:結案申報 4:測試合格的時間 5:")
    
    # 時間戳記
    created_at = fields.DatetimeField(auto_now_add=True, description="建立時間")
    modified_at = fields.DatetimeField(auto_now=True, description="修改時間")
    created_by = fields.ForeignKeyField("models.Users", related_name="created_grants", description="建立人帳號", on_delete=fields.CASCADE)
    # modified_by = fields.ForeignKeyField("models.Users", related_name="modified_grants", description="修改人帳號")
    attachments = fields.ReverseRelation["GrantAttachments"]
    comments = fields.ReverseRelation["GrantComments"]
    history = fields.ReverseRelation["GrantHistory"]
    
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
        return f"{self.year}{self.office_id}{str(self.sn).zfill(4)}"

    async def save(self, *args, **kwargs):
        """在存入資料時，自動產生 SN 與 case_number"""
        if not self.sn:  # 如果 SN 尚未設定，則自動產生
            self.sn = await self.generate_sn(self.year, self.office_id)
        self.case_number = self.generate_case_number()  # 確保 case_number 正確
        await super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.case_number} - {self.applicant_name}"
    
class GrantAttachments(models.Model):
    """補助案件附件資料表"""
    id = fields.IntField(pk=True)
    grant = fields.ForeignKeyField("models.Grants", related_name="attachments", description="所屬案件")
    file_name = fields.CharField(max_length=255, description="檔案名稱")
    file_path = fields.CharField(max_length=255, description="檔案路徑")
    file_type = fields.CharField(max_length=50, description="檔案類型")
    file_size = fields.IntField(description="檔案大小(bytes)")
    upload_time = fields.DatetimeField(auto_now_add=True, description="上傳時間")
    description = fields.CharField(max_length=255, null=True, description="檔案描述")
    
    class Meta:
        table = "grant_attachments"
        table_description = "補助案件附件資料表"


class GrantComments(models.Model):
    """補助案件評論資料表"""
    id = fields.IntField(pk=True)
    grant = fields.ForeignKeyField("models.Grants", related_name="comments", description="所屬案件")
    user = fields.ForeignKeyField("models.Users", related_name="grant_comments", description="評論者")
    comment = fields.TextField(description="評論內容")
    created_at = fields.DatetimeField(auto_now_add=True, description="建立時間")
    
    class Meta:
        table = "grant_comments"
        table_description = "補助案件評論資料表"


class GrantHistory(models.Model):
    """補助案件歷史紀錄資料表"""
    id = fields.IntField(pk=True)
    grant = fields.ForeignKeyField("models.Grants", related_name="history", description="所屬案件")
    status = fields.CharEnumField(GrantStatus, description="案件狀態")
    changed_by = fields.ForeignKeyField(
        "models.Users", related_name="grant_history_changes", description="修改人員"
    )
    changed_at = fields.DatetimeField(auto_now_add=True, description="修改時間")
    notes = fields.TextField(null=True, description="備註")
    
    class Meta:
        table = "grant_history"
        table_description = "補助案件歷史紀錄資料表"

class CropCategories(models.Model):
    """作物類別資料表"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True, description="作物類別名稱")
    
    class Meta:
        table = "crop_categories"
        table_description = "作物類別資料表"
    
    def __str__(self):
        return self.name
    
class CropNames(models.Model):
    """作物名稱資料表"""
    id = fields.IntField(pk=True)
    category = fields.ForeignKeyField("models.CropCategories", related_name="crop_name", description="所屬作物類別")
    name = fields.CharField(max_length=50, description="作物名稱")
    
    class Meta:
        table = "crop_names"
        table_description = "作物名稱資料表"
        unique_together = (("category", "name"),)
    
    def __str__(self):
        return f"{self.category.name}-{self.name}"
    
class FundingSources(models.Model):
    """補助來源資料表"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True, description="補助來源名稱")
    code = fields.CharField(max_length=10, unique=True, description="補助來源代碼")
    
    class Meta:
        table = "funding_sources"
        table_description = "補助來源資料表"
    
    def __str__(self):
        return self.name
    
class Offices(models.Model):
    """單位/管理處資料表"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True, description="單位名稱")
    short_name = fields.CharField(max_length=10, unique=True, description="單位縮寫")
    code = fields.CharField(max_length=10, unique=True, description="單位代碼")
    classification = fields.IntField(max_length=2, default=1, description="單位類型(1:管理處 2:其他)")
    
    class Meta:
        table = "offices"
        table_description = "單位/管理處資料表"
    
    def __str__(self):
        return self.name
    
class Counties(models.Model):
    """縣市資料表"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=10, unique=True, description="縣市名稱")
    code = fields.CharField(max_length=10, unique=True, description="縣市代碼")
    
    class Meta:
        table = "counties"
        table_description = "縣市資料表"
    
    def __str__(self):
        return self.name

class Towns(models.Model):
    """鄉鎮市區資料表"""
    id = fields.IntField(pk=True)
    county = fields.ForeignKeyField("models.Counties", related_name="town", description="所屬縣市")
    name = fields.CharField(max_length=20, description="鄉鎮市區名稱")
    code = fields.CharField(max_length=10, description="鄉鎮市區代碼")
    is_indigenous = fields.BooleanField(default=False, description="是否為原民區域")
    indigenous_type = fields.CharField(max_length=10, null=True, description="原民區域類型(1:山地鄉 2:平地鄉)")
    
    class Meta:
        table = "towns"
        table_description = "鄉鎮市區資料表"
        unique_together = (("county", "name"), ("county", "code"))
    
    def __str__(self):
        return f"{self.county.name}{self.name}"
    
class Villages(models.Model):
    """村里資料表"""
    id = fields.IntField(pk=True)
    town = fields.ForeignKeyField("models.Towns", related_name="village", description="所屬鄉鎮市區")
    name = fields.CharField(max_length=10, description="村里名稱")
    code = fields.CharField(max_length=20, description="村里代碼")
    
    class Meta:
        table = "villages"
        table_description = "村里資料表"
        unique_together = (("town", "name"), ("town", "code"))
    
    def __str__(self):
        return f"{self.town.county.name}{self.town.name}{self.name}"
    
class Sections(models.Model):
    """地段資料表"""
    id = fields.IntField(pk=True)
    town = fields.ForeignKeyField("models.Towns", related_name="section", description="所屬鄉鎮市區")
    name = fields.CharField(max_length=50, description="地段名稱")
    code = fields.CharField(max_length=10, description="地段代碼")
    
    class Meta:
        table = "sections"
        table_description = "地段資料表"
        unique_together = (("town", "name"), ("town", "code"))
    
    def __str__(self):
        return f"{self.town.county.name}{self.town.name}{self.name}"

class PFMaterials(models.Model):
    """管件材質資料表"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True, description="管件材質名稱")
    
    class Meta:
        table = "pf_materials"
        table_description = "管件材質資料表"
    
    def __str__(self):
        return self.name

class PFDiameters(models.Model):
    """管徑資料表"""
    id = fields.IntField(pk=True)
    value = fields.FloatField(description="管徑值")
    name = fields.CharField(max_length=50, description="管徑名稱")

    class Meta:
        table = "pf_diameters"
        table_description = "管徑資料表"
        unique_together = (("name", "value"),)
    
    def __str__(self):
        return f"{self.name} - {self.value}"

class PFModules(models.Model):
    """管件功能類型資料表"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True, description="管件功能類型名稱")
    
    class Meta:
        table = "pf_modules"
        table_description = "管件功能類型資料表"
    
    def __str__(self):
        return self.name

class PFGroups(models.Model):
    """管件分組資料表"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True, description="管件組別名稱")

    class Meta:
        table = "pf_groups"
        table_description = "管件分組資料表"
        
    def __str__(self):
        return self.name

class PipeFittings(models.Model):
    """管件資料表"""
    pomno = fields.IntField(pk=True, description="管件代碼")
    name = fields.CharField(max_length=50, unique=False, description="管件名稱或料號")
    material = fields.ForeignKeyField("models.PFMaterials", related_name="pf_material", description="所屬管件材質")
    module = fields.ForeignKeyField("models.PFModules", related_name="pf_module", description="所屬管件功能類型")
    diameter1 = fields.ForeignKeyField("models.PFDiameters", related_name="pf_diameter1", null=True, description="所屬管徑1")
    diameter2 = fields.ForeignKeyField("models.PFDiameters", related_name="pf_diameter2", null=True, description="所屬管徑2")
    diameter3 = fields.ForeignKeyField("models.PFDiameters", related_name="pf_diameter3", null=True, description="所屬管徑3")
    unit = fields.CharField(max_length=10, null=True, description="管件計量單位")
    description = fields.CharField(max_length=255, null=True, description="管件描述")
    office = fields.ForeignKeyField("models.Offices", related_name="pipe_fittings", null=True, description="所屬單位/管理處")
    length = fields.FloatField(null=True, description="管件長度")
    compatibility_group = fields.JSONField(null=True, description="相容性分組")
    typical_location = fields.CharField(max_length=255, null=True, description="典型使用位置")
    is_active = fields.BooleanField(default=True, description="是否啟用")
    is_terminal = fields.BooleanField(default=False, description="是否為末端設備")
    year = fields.IntField(null=True, description="管件年份")
    created_at = fields.DatetimeField(auto_now_add=True, description="建立時間")
    modified_at = fields.DatetimeField(auto_now=True, description="修改時間")
    created_by = fields.ForeignKeyField("models.Users", related_name="created_pipe_fittings", description="建立人帳號", null=True, on_delete=fields.CASCADE)
    modified_by = fields.ForeignKeyField("models.Users", related_name="modified_pipe_fittings", description="修改人帳號", null=True, on_delete=fields.SET_NULL)

    class Meta:
        table = "pipe_fittings"
        table_description = "管件資料表"
        unique_together = (("name", "material", "module", "diameter1", "diameter2", "diameter3", "office"),)
        indexes = [
            ("name", "material", "module", "diameter1", "diameter2", "diameter3", "office"),
        ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.price_history = []
        self.current_price = None
    
    def __str__(self):
        return f"{self.name} - {self.material.name} - {self.module.name} - {self.diameter1.value} - {self.diameter2.value} - {self.diameter3.value}"
    
class IrrigationTypes(models.Model):
    """灌溉類型資料表"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True, description="灌溉類型名稱")
    code = fields.CharField(max_length=10, unique=True, description="灌溉類型代碼")
    description = fields.CharField(max_length=255, null=True, description="灌溉類型描述")
    is_active = fields.BooleanField(default=True, description="是否啟用")
    parent = fields.ForeignKeyField("models.IrrigationTypes", related_name="children", null=True, description="父類型")

    
    class Meta:
        table = "irrigation_types"
        table_description = "灌溉類型資料表"
    
    def __str__(self):
        return self.name
    
class PFAnnualPrices(models.Model):
    """管件年度價格資料表"""
    id = fields.IntField(pk=True)
    pipe_fitting = fields.ForeignKeyField("models.PipeFittings", related_name="annual_prices", description="所屬管件")
    office= fields.ForeignKeyField("models.Offices", related_name="pf_annual_prices", null=True, description="所屬單位/管理處")
    is_active = fields.BooleanField(default=True, description="是否啟用")
    year = fields.IntField(description="年度")
    price = fields.FloatField(description="價格")
    created_at = fields.DatetimeField(auto_now_add=True, description="建立時間")
    modified_at = fields.DatetimeField(auto_now=True, description="修改時間")
    created_by = fields.ForeignKeyField("models.Users", related_name="created_pf_annual_price", description="建立人帳號", null=True, on_delete=fields.CASCADE)
    modified_by = fields.ForeignKeyField("models.Users", related_name="modified_pf_annual_price", description="修改人帳號", null=True, on_delete=fields.SET_NULL)
    
    class Meta:
        table = "pf_annual_prices"
        table_description = "管件年度價格資料表"
        unique_together = (("pipe_fitting", "year", "office"),)
        indexes = [
            ("pipe_fitting", "year", "office"),
        ]
    def __str__(self):
        return f"{self.pipe_fitting.name} - {self.year} - {self.price}"
    
class SubsidySettings(models.Model):
    """補助設定資料表"""
    id = fields.IntField(pk=True)
    irrigation_type = fields.ForeignKeyField("models.IrrigationTypes", related_name="subsidy_settings", description="所屬灌溉類型")
    facility_type = fields.ForeignKeyField("models.FacilityTypes", related_name="subsidy_settings", description="所屬設施類型")
    year = fields.IntField(description="年度")
    founding_source = fields.ForeignKeyField("models.FundingSources", related_name="subsidy_settings", description="所屬補助來源")
    working_fee_cap = fields.FloatField(description="工作費上限(元/公頃)")
    design_fee_ratio = fields.FloatField(description="規劃設計費比例(%)")
    subsidy_ratio = fields.FloatField(description="補助比例(%)")
    subsidy_cap = fields.FloatField(description="補助上限(元/公頃)")
    is_active = fields.BooleanField(default=True, description="是否啟用")
    created_at = fields.DatetimeField(auto_now_add=True, description="建立時間")
    modified_at = fields.DatetimeField(auto_now=True, description="修改時間")
    created_by = fields.ForeignKeyField("models.Users", related_name="created_subsidy_settings", description="建立人帳號", null=True, on_delete=fields.CASCADE)
    modified_by = fields.ForeignKeyField("models.Users", related_name="modified_subsidy_settings", description="修改人帳號", null=True, on_delete=fields.SET_NULL)
    
    class Meta:
        table = "subsidy_settings"
        table_description = "補助設定資料表"
    
    def __str__(self):
        return self.name
    
class FacilityTypes(models.Model):
    """設施類型資料表"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True, description="設施類型名稱")
    code = fields.CharField(max_length=10, unique=True, null=True, description="設施類型代碼")
    description = fields.CharField(max_length=255, null=True, description="設施類型描述")
    is_active = fields.BooleanField(default=True, description="是否啟用")
    created_at = fields.DatetimeField(auto_now_add=True, description="建立時間")
    modified_at = fields.DatetimeField(auto_now=True, description="修改時間")
    
    class Meta:
        table = "facility_types"
        table_description = "設施類型資料表"
    
    def __str__(self):
        return self.name
    
class SubsidyPolicies(models.Model):
    """補助政策資料表"""
    id = fields.IntField(pk=True)
    year = fields.IntField(description="年度")
    funding_source = fields.ForeignKeyField("models.FundingSources", related_name="subsidy_policies", description="所屬補助來源")
    general_subsidy_ratio = fields.FloatField(description="一般補助比例(%)")
    gold_corridor_ratio = fields.FloatField(description="金色走廊補助比例(%)")
    indigenous_increase_ratio = fields.FloatField(description="原民區域增額補助比例(%)")
    total_cap = fields.FloatField(description="補助上限")
    person_cap = fields.FloatField(description="每人補助上限")
    engine_cap = fields.FloatField(description="每台引擎補助上限")
    control_device_min_area = fields.FloatField(description="控制裝置最小面積(公頃)")
    control_device_cap = fields.FloatField(description="控制裝置補助上限")
    storage_cap = fields.FloatField(description="儲水設備補助上限")
    storage_min_area = fields.FloatField(description="儲水設備最小面積(公頃)")
    reapplication_ratio = fields.FloatField(description="再申請比例(%)")
    design_fee_ratio = fields.FloatField(description="設計費比例(%)")
    is_active = fields.BooleanField(default=True, description="是否啟用")
    created_at = fields.DatetimeField(auto_now_add=True, description="建立時間")
    modified_at = fields.DatetimeField(auto_now=True, description="修改時間")
    created_by = fields.ForeignKeyField("models.Users", related_name="created_subsidy_policies", description="建立人帳號", null=True, on_delete=fields.CASCADE)
    modified_by = fields.ForeignKeyField("models.Users", related_name="modified_subsidy_policies", description="修改人帳號", null=True, on_delete=fields.SET_NULL)
    
    class Meta:
        table = "subsidy_policies"
        table_description = "補助政策資料表"
    
    def __str__(self):
        return self.name
    
class IrrigationSubsidies(models.Model):
    """灌溉補助資料表"""
    id = fields.IntField(pk=True)
    subsidy_policy = fields.ForeignKeyField("models.SubsidyPolicies", related_name="irrigation_subsidies", description="所屬補助政策")
    irrigation_type = fields.ForeignKeyField("models.IrrigationTypes", related_name="irrigation_subsidies", description="所屬灌溉類型")
    facility_type = fields.ForeignKeyField("models.FacilityTypes", related_name="irrigation_subsidies", description="所屬設施類型")
    facility_fee = fields.FloatField(description="設施費用")
    subsidy_reference = fields.FloatField(description="補助參考值")
    working_fee = fields.FloatField(description="工作費")
    is_active = fields.BooleanField(default=True, description="是否啟用")
    created_at = fields.DatetimeField(auto_now_add=True, description="建立時間")
    modified_at = fields.DatetimeField(auto_now=True, description="修改時間")
    
    class Meta:
        table = "irrigation_subsidies"
        table_description = "灌溉補助資料表"
    def __str__(self):
        return f"{self.subsidy_policy.year} - {self.irrigation_type.name} - {self.facility_type.name}"

class WaterSources(models.Model):
    """水源資料表"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True, description="水源名稱")
    code = fields.CharField(max_length=10, unique=True, null=True, description="水源代碼")
    description = fields.CharField(max_length=255, null=True, description="水源描述")
    is_active = fields.BooleanField(default=True, description="是否啟用")
    
    class Meta:
        table = "water_sources"
        table_description = "水源資料表"
    
    def __str__(self):
        return self.name
    
