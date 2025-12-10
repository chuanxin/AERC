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


class LeisureFarms(Model):
    """
    休閒農場資料表 - 來自農業部開放資料 API
    
    資料來源：農業部開放資料平台
    API URL: https://data.moa.gov.tw/Service/OpenData/ODwsv/ODwsvQualityFarm.aspx?&UnitId=376
    
    此資料表由 PostGIS 直接管理，不透過 Tortoise migration
    資料透過定期同步腳本從 MOA API 更新
    """
    id = fields.IntField(pk=True, description="主鍵 ID")
    farm_name = fields.CharField(max_length=255, description="農場名稱 (對應 API: FarmNm_CH)")
    county = fields.CharField(max_length=50, description="縣市名稱 (對應 API: County)")
    township = fields.CharField(max_length=50, description="鄉鎮市區名稱 (對應 API: Township)")
    address = fields.CharField(max_length=500, null=True, description="農場地址 (對應 API: Address_CH)")
    phone = fields.CharField(max_length=50, null=True, description="聯絡電話 (對應 API: TEL)")
    web_url = fields.CharField(max_length=500, null=True, description="農場網站 (對應 API: WebURL)")
    certify_start_date = fields.DateField(null=True, description="認證起始日期 (對應 API: CertifySDate)")
    certify_end_date = fields.DateField(null=True, description="認證結束日期 (對應 API: CertifyEDate)")
    identify_item = fields.CharField(max_length=255, null=True, description="認證項目 (對應 API: IdentifyItem)")
    photo_url = fields.CharField(max_length=500, null=True, description="農場照片 URL (對應 API: Photo)")
    longitude = fields.DecimalField(max_digits=12, decimal_places=8, description="經度 WGS84 (對應 API: Longitude)")
    latitude = fields.DecimalField(max_digits=12, decimal_places=8, description="緯度 WGS84 (對應 API: Latitude)")
    # geom 欄位由 PostGIS 直接管理，在 ORM 中不定義
    last_synced = fields.DatetimeField(null=True, description="最後同步時間")
    created_at = fields.DatetimeField(null=True, description="建立時間")

    class Meta:
        table = "leisure_farms"
        managed = False  # 不由 Tortoise ORM 管理遷移，由 PostGIS 直接管理