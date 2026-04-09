from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .settings import settings
from .api import router as api_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_methods="*"
)


@app.get("", status_code=200)
def health_check():
    return {"detail": [{"msg": "stocksmart ok"}]}

app.include_router(api_router)
