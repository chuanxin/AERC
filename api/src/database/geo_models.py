from tortoise.models import Model
from tortoise import fields

class GrantLocations(Model):
    id = fields.IntField(pk=True)
    source_system = fields.CharField(max_length=20, description="資料來源 ('new_aerc' or 'legacy_farmdata')")
    source_id = fields.CharField(max_length=255, description="在資料來原系統中的唯一id (grant.id or MapNo)")
    apply_year = fields.IntField(null=True, description="申請年度 (民國年)")
    applicant_name = fields.CharField(max_length=255, null=True, description="申請人姓名")
    land_section = fields.CharField(max_length=255, null=True, description="地段")
    land_number = fields.CharField(max_length=255, null=True, description="地號")
    land_type = fields.CharField(max_length=50, null=True, description="地目代碼: 1:田, 2:旱, 3:林, 4:原, 5:雜, 6:其他, 7:未登記, 8:空白")
    case_status = fields.CharField(max_length=50, null=True, description="案件狀態")
    comment = fields.TextField(null=True, description="土地資料備註")
    meta_data = fields.JSONField(null=True, description="即時顯示的彈出資訊")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "grant_locations"
        # The unique constraint will be added manually in the migration script
        # to handle the PostGIS-specific parts correctly.