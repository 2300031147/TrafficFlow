import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, Response
from server.api.dependencies import verify_device_token_route
from server.config.settings import settings

router = APIRouter()
# __file__ = .../server/api/routes/models.py → dirname x3 = .../server/
_SERVER_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@router.get("/lstm/{junction_id}")
async def get_lstm_model(junction_id: str, d_id: str = Depends(verify_device_token_route)):
    model_path = os.path.join(settings.model_storage_path, "lstm_latest.pt")
    if not os.path.exists(model_path):
        raise HTTPException(status_code=404, detail="Model not available yet")
    return FileResponse(model_path, media_type="application/octet-stream")

@router.get("/rl/{junction_id}")
async def get_rl_model(junction_id: str, d_id: str = Depends(verify_device_token_route)):
    model_path = os.path.join(settings.model_storage_path, "rl_latest.pt")
    if not os.path.exists(model_path):
        raise HTTPException(status_code=404, detail="Model not available yet")
    return FileResponse(model_path, media_type="application/octet-stream")

@router.get("/festival-dates/{year}")
async def get_festival_dates(year: int, d_id: str = Depends(verify_device_token_route)):
    if not (2020 <= year <= 2035):
        raise HTTPException(status_code=400, detail="Year out of range (2020-2035)")
    path = os.path.join(_SERVER_DIR, "config", f"festival_dates_{year}.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Year not found")
    return FileResponse(path, media_type="application/json")
