from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.limiter import limiter
from app.features.v1.ai_integration import router as ai_router
from app.features.v1.appointments import router as appointments_router
from app.features.v1.audit_logs import router as audit_router
from app.features.v1.auth import router as auth_router
from app.features.v1.dashboard import router as dashboard_router
from app.features.v1.notifications import router as notifications_router
from app.features.v1.doctors import router as doctors_router
from app.features.v1.patients import router as patients_router
from app.features.v1.reports import router as reports_router
from app.features.v1.schedules import router as schedules_router
from app.features.v1.services import router as services_router
from app.features.v1.specialties import router as specialties_router
from app.features.v1.uploads import router as uploads_router
from app.features.v1.users import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="SMMG API",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(specialties_router.router)
app.include_router(services_router.router)
app.include_router(doctors_router.router)
app.include_router(patients_router.router)
app.include_router(schedules_router.router)
app.include_router(appointments_router.router)
app.include_router(dashboard_router.router)
app.include_router(notifications_router.router)
app.include_router(reports_router.router)
app.include_router(ai_router.router)
app.include_router(uploads_router.router)
app.include_router(audit_router.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
