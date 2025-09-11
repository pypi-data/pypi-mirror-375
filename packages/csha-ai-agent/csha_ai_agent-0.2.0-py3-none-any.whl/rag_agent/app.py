from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from rag_agent.core.config import settings
from rag_agent.api.rag import router

app = FastAPI(title=settings.APP_NAME)

#Only neeeded if FastAPI is called from browser - TODO: Remove if not needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.ALLOW_ORIGINS], #AnyHttpUrl -> str
    allow_credentials=settings.ALLOW_CREDENTIALS,
    allow_methods=settings.ALLOW_METHODS,
    allow_headers=settings.ALLOW_HEADERS,
)
app.include_router(router)

