from tortoise import fields, models
from enum import Enum

class Users(models.Model):
    """系統使用者資料表"""
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=20, unique=True, description="使用者帳號")
    full_name = fields.CharField(max_length=50, null=True, description="使用者姓名")
    email = fields.CharField(max_length=255, null=True, description="電子郵件")
    email_verified = fields.BooleanField(default=False, description="電子郵件是否已驗證")
    password = fields.CharField(max_length=128, null=True, description="密碼")

    office = fields.ForeignKeyField("models.Offices", related_name="user", null=True, description="所屬單位/管理處")
    department = fields.JSONField(null=True, description="部門詳細資訊 JSON: {'branch': {'code': '1', 'name': '北港分處'}, 'station': {'code': '01', 'name': '鹿寮站'}} 或 {'legacy_text': '自由輸入文字'}")
    job_title = fields.CharField(max_length=50, null=True, description="職稱")
    phone = fields.CharField(max_length=20, null=True, description="聯絡電話")
    phone_ext = fields.CharField(max_length=10, null=True, description="分機")
    mobile = fields.CharField(max_length=20, null=True, description="手機")

    is_active = fields.BooleanField(default=True, description="是否啟用")
    role = fields.CharField(max_length=50, default="user", description="角色: admin, manager, user 等")
    permissions = fields.JSONField(null=True, description="使用者權限設定（JSONB）：{mode: 'default'|'scoped'|'custom', scope: {...}, custom: {...}}")
    last_login = fields.DatetimeField(null=True, description="最後登入時間")

    # 密碼政策相關欄位
    password_changed_at = fields.DatetimeField(null=True, description="密碼最後更改時間")
    failed_login_count = fields.IntField(default=0, description="連續登入失敗次數")
    locked_until = fields.DatetimeField(null=True, description="帳號鎖定截止時間")

    created_at = fields.DatetimeField(auto_now_add=True, description="建立時間")
    modified_at = fields.DatetimeField(auto_now=True, description="修改時間")

    class Meta:
        table = "users"
        table_description = "使用者資料表"
    
    def __str__(self):
        return f"{self.username} ({self.full_name})"


class AuthTokenType(str, Enum):
    """認證 Token 類型枚舉"""
    EMAIL_VERIFICATION = "email_verification"  # Email 驗證
    PASSWORD_RESET = "password_reset"          # 密碼重設
    ACCOUNT_MIGRATION = "account_migration"    # 帳號轉移（舊系統使用者啟用）


class AuthTokenStatus(str, Enum):
    """認證 Token 狀態枚舉"""
    PENDING = "pending"    # 待使用
    USED = "used"          # 已使用
    EXPIRED = "expired"    # 已過期
    REVOKED = "revoked"    # 已撤銷


class AuthToken(models.Model):
    """認證 Token 資料表 - 統一處理 Email 驗證和密碼重設"""
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.Users", related_name="auth_tokens", description="所屬用戶")
    token_type = fields.CharEnumField(AuthTokenType, description="Token 類型")
    token = fields.CharField(max_length=128, unique=True, description="Token 值（UUID）")
    status = fields.CharEnumField(AuthTokenStatus, default=AuthTokenStatus.PENDING, description="Token 狀態")

    # OTP 驗證（用於密碼重設）
    otp = fields.CharField(max_length=6, null=True, description="6位數字 OTP（僅密碼重設使用）")
    otp_verified = fields.BooleanField(default=False, description="OTP 是否已驗證")

    # 時效性
    created_at = fields.DatetimeField(auto_now_add=True, description="建立時間")
    expires_at = fields.DatetimeField(description="過期時間")
    used_at = fields.DatetimeField(null=True, description="使用時間")

    # 安全審計
    ip_address = fields.CharField(max_length=45, null=True, description="請求 IP 地址")
    user_agent = fields.CharField(max_length=255, null=True, description="請求 User-Agent")

    class Meta:
        table = "auth_tokens"
        table_description = "認證 Token 資料表"
        indexes = [
            ("token",),
            ("user", "token_type", "status"),
            ("expires_at",),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.token_type.value} - {self.status.value}"


class RegistrationStatus(str, Enum):
    """帳號申請狀態枚舉"""
    PENDING = "pending"      # 待審核
    APPROVED = "approved"    # 已核准
    REJECTED = "rejected"    # 已拒絕


