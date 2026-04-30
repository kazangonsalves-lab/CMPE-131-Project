from fastapi import FastAPI

from app.core.database import Base, engine
import app.models  # registers all models with Base before create_all

from app.api.v1.router import api_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Travel Search API")
app.include_router(api_router, prefix="/api/v1")

