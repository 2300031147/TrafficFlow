from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from typing import Optional
import uuid as _uuid
from server.api.dependencies import get_current_user, require_role, city_scope_check
from server.db.queries import junctions as jq
from server.db.queries import counts as cq
from server.db.queries import signals as sq
from server.db.connection import get_connection

router = APIRouter()

class OverrideRequest(BaseModel):
    phase: str
    duration: int
    reason: Optional[str] = None

@router.get("/")
async def list_junctions(status: Optional[str] = None, user: dict = Depends(get_current_user)):
    return await jq.get_all_junctions(user['city_access'])

@router.get("/{junction_id}")
async def get_junction(junction_id: str, user: dict = Depends(get_current_user)):
    await city_scope_check(junction_id, user)
    j = await jq.get_junction_by_id(junction_id)
    if not j:
        raise HTTPException(status_code=404, detail="Junction not found")
        
    latest_counts = await cq.get_latest_counts(junction_id)
    return {
        "junction": j,
        "latest_counts": latest_counts
    }

@router.get("/{junction_id}/counts/live")
async def get_live_counts(junction_id: str, user: dict = Depends(get_current_user)):
    await city_scope_check(junction_id, user)
    return await cq.get_latest_counts(junction_id)

@router.get("/{junction_id}/counts/history")
async def get_history_counts(junction_id: str, minutes: int = Query(60, ge=1, le=1440), user: dict = Depends(get_current_user)):
    await city_scope_check(junction_id, user)
    return await cq.get_count_history(junction_id, minutes)

@router.get("/{junction_id}/signals/history")
async def get_signal_history(junction_id: str, hours: int = Query(24, ge=1, le=168), user: dict = Depends(get_current_user)):
    await city_scope_check(junction_id, user)
    return await sq.get_signal_history(junction_id, hours)

@router.get("/{junction_id}/override/active")
async def get_active_override(junction_id: str, user: dict = Depends(get_current_user)):
    await city_scope_check(junction_id, user)
    return await sq.get_active_override(junction_id)

@router.post("/{junction_id}/override", dependencies=[Depends(require_role("operator", "admin", "superadmin"))])
async def execute_override(junction_id: str, req: OverrideRequest, request: Request, user: dict = Depends(get_current_user)):
    await city_scope_check(junction_id, user)
    
    if req.phase not in ("NS_GREEN", "EW_GREEN", "ALL_RED"):
        raise HTTPException(status_code=400, detail="Invalid phase")
    if not (10 <= req.duration <= 120):
        raise HTTPException(status_code=400, detail="Duration must be between 10 and 120 seconds")
        
    async with get_connection() as conn:
        async with conn.transaction():
            # SEC-11: Prevent stacking overrides
            existing = await conn.fetchrow("""
                SELECT id FROM overrides
                WHERE junction_id = $1 AND cancelled_at IS NULL
                AND created_at + (duration || ' seconds')::interval > NOW()
            """, junction_id)
            if existing:
                raise HTTPException(status_code=409, detail="Override already active. Cancel it first.")

            # SEC-M4: Capture operator IP address
            ip_addr = request.client.host if request.client else None
            await conn.execute("""
                INSERT INTO overrides (junction_id, operator_id, phase, duration, reason, ip_address)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, junction_id, user['id'], req.phase, req.duration, req.reason, ip_addr)

            await conn.execute("""
                INSERT INTO audit_log (user_id, action, resource, resource_id)
                VALUES ($1, $2, $3, $4)
            """, user['id'], "CREATE_OVERRIDE", "junction", junction_id)
            
    return {"success": True}

@router.delete("/{junction_id}/override", dependencies=[Depends(require_role("operator", "admin", "superadmin"))])
async def cancel_override(junction_id: str, user: dict = Depends(get_current_user)):
    await city_scope_check(junction_id, user)
    
    async with get_connection() as conn:
        async with conn.transaction():
            await conn.execute("""
                UPDATE overrides SET cancelled_at=NOW(), cancelled_by=$1
                WHERE junction_id=$2 AND cancelled_at IS NULL
            """, user['id'], junction_id)
            
            await conn.execute("""
                INSERT INTO audit_log (user_id, action, resource, resource_id)
                VALUES ($1, $2, $3, $4)
            """, user['id'], "CANCEL_OVERRIDE", "junction", junction_id)
            
    return {"success": True}