class UserRegistration(models.Model):
    """帳號申請記錄表 - 儲存申請原因和審核流程"""
    id = fields.IntField(pk=True)
    user = fields.OneToOneField("models.Users", related_name="registration", description="申請的使用者帳號")

    # 申請資訊
    application_reason = fields.TextField(description="申請原因說明")

    # 審核流程
    status = fields.CharEnumField(RegistrationStatus, default=RegistrationStatus.PENDING, description="申請狀態")
    reviewed_by = fields.ForeignKeyField("models.Users", null=True, related_name="reviewed_registrations", description="審核人員")
    reviewed_at = fields.DatetimeField(null=True, description="審核時間")
    review_comment = fields.TextField(null=True, description="審核意見")

    # 時間戳記
    created_at = fields.DatetimeField(auto_now_add=True, description="申請時間")
    modified_at = fields.DatetimeField(auto_now=True, description="修改時間")

    class Meta:
        table = "user_registrations"
        table_description = "帳號申請記錄表"
        indexes = [
            ("status",),
            ("created_at",),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.status.value}"


class PasswordHistory(models.Model):
    """密碼歷史記錄表 - 用於實作密碼三代不重複政策"""
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.Users", related_name="password_history", description="使用者")
    password_hash = fields.CharField(max_length=128, description="歷史密碼 hash")

    # 審計資訊
    changed_at = fields.DatetimeField(auto_now_add=True, description="密碼變更時間")
    changed_by_ip = fields.CharField(max_length=45, null=True, description="變更來源 IP")
    user_agent = fields.CharField(max_length=255, null=True, description="User Agent")
    change_method = fields.CharField(max_length=50, null=True, description="變更方式: password_reset, user_change, admin_reset")

    class Meta:
        table = "password_history"
        table_description = "密碼歷史記錄表"
        ordering = ["-changed_at"]  # 最新的在前
        indexes = [
            ("user", "changed_at"),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.changed_at.strftime('%Y-%m-%d %H:%M')}"


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
    """補助案件狀態"""
    DRAFT = "draft"                # 草稿（編輯中）
    SUBMITTED = "submitted"        # 已結案，並完成文件上傳的完整封存狀態
    UNDER_REVIEW = "under_review"  # 審查中（已編預算）
    APPROVED = "approved"          # 核准
    REJECTED = "rejected"          # 駁回
    WITHDRAWN = "withdrawn"        # 撤回
    CROSS_YEAR = "cross_year"      # 跨年度案件狀態
    COMPLETED = "completed"        # 線上結案，尚未完成文件上傳
    SOFT_DELETE = "deleted"        # 邏輯刪除
    INACTIVE = "inactive"          # 歷史案件初始狀態（待認領）

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
    active_version = fields.ForeignKeyField("models.GrantVersions", related_name="active_grant", null=True, description="目前現行的版本ID")
    
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
    
    # 災害案件相關欄位
    is_disaster_case = fields.BooleanField(default=False, description="是否為災害案件")
    disaster_case_description = fields.TextField(null=True, description="災害案件說明")
    
    # 申請、收件日期
    received_date = fields.DateField(description="建檔日期")
    received_time = fields.TimeField(description="建檔時間")
    
    # 案件狀態
    status = fields.CharField(max_length=20, default="draft", description="案件狀態: 0:完成申請人資料, 1:完成土地資料, 2:完成灌溉調控設施, 3:完成田間管路, 4:完成現場勘查, 5:完成補助申請資料, 6:完成結案申報, 7:完成測試合格的時間, 8:完成撥款作業, 9:完成撥款, 99:駁回申請")
    status_detail = fields.CharField(max_length=50, null=True, description="狀態詳情")
    current_step = fields.IntField(default=1, description="目前步驟")
    bulletin = fields.CharField(max_length=20, null=True, description="公告狀態: 0:已受理, 1:審查中, 2:審查通過 3:結案流程 4:撥款作業 5:撥款完成")
    bulletin_sys = fields.CharField(max_length=20, null=True, description="公告狀態(系統): 0:申請人資料, 1:現場勘查, 2:補助申請資料 3:結案申報 4:測試合格的時間 5:")
    is_legacy = fields.BooleanField(default=False, description="是否為歷史匯入資料")
    
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
        indexes = [
            ("year", "office_id", "sn"),
        ]
    
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
    
    async def generate_case_number(self):
        """
        根據 year + office_id + 序列號 產生完整案件編號

        序列號邏輯：查詢同單位同年度的案件數量（不包含自己）+ 1
        這樣即使 sn 欄位不連續，case_number 仍然反映真實的案件順序
        """
        office_id_str = str(self.office_id)
        if self.office_id is not None:
            if self.office_id < 10: # 個位數
                office_id_str = f"0{self.office_id}"
            elif self.office_id < 100: # 兩位數
                office_id_str = str(self.office_id)
            # 三位數或以上則 office_id_str 保持原樣 str(self.office_id)
        else:
            office_id_str = "00" # 或者您希望 office_id 為 None 時的默認處理

        # 查詢同單位同年度已有的案件數量（不包含自己）
        query = Grants.filter(year=self.year, office_id=self.office_id)
        if self.id:  # 如果是更新操作（已有 id），排除自己
            query = query.exclude(id=self.id)

        existing_count = await query.count()
        sequence_number = existing_count + 1  # 這是第 N 個案件

        return f"{self.year}{office_id_str}{str(sequence_number).zfill(4)}"

    async def save(self, *args, **kwargs):
        """在存入資料時，自動產生 SN 與 case_number"""
        if not self.sn:  # 如果 SN 尚未設定，則自動產生
            self.sn = await self.generate_sn(self.year, self.office_id)
        if not self.case_number:  # 只在 case_number 不存在時才生成
            self.case_number = await self.generate_case_number()
        await super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.case_number} - {self.applicant_name}"
    
