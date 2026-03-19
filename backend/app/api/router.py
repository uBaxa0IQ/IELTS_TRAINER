from fastapi import APIRouter

from app.api.routes.analytics import router as analytics_router
from app.api.routes.auth import router as auth_router
from app.api.routes.essays import router as essays_router
from app.api.routes.prompts import router as prompts_router


api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(prompts_router, prefix="/prompts", tags=["prompts"])
api_router.include_router(essays_router, prefix="/essays", tags=["essays"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
