from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.controllers.auth import (
    auth_controller,
    google_auth_controller,
    otp_controller,
    permission_controller,
    role_controller,
    user_controller,
)
from app.core.config import Settings
from app.providers.providers import get_settings


# Application Fastapi
app = FastAPI(
    title="SkillMap",
    description="Backend de SkillMap: application de de suivi et de gestion des compétences",
)

# Origins autorisés
origins = ["http://localhost:3000", "http://127.0.0.1:3000"]

# Configuration des CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_headers="*",
    allow_methods="*",
)

# Ajout des controllers/routers
app.include_router(auth_controller.router)
app.include_router(google_auth_controller.router)
app.include_router(user_controller.router)
app.include_router(otp_controller.router)
app.include_router(role_controller.router)
app.include_router(permission_controller.router)


# Endpoint racine
@app.get("/")
async def root(settings: Settings = Depends(get_settings)):
    return {
        "msg": "Bienvenue sur l'API SkillMap !",
        "documentation": f"{settings.base_url}/docs",
        "description": "Backend de SkillMap: Application de suivi et de gestion des compétences.",
        "version": "1.0.0",
    }


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("./favicon.ico")
