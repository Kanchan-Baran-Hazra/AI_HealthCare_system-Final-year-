from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.middleware import register_middleware
from src.db.main import init_db,engine
from src.api.users.routers import user_router


@asynccontextmanager
async def life_span(app:FastAPI):
    # Create tables
    await init_db()
    # print("stsrt...")
    yield
    # print("closing...")
    # Dispose connection engine on shutdown
    await engine.dispose()


version = "v1"

app = FastAPI(
    version=version,
    title="AI HealthCare App",
    summary="api for ai healthcare platform developed by K.B Hazra for final-year project",
    lifespan=life_span,
    license_info={
        "name": "XXX",
        "url": "https://khazra.com/XXX",  # Optional URL
    },
)


register_middleware(app)


@app.get("/")
def health():
    return {"status": "ok"}



app.include_router(user_router,prefix=f'/api/{version}/user',tags=['Users'])


