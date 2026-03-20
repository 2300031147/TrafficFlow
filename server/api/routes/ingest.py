import time as _time
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
from server.api.dependencies import verify_device_token_body
from server.api.middleware import limiter
from fastapi import Request
from server.config.settings import settings
from server.db.queries.junctions import upsert_junction_heartbeat
from server.db.queries.counts import insert_counts
from server.db.queries.signals import insert_signal_decision

router = APIRouter()

class IngestPayload(BaseModel):
    junction_id: str
    sequence_number: int
    data: Dict[str, Any]

@router.post("/")
@limiter.limit(f"{settings.ingest_rate_limit_per_minute}/minute")
async def ingest_report(request: Request, payload: IngestPayload, j_id: str = Depends(verify_device_token_body)):
    """Pi sends batch reporting updates securely"""
    data = payload.data
    
    if "lanes" in data:
       await insert_counts(j_id, data.get('timestamp') or _time.time(), data["lanes"])
       
    if "decisions" in data:
       for dec in data["decisions"][:100]:  # M9: cap to 100 to prevent DoS
           await insert_signal_decision(j_id, dec)

    if "pi_health" in data:
        await upsert_junction_heartbeat(j_id, data["pi_health"])
        
    return {"success": True, "message": "Batch ingested", "model_update_available": False}
