from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controllers.auth import (
    auth_controller,
    google_auth_controller,
    otp_controller,
    permission_controller,
    role_controller,
    user_controller,
)


# Application Fastapi
app = FastAPI(
    title="SkillMap",
    description="Backend de SkillMap: application de de suivi et de gestion des compétences",
)

# Origins autorisés
origins = ["http://localhost:300", "http://127.0.0.1:300"]

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
async def root():
    return {
        "msg": "Application de suivi et de gestion des compétences. Retrouvez la documentation sur '/docs'"
    }
