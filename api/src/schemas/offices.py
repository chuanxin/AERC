# from typing import List, Optional
# from pydantic import BaseModel, Field
from tortoise.contrib.pydantic import pydantic_model_creator

from src.database.models import Offices


# Office model
OfficeInSchema = pydantic_model_creator(
    Offices, name="OfficeIn", exclude_readonly=True
)
OfficeOutSchema = pydantic_model_creator(
    Offices,
    name="OfficeOut",
    # exclude=("grant", "user")
    # exclude_readonly=True,
    include=("id", "name", "short_name", "code", "classification"), # 只包含 Office 本身的字段
)

# OfficeListSchema = pydantic_model_creator(
#     Offices,
#     name="OfficeListOut",
#     exclude_readonly=True,
#     # 明確排除或不包含可能引起大量數據的關聯字段
#     # 例如，如果 Offices 有 'users' (用戶列表), 'projects' (項目列表) 等關聯
#     # 可以在這裡 exclude 它們，或者只包含必要的標識符
#     # exclude = ("users", "projects", "another_large_relation") # 示例
#     fields = ("id", "name", "short_name", "code", "classification", "is_active") # 只包含 Office 本身的字段
#     # exclude=("grant", "user"), include=("id", "name")
# )

# # 通用的分頁響應模型
# class PaginatedResponse(BaseModel):
#     """通用分頁響應格式"""
#     items: List
#     total: int
#     page: int
#     size: int
#     pages: int


# # Office 分頁響應
# class PaginatedOfficeResponse(PaginatedResponse):
#     items: List[OfficeOutSchema]