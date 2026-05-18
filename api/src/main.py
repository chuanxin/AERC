from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from tortoise import Tortoise

from src.database.register import register_tortoise
from src.database.config import TORTOISE_ORM

import os
import pytz

os.environ['TZ'] = 'Asia/Taipei'

# enable schemas to read relationship between models
Tortoise.init_models(["src.database.models", "src.database.geo_models"], "models")

"""
import 'from src.routes import users, notes' must be after 'Tortoise.init_models'
why?
https://stackoverflow.com/questions/65531387/tortoise-orm-for-python-no-returns-relations-of-entities-pyndantic-fastapi
"""
from src.routes import users, offices, domicile, grants, grant_versions, pipe_fittings, pf_modules, pf_materials, pf_diameters, pf_annual_prices, irrigation_types, gis, test_pdf, attachments, qualification, spatial_services, downloads, crops, user_management, permissions, leisure_farms, nlsc, auth_keys

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip Compression Middleware
# 壓縮所有大於 1000 bytes 的回應，可將 JSON 資料大小減少 80-90%
app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,      # 只壓縮大於 1KB 的回應
    compresslevel=6         # 壓縮等級 1-9（6 是速度與壓縮率的平衡點）
)

app.include_router(users.router)
app.include_router(user_management.router, prefix="/user-management", tags=["User Management"])
app.include_router(permissions.router, prefix="/permissions", tags=["Permissions"])
app.include_router(offices.router)
app.include_router(domicile.router)
app.include_router(grants.router)
app.include_router(grant_versions.router)
app.include_router(pipe_fittings.router, prefix="/pipe_fittings", tags=["Pipe Fittings"])
app.include_router(pf_modules.router)
app.include_router(pf_materials.router)
app.include_router(pf_diameters.router)
app.include_router(pf_annual_prices.router)
app.include_router(irrigation_types.router)
app.include_router(gis.router)
app.include_router(test_pdf.router)
app.include_router(attachments.router)
app.include_router(qualification.router)
app.include_router(spatial_services.router)
app.include_router(downloads.router)
app.include_router(crops.router)
app.include_router(leisure_farms.router)
app.include_router(nlsc.router)
app.include_router(auth_keys.router)


register_tortoise(app, config=TORTOISE_ORM, generate_schemas=False)