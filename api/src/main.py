import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from tortoise import Tortoise
from tortoise.exceptions import ValidationError as TortoiseValidationError

from src.database.register import register_tortoise
from src.database.config import TORTOISE_ORM
from src.exceptions import AppError
from src.services.data_encryption import data_encryption_service  # noqa: F401 — triggers key validation at startup

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

logger = logging.getLogger("api.error_handlers")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "輸入資料格式不正確", "error_code": "VALIDATION_ERROR"},
    )


@app.exception_handler(TortoiseValidationError)
async def tortoise_validation_exception_handler(request: Request, exc: TortoiseValidationError):
    # ORM 欄位驗證失敗，表示 Pydantic schema 的 max_length 未與 ORM CharField 對齊
    # 正確修法：在對應 schema 欄位加上 max_length ≤ ORM 定義值
    logger.warning(
        "ORM 欄位驗證失敗（Schema Drift）%s %s: %s",
        request.method, request.url.path, str(exc),
    )
    return JSONResponse(
        status_code=422,
        content={"detail": "輸入資料格式不正確", "error_code": "VALIDATION_ERROR"},
    )


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    if exc.status_code >= 500:
        diagnostic = exc.diagnostic or exc.detail
        logger.error(
            "AppError 5xx %s %s (status=%d): %s",
            request.method, request.url.path, exc.status_code, diagnostic,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "error_code": "INTERNAL_ERROR"},
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code >= 500:
        logger.error(
            "內部錯誤 %s %s (status=%d): %s",
            request.method, request.url.path, exc.status_code, exc.detail,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": "伺服器發生錯誤，請聯絡系統管理員", "error_code": "INTERNAL_ERROR"},
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("未捕捉異常 %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "伺服器發生錯誤，請聯絡系統管理員", "error_code": "INTERNAL_ERROR"},
    )


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