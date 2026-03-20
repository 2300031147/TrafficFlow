from fastapi import Header, HTTPException, Depends, Request
import jwt
from typing import Optional, List
from server.config.settings import settings
from server.db.queries.junctions import get_junction_by_id
import bcrypt

async def get_current_user(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
            
        return {
            "id": user_id,
            "role": payload.get("role"),
            "city_access": payload.get("city_access", [])
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_role(*roles):
    async def role_checker(user: dict = Depends(get_current_user)):
        if user["role"] not in roles:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return user
    return role_checker

async def city_scope_check(junction_id: str, current_user: dict):
    j = await get_junction_by_id(junction_id)
    if not j:
        raise HTTPException(status_code=404, detail="Junction not found")
        
    city = j['city']
    access = current_user.get('city_access', [])
    if "*" not in access and city not in access:
        raise HTTPException(status_code=403, detail="Not authorized for this city")

async def verify_device_token_route(request: Request) -> str:
    """Verifies Pi node authentication headers."""
    device_token = request.headers.get("X-Device-Token")
    if not device_token:
        raise HTTPException(status_code=401, detail="X-Device-Token header missing or invalid")
        
    junction_id = request.path_params.get("junction_id")
    if not junction_id:
        raise HTTPException(status_code=400, detail="junction_id path parameter required")
        
    isValid = False
    
    # Needs to match a hashed token in DB.
    # We fetch the junction, get the token hash, verify using bcrypt
    j = await get_junction_by_id(junction_id)
    if j and j['api_token_hash']:
        try:
            isValid = bcrypt.checkpw(device_token.encode('utf-8'), j['api_token_hash'].encode('utf-8'))
        except Exception:
            pass

    if not isValid:
        raise HTTPException(status_code=401, detail="Invalid device token")
        
    return junction_id

async def verify_device_token_body(request: Request) -> str:
    """Verifies Pi device token for ingest route. Reads junction_id from
    Starlette's cached body (request._body) to avoid double-read issue
    since FastAPI has already consumed the stream for Pydantic parsing."""
    device_token = request.headers.get("X-Device-Token")
    if not device_token:
        raise HTTPException(status_code=401, detail="X-Device-Token header missing or invalid")
    try:
        # Starlette caches the body after first read — safe to call again
        body = await request.body()
        import json as _json
        parsed = _json.loads(body)
        junction_id = parsed.get('junction_id')
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid body")

    if not junction_id:
         raise HTTPException(status_code=400, detail="junction_id body parameter required")
         
    j = await get_junction_by_id(junction_id)
    isValid = False
    if j and j['api_token_hash']:
        try:
            isValid = bcrypt.checkpw(device_token.encode('utf-8'), j['api_token_hash'].encode('utf-8'))
        except Exception:
            pass
            
    if not isValid:
        raise HTTPException(status_code=401, detail="Invalid device token")
        
    return junction_id
