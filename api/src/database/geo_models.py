from tortoise.models import Model
from tortoise import fields

class OfficeBoundaries(Model):
    """
    農田水利事業區域資料表 - 外部管理的空間資料表
    此資料表由 PostGIS 直接管理，不透過 Tortoise migration
    """
    gid = fields.IntField(pk=True)
    # 使用 TextField 來處理 PostGIS geometry 欄位
    geom = fields.TextField(description="MultiPolygon geometry in SRID 3824")
    ia_code = fields.CharField(max_length=255, null=True, description="灌區代碼")
    ia_name = fields.CharField(max_length=255, null=True, description="灌區名稱")
    mng_code = fields.CharField(max_length=255, null=True, description="管理處代碼")
    mng_name = fields.CharField(max_length=255, null=True, description="管理處名稱")
    stn_code = fields.CharField(max_length=255, null=True, description="工作站代碼")
    stn_name = fields.CharField(max_length=255, null=True, description="工作站名稱")
    grp_code = fields.CharField(max_length=255, null=True, description="小組代碼")
    grp_name = fields.CharField(max_length=255, null=True, description="小組名稱")
    area = fields.FloatField(null=True, description="面積")
    record_date = fields.DateField(null=True, description="記錄日期")
    sg = fields.CharField(max_length=255, null=True, description="SG")
    stngrp = fields.CharField(max_length=255, null=True, description="工作站小組")
    part = fields.CharField(max_length=255, null=True, description="部分")
    is_virtual = fields.BooleanField(default=False, description="是否為虛擬單位（無實際邊界）")

    class Meta:
        table = "office_boundaries"
        managed = False  # 告訴 Tortoise 不要管理此資料表的 schema


class CountyMOI1090820(Model):
    """
    縣市界線資料表 - 外部管理的空間資料表  
    此資料表由 PostGIS 直接管理，不透過 Tortoise migration
    資料來源：內政部縣市界線圖資 (MOI 109/08/20)
    """
    gid = fields.IntField(pk=True)
    # 使用 TextField 來處理 PostGIS geometry 欄位
    geom = fields.TextField(description="MultiPolygon geometry in SRID 3824")
    countyid = fields.CharField(max_length=255, null=True, description="縣市ID")
    countycode = fields.CharField(max_length=255, null=True, description="縣市代碼")
    countyname = fields.CharField(max_length=255, null=True, description="縣市名稱")
    countyeng = fields.CharField(max_length=255, null=True, description="縣市英文名稱")

    class Meta:
        table = "county_moi_1090820"
        managed = False  # 告訴 Tortoise 不要管理此資料表的 schema


class GrantLocations(Model):
    id = fields.IntField(pk=True)
    source_system = fields.CharField(max_length=20, description="資料來源 ('new_aerc' or 'legacy_farmdata')")
    source_id = fields.CharField(max_length=255, description="在資料來原系統中的唯一id (grant.id or MapNo)")
    apply_year = fields.IntField(null=True, description="申請年度 (民國年)")
    applicant_name = fields.CharField(max_length=255, null=True, description="申請人姓名")
    land_section = fields.CharField(max_length=255, null=True, description="地段")
    land_number = fields.CharField(max_length=255, null=True, description="地號")
    land_type = fields.CharField(max_length=50, null=True, description="地目代碼: 1:田, 2:旱, 3:林, 4:原, 5:雜, 6:其他, 7:未登記, 8:空白")
    case_number = fields.CharField(max_length=100, null=True, description="案件編號")
    case_status = fields.CharField(max_length=50, null=True, description="案件狀態")
    comment = fields.TextField(null=True, description="土地資料備註")
    meta_data = fields.JSONField(null=True, description="即時顯示的彈出資訊")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "grant_locations"
        # The unique constraint will be added manually in the migration script
        # to handle the PostGIS-specific parts correctly.