class GrantAttachments(models.Model):
    """補助案件附件資料表"""
    id = fields.IntField(pk=True)
    grant = fields.ForeignKeyField("models.Grants", related_name="attachments", description="所屬補助申請案件")
    version = fields.ForeignKeyField("models.GrantVersions", related_name="attachments", null=True, description="所屬案件版本")

    # 分類資訊
    step = fields.IntField(description="申請步驟編號 (5:現場勘查, 6:補助申請, 7:結案申報, 8:測試合格)")
    category = fields.CharField(max_length=20, description="附件分類 (如:施工前照片、施工後照片、收據等)")

    # 檔案資訊（關鍵設計）
    original_filename = fields.CharField(max_length=255, description="使用者上傳的原始檔名")
    internal_filename = fields.CharField(max_length=255, description="系統內部儲存檔名 (UUID格式)")
    filepath = fields.CharField(max_length=500, description="檔案儲存相對路徑")
    filesize = fields.BigIntField(description="檔案大小 (位元組)")
    mime_type = fields.CharField(max_length=100, description="檔案MIME類型")
    checksum = fields.CharField(max_length=64, description="檔案SHA-256校驗和")

    # 業務資訊
    description = fields.TextField(null=True, description="附件說明或備註")
    status = fields.CharField(max_length=20, default="active", description="附件狀態 (active:有效, deleted:已刪除)")

    # 關聯性（Step 7 前後對比用）
    related_attachment = fields.ForeignKeyField("models.GrantAttachments", null=True, description="關聯附件ID (用於前後對比)")
    
    # 審計欄位
    uploaded_at = fields.DatetimeField(auto_now_add=True, description="上傳時間")
    uploaded_by = fields.ForeignKeyField("models.Users", related_name="uploaded_attachments", description="上傳人員")
    
    class Meta:
        table = "grant_attachments"
        table_description = "補助案件附件資料表"
        indexes = [
            ("grant", "step", "category"),
            ("internal_filename",),
            ("uploaded_at",),
            ("status",),
        ]
        

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


class GrantActionType(str, Enum):
    """操作類型枚舉"""
    STATUS_CHANGE = "status_change"           # 狀態變更
    STEP_CHANGE = "step_change"               # 步驟切換
    DATA_UPDATE = "data_update"               # 資料更新
    STEP_DATA_UPDATE = "step_data_update"     # 步驟資料更新
    CURRENT_STEP_UPDATE = "current_step_update"  # 當前步驟更新
    FILE_UPLOAD = "file_upload"               # 檔案上傳
    FILE_DELETE = "file_delete"               # 檔案刪除
    COMMENT_ADD = "comment_add"               # 新增評論
    MANUAL_SAVE = "manual_save"               # 手動保存
    AUTO_SAVE = "auto_save"                   # 自動保存
    FORM_VALIDATION = "form_validation"       # 表單驗證
    CASE_CREATE = "case_create"               # 案件建立
    CASE_SUBMIT = "case_submit"               # 案件提交
    VERSION_UPDATE = "version_update"         # 版本更新
    OWNERSHIP_CLAIM = "ownership_claim"       # 認領案件所有權


