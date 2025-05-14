from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise import Tortoise

from src.database.register import register_tortoise
from src.database.config import TORTOISE_ORM

# enable schemas to read relationship between models
Tortoise.init_models(["src.database.models"], "models")

"""
import 'from src.routes import users, notes' must be after 'Tortoise.init_models'
why?
https://stackoverflow.com/questions/65531387/tortoise-orm-for-python-no-returns-relations-of-entities-pyndantic-fastapi
"""
from src.routes import users, offices, domicile, grants, pipe_fittings, pf_modules, pf_materials, pf_diameters

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
app.include_router(pipe_fittings.router, prefix="/pipe_fittings", tags=["Pipe Fittings"])
app.include_router(pf_modules.router)
app.include_router(pf_materials.router)
app.include_router(pf_diameters.router)


register_tortoise(app, config=TORTOISE_ORM, generate_schemas=False)

@app.get("/")
async def home():
    return "Hello, World!"