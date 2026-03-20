import time
import uuid
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from pydantic import BaseModel
from server.config.settings import settings
from server.db.connection import get_connection
from server.api.middleware import limiter
import bcrypt

router = APIRouter()

# Pre-computed hash for timing-safe dummy check on non-existent users (SEC-8)
_DUMMY_HASH = bcrypt.hashpw(b"dummy-timing-guard", bcrypt.gensalt()).decode()
_IS_SECURE = settings.environment != "development"  # SEC-2: allow HTTP in dev

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
@limiter.limit(f"{settings.auth_rate_limit_per_minute}/minute")
async def login(req: LoginRequest, response: Response, request: Request):
    ip_addr = request.client.host if request.client else "0.0.0.0"
    
    query = """SELECT id, email, password_hash, name, role, city_access,
               is_active, failed_attempts, locked_until, refresh_token_hash,
               last_login, last_login_ip FROM users WHERE email = $1"""
    async with get_connection() as conn:
        user = await conn.fetchrow(query, req.email)

        # SEC-8: Always run bcrypt to prevent timing-based email enumeration
        if not user or not user['is_active']:
            bcrypt.checkpw(b"dummy-timing-guard", _DUMMY_HASH.encode())
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
        if user['locked_until'] and user['locked_until'] > datetime.now(timezone.utc):
            raise HTTPException(status_code=423, detail="Account locked")
            
        # Verify password
        isValid = bcrypt.checkpw(req.password.encode('utf-8'), user['password_hash'].encode('utf-8'))
        
        if not isValid:
            failed = user['failed_attempts'] + 1
            if failed >= settings.auth_lockout_attempts:
                lockout = datetime.now(timezone.utc) + timedelta(minutes=settings.auth_lockout_minutes)
                await conn.execute("UPDATE users SET failed_attempts=$1, locked_until=$2 WHERE id=$3", failed, lockout, user['id'])
            else:
                await conn.execute("UPDATE users SET failed_attempts=$1 WHERE id=$2", failed, user['id'])
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
        # Success
        new_refresh_uuid = str(uuid.uuid4())
        new_refresh = f"{user['id']}:{new_refresh_uuid}"
        refresh_hash = bcrypt.hashpw(new_refresh_uuid.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        await conn.execute(
            """UPDATE users SET failed_attempts=0, locked_until=NULL, 
               last_login=NOW(), last_login_ip=$1, refresh_token_hash=$2 WHERE id=$3""",
            ip_addr, refresh_hash, user['id']
        )
        
        # Issue JWT
        exp = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
        payload = {
            "sub": str(user['id']),
            "role": user['role'],
            "city_access": user['city_access'],
            "exp": exp
        }
        access_token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        
        response.set_cookie(key="access_token", value=access_token, httponly=True, samesite="lax", secure=_IS_SECURE)
        response.set_cookie(key="refresh_token", value=new_refresh, httponly=True, samesite="lax", secure=_IS_SECURE, max_age=settings.refresh_token_expire_days * 86400)
        # NEW-2: Separate non-httpOnly cookie for WS auth (JS must read this)
        response.set_cookie(key="ws_token", value=access_token, httponly=False, samesite="strict", secure=_IS_SECURE, max_age=settings.access_token_expire_minutes * 60)
        
        return {
            "success": True,
            "role": user['role'],
            "city_access": user['city_access']
        }

@router.post("/refresh")
@limiter.limit(f"{settings.auth_rate_limit_per_minute}/minute")
async def refresh(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")
        
    parts = refresh_token.split(':')
    if len(parts) != 2:
        raise HTTPException(status_code=401, detail="Invalid refresh token format")
        
    user_id_str, token_uuid = parts
    
    query = """SELECT id, email, name, role, city_access, is_active,
               refresh_token_hash FROM users WHERE id = $1"""
    user = None
    async with get_connection() as conn:
        try:
            user = await conn.fetchrow(query, user_id_str)
        except Exception:
            raise HTTPException(status_code=401, detail="User not found")
            
        if not user or not user['refresh_token_hash']:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        # SEC-H3: reject deactivated users from refreshing tokens
        if not user['is_active']:
            raise HTTPException(status_code=401, detail="Account deactivated")

        if not bcrypt.checkpw(token_uuid.encode('utf-8'), user['refresh_token_hash'].encode('utf-8')):
            raise HTTPException(status_code=401, detail="Invalid refresh token")
            
        new_refresh_uuid = str(uuid.uuid4())
        new_refresh = f"{user['id']}:{new_refresh_uuid}"
        refresh_hash = bcrypt.hashpw(new_refresh_uuid.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        await conn.execute("UPDATE users SET refresh_token_hash=$1 WHERE id=$2", refresh_hash, user['id'])
        
        exp = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
        payload = {
            "sub": str(user['id']),
            "role": user['role'],
            "city_access": user['city_access'],
            "exp": exp
        }
        access_token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        
        response.set_cookie(key="access_token", value=access_token, httponly=True, samesite="lax", secure=_IS_SECURE)
        response.set_cookie(key="refresh_token", value=new_refresh, httponly=True, samesite="lax", secure=_IS_SECURE, max_age=settings.refresh_token_expire_days * 86400)
        response.set_cookie(key="ws_token", value=access_token, httponly=False, samesite="strict", secure=_IS_SECURE, max_age=settings.access_token_expire_minutes * 60)
        
        return {"success": True}

@router.post("/logout")
async def logout(request: Request, response: Response):
    access_token = request.cookies.get("access_token")
    if access_token:
        try:
            payload = jwt.decode(access_token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm], options={"verify_exp": False})
            user_id = payload.get("sub")
            if user_id:
                async with get_connection() as conn:
                    await conn.execute("UPDATE users SET refresh_token_hash=NULL WHERE id=$1", user_id)
        except Exception:
            pass
            
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    response.delete_cookie("ws_token")
    return {"success": True}