class GrantHistory(models.Model):
    """補助案件歷史紀錄資料表"""
    id = fields.IntField(pk=True)
    grant = fields.ForeignKeyField("models.Grants", related_name="history", description="所屬案件")
    
    # 核心欄位
    action_type = fields.CharEnumField(GrantActionType, description="操作類型")
    grant_status = fields.CharEnumField(GrantStatus, null=True, description="案件狀態")
    step_number = fields.IntField(null=True, description="相關步驟編號")
    changed_fields = fields.JSONField(null=True, description="變更的欄位列表")

    # 審計欄位
    old_value = fields.JSONField(null=True, description="變更前的值")
    new_value = fields.JSONField(null=True, description="變更後的值")
    
    # 安全欄位 - 建議
    session_id = fields.CharField(max_length=100, null=True, description="會話ID")
    ip_address = fields.CharField(max_length=45, null=True, description="IP地址")
    
    # status = fields.CharEnumField(GrantStatus, description="案件狀態")
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
    classification = fields.IntField(default=1, description="單位類型(1:管理處 2:其他)")
    is_funding_source = fields.BooleanField(default=False, description="是否為補助來源")

    class Meta:
        table = "offices"
        table_description = "單位/管理處資料表"

    def __str__(self):
        return self.name


class SubsidyAnnualBudget(models.Model):
    """補助年度預算計畫表"""
    id = fields.IntField(pk=True)
    year = fields.IntField(description="年度（民國年）")
    office = fields.ForeignKeyField("models.Offices", related_name="annual_budgets", description="所屬辦公室")
    approved_budget = fields.DecimalField(max_digits=15, decimal_places=2, default=0, description="核定執行預算金額")
    approved_area = fields.DecimalField(max_digits=10, decimal_places=4, default=0, description="核定執行面積（公頃）")

    # 時間戳記
    created_at = fields.DatetimeField(auto_now_add=True, description="建立時間")
    modified_at = fields.DatetimeField(auto_now=True, description="修改時間")
    created_by = fields.ForeignKeyField("models.Users", related_name="created_budgets", null=True, description="建立人帳號", on_delete=fields.SET_NULL)
    modified_by = fields.ForeignKeyField("models.Users", related_name="modified_budgets", null=True, description="修改人帳號", on_delete=fields.SET_NULL)

    class Meta:
        table = "subsidy_annual_budgets"
        table_description = "補助年度預算計畫表"
        unique_together = (("year", "office"),)
        indexes = [
            ("year", "office"),
        ]

    def __str__(self):
        return f"{self.year}年度 - {self.office.name} 預算"

class Counties(models.Model):
    """縣市資料表"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=10, unique=True, description="縣市名稱")
    code = fields.CharField(max_length=10, unique=True, description="縣市代碼")
    land_code = fields.CharField(max_length=10, null=True, description="地政代碼")
    
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
    land_code = fields.CharField(max_length=10, null=True, description="地政代碼")
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
    created_by = fields.ForeignKeyField("models.Users", related_name="pf_annual_prices_created", description="建立人帳號", null=True, on_delete=fields.CASCADE)
    modified_by = fields.ForeignKeyField("models.Users", related_name="pf_annual_prices_modified", description="修改人帳號", null=True, on_delete=fields.SET_NULL)
    
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
    
class PowerEquipments(models.Model):
    """動力設備資料表"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True, description="動力設備名稱")
    code = fields.CharField(max_length=10, unique=True, null=True, description="動力設備代碼")
    description = fields.CharField(max_length=255, null=True, description="動力設備描述")
    is_active = fields.BooleanField(default=True, description="是否啟用")
    
    class Meta:
        table = "power_equipments"
        table_description = "動力設備資料表"
    
    def __str__(self):
        return self.name
    
class RegulationEquipments(models.Model):
    """調控設備資料表"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True, description="調控設備名稱")
    code = fields.CharField(max_length=10, unique=True, null=True, description="調控設備代碼")
    description = fields.CharField(max_length=255, null=True, description="調控設備描述")
    is_active = fields.BooleanField(default=True, description="是否啟用")
    
    class Meta:
        table = "regulation_equipments"
        table_description = "調控設備資料表"
    
    def __str__(self):
        return self.name
    
class TankMaterials(models.Model):
    """儲水設備材質資料表"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True, description="儲水設備材質名稱")
    
    class Meta:
        table = "tank_materials"
        table_description = "儲水設備材質資料表"
    
    def __str__(self):
        return self.name

class DataSchemaVersions(str, Enum):
    """資料結構版本枚舉"""
    V1_0 = "1.0"          # 初始版本
    V1_1 = "1.1"          # 第一次結構調整
    V1_2 = "1.2"          # 新增災害案件欄位
    V1_3 = "1.3"          # 優化土地資料結構
    V1_4 = "1.4"          # 新增設施資料驗證
    V2_0 = "2.0"          # 重大結構變更
    LEGACY = "legacy"     # 歷史匯入資料

