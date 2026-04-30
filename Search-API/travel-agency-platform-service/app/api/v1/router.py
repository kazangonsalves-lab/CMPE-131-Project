from fastapi import APIRouter

from app.api.v1.endpoints.rapidapi import router as rapidapi_router
from app.api.v1.endpoints.price_history import router as price_history_router


api_router = APIRouter()
api_router.include_router(rapidapi_router)
api_router.include_router(price_history_router)
