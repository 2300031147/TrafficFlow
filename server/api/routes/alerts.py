from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid as _uuid
from server.api.dependencies import get_current_user, require_role, city_scope_check
from server.db.connection import get_connection

router = APIRouter()

class ResolveRequest(BaseModel):
    resolution_note: Optional[str] = None

@router.get("/")
async def list_alerts(resolved: bool = Query(False), user: dict = Depends(get_current_user)):
    from server.db.queries import alerts as aq
    return await aq.get_active_alerts(user['city_access'], resolved)

@router.post("/{alert_id}/resolve", dependencies=[Depends(require_role("operator", "admin", "superadmin"))])
async def resolve_alert(alert_id: str, req: ResolveRequest, user: dict = Depends(get_current_user)):
    try:
        _uuid.UUID(alert_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid alert ID format")

    # One connection, one transaction — atomic city check + resolve + audit
    async with get_connection() as conn:
        async with conn.transaction():
            row = await conn.fetchrow(
                "SELECT j.city FROM alerts a JOIN junctions j ON a.junction_id = j.id WHERE a.id = $1",
                alert_id
            )
            if not row:
                raise HTTPException(status_code=404, detail="Alert not found")
            if "*" not in user.get('city_access', []) and row['city'] not in user.get('city_access', []):
                raise HTTPException(status_code=403, detail="Not authorized for this city")

            await conn.execute(
                "UPDATE alerts SET resolved_at=NOW(), resolved_by=$1, resolution_note=$2 WHERE id=$3",
                user['id'], req.resolution_note, alert_id
            )
            await conn.execute(
                "INSERT INTO audit_log (user_id, action, resource, resource_id) VALUES ($1, $2, $3, $4)",
                user['id'], "RESOLVE_ALERT", "alert", alert_id
            )

    return {"success": True}