class GrantVersions(models.Model):
    """補助申請單版本資料表"""
    id = fields.IntField(pk=True)
    grant = fields.ForeignKeyField("models.Grants", related_name="versions", description="所屬補助申請")
    version = fields.IntField(description="版本資訊")
    all_steps_data = fields.JSONField(description="所有步驟的資料(JSON格式)")
    all_steps_data_hash = fields.CharField(max_length=64, description="所有步驟資料的Hash值，用於檢查版本變更", null=True)
    data_schema_version = fields.CharEnumField(DataSchemaVersions, default=DataSchemaVersions.V1_0, description="資料結構版本")
    comment = fields.CharField(max_length=255, null=True, description="版本說明")
    created_at = fields.DatetimeField(auto_now_add=True, description="建立時間")
    created_by = fields.ForeignKeyField("models.Users", related_name="created_versions", description="建立人帳號", null=True, on_delete=fields.CASCADE)
    modified_at = fields.DatetimeField(auto_now=True, description="修改時間")
    
    class Meta:
        table = "grant_versions"
        table_description = "補助申請單版本資料表"
        unique_together = (("grant", "version"),)
    
    def __str__(self):
        return f"{self.grant.case_number} - Version {self.version}"
    
class DocumentType(str, Enum):
    APPLICATION_FORM = "application_form"        # 申請表
    BUDGET_SHEET = "budget_sheet"               # 預算書
    LAND_REGISTRY = "land_registry"             # 土地清冊
    MATERIAL_LIST = "material_list"             # 材料數量表
    DESIGN_DRAWING = "design_drawing"           # 設計圖
    PHOTO_RECORD = "photo_record"               # 照片記錄
    RECEIPT = "receipt"                         # 收據
    TEST_REPORT = "test_report"                 # 測試報告
    REVIEW_FORM = "review_form"                 # 審查表
    BUDGET_STATEMENT = "budget_statement"           # 預算聲明


class GrantPapers(models.Model):
    """補助申請文件表"""
    id = fields.IntField(pk=True)
    version = fields.ForeignKeyField("models.GrantVersions", related_name="reports", description="所屬補助申請版本")
    document_type = fields.CharField(max_length=50, description="文件類型")
    document_data = fields.JSONField(description="文件內容")
    data_hash = fields.CharField(max_length=64, description="文件內容的Hash值，用於檢查變更", null=True)
    generated_at = fields.DatetimeField(auto_now_add=True, description="建立時間")
    created_by = fields.ForeignKeyField("models.Users", related_name="created_reports", description="建立人帳號", null=True, on_delete=fields.CASCADE)
    is_valid = fields.BooleanField(default=True, description="文件是否有效")
    
    class Meta:
        table = "grant_papers"
        table_description = "補助申請文件表"
        unique_together = (("version", "document_type"),)
        indexes = [
            ("version_id", "document_type"),      # 覆蓋複合查詢
        ]
    
    def __str__(self):
        """返回文件的簡要描述"""
        return f"{self.version.grant.case_number} - {self.document_type.value} - v{self.version.version}"


# === Qualification 重複案件查詢系統相關模型 ===

class QualificationQueryType(str, Enum):
    """查詢類型枚舉 - 統一處理三種查詢模式"""
    GENERAL = "general"        # 一般區域查詢
    INDIGENOUS = "indigenous"  # 原住民鄉查詢
    SLOPE = "slope"           # 山坡地查詢


class QualificationQuery(models.Model):
    """重複案件查詢記錄表 - 統一查詢介面的核心"""
    id = fields.IntField(pk=True)
    query_type = fields.CharEnumField(QualificationQueryType, description="查詢類型")
    
    # 地區參數 - 使用 JSONField 統一存儲不同查詢類型的參數
    location_data = fields.JSONField(description="地區查詢參數: {county, town, section?, landNumber?}")
    
    # 查詢選項
    query_options = fields.JSONField(null=True, description="查詢選項: {years, includeStatistics}")
    
    # 查詢結果快取 - 提升效能
    search_results = fields.JSONField(null=True, description="查詢結果快取")
    area_statistics = fields.JSONField(null=True, description="面積統計結果快取")
    
    # 查詢元資料
    result_count = fields.IntField(default=0, description="查詢結果數量")
    query_hash = fields.CharField(max_length=64, null=True, description="查詢參數雜湊值(用於快取)")
    response_time_ms = fields.IntField(null=True, description="查詢響應時間(毫秒)")
    
    # 時間戳記
    created_at = fields.DatetimeField(auto_now_add=True, description="查詢時間")
    updated_at = fields.DatetimeField(auto_now=True, description="更新時間")
    
    class Meta:
        table = "qualification_queries"
        table_description = "重複案件查詢記錄表"