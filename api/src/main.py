from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
from src.routes import users, offices, domicile, grants, grant_versions, pipe_fittings, pf_modules, pf_materials, pf_diameters, pf_annual_prices, irrigation_types, gis, test_pdf, attachments, qualification, spatial_services, downloads

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
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


register_tortoise(app, config=TORTOISE_ORM, generate_schemas=False)