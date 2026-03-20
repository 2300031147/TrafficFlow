from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
import httpx
import socket
from server.api.dependencies import get_current_user, city_scope_check
from server.db.queries.junctions import get_junction_vpn_ip
from server.config.settings import settings

router = APIRouter()

async def _check_stream_available(vpn_ip: str, port: int) -> bool:
    """Lightweight TCP connectivity check — no full MJPEG stream opened."""
    try:
        sock = socket.create_connection((vpn_ip, port), timeout=2)
        sock.close()
        return True
    except OSError:
        return False

async def fetch_mjpeg_stream(vpn_ip: str, port: int):
    url = f"http://{vpn_ip}:{port}/stream"
    async with httpx.AsyncClient() as client:
        try:
            async with client.stream("GET", url) as response:
                async for chunk in response.aiter_bytes():
                    yield chunk
        except httpx.RequestError:
            return  # stream ends cleanly

@router.get("/{junction_id}")
async def proxy_stream(junction_id: str, user: dict = Depends(get_current_user)):
    """Reverse proxies the Pi MJPEG stream, preventing direct access without JWT/Tokens."""
    await city_scope_check(junction_id, user)

    vpn_ip = await get_junction_vpn_ip(junction_id)
    if not vpn_ip:
        raise HTTPException(status_code=404, detail="Junction offline or not found")

    # M7: Check stream availability BEFORE entering generator
    if not await _check_stream_available(vpn_ip, settings.stream_port):
        raise HTTPException(status_code=502, detail="Edge stream unavailable")

    return StreamingResponse(
        fetch_mjpeg_stream(vpn_ip, port=settings.stream_port),
        media_type="multipart/x-mixed-replace; boundary=FRAME"
    )
