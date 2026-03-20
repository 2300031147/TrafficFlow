from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from server.config.settings import settings
import structlog
import jwt
from server.db.connection import get_pool, close_pool
from server.api.websocket import manager

from server.api.routes import auth, junctions, alerts, models, stream, ingest
from server.api.middleware import setup_middleware

logger = structlog.get_logger(__name__)

_is_dev = settings.environment == "development"
app = FastAPI(
    title="UrbanFlow CCC API",
    docs_url="/docs" if _is_dev else None,
    redoc_url="/redoc" if _is_dev else None,
    openapi_url="/openapi.json" if _is_dev else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_middleware(app)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(junctions.router, prefix="/api/v1/junctions", tags=["junctions"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["alerts"])
app.include_router(models.router, prefix="/api/v1/models", tags=["models"])
app.include_router(stream.router, prefix="/api/v1/stream", tags=["stream"])
app.include_router(ingest.router, prefix="/api/v1/ingest", tags=["ingest"])

@app.websocket("/ws/{city_id}")
async def websocket_endpoint(websocket: WebSocket, city_id: str, token: str = Query(...)):
    """Authenticated WebSocket — token passed as ?token=<access_token> query param."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        city_access = payload.get("city_access", [])
        if "*" not in city_access and city_id not in city_access:
            await websocket.close(code=4003)  # Policy violation
            return
    except Exception:
        await websocket.close(code=4001)  # Unauthorized
        return

    await manager.connect(websocket, city_id)
    try:
        while True:
            await websocket.receive_text()  # Heartbeat / keep-alive
    except WebSocketDisconnect:
        manager.disconnect(websocket, city_id)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting UrbanFlow Server CCC API")
    # SEC-M7: never start production with default JWT secret
    if settings.environment == "production" and "development" in settings.jwt_secret_key:
        raise RuntimeError("FATAL: default JWT secret detected in production. Set JWT_SECRET_KEY in .env.")
    # M14: reject default DB credentials in production
    if settings.environment == "production" and "urban_password" in settings.database_url:
        raise RuntimeError("FATAL: default DB password in production. Set DATABASE_URL in .env.")
    await get_pool()
    import asyncio
    from server.api.websocket import broadcast_loop
    asyncio.create_task(broadcast_loop())

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down UrbanFlow Server CCC API")
    await close_pool()

@app.get("/health")
async def health():
    return {"status": "ok"}
