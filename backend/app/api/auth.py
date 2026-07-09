from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, get_current_user, verify_seed_password
from app.schemas.auth import CurrentUser, KeyLoginRequest, LoginRequest, LoginResponse
from app.services.access_key_service import AccessKeyService
from sqlalchemy.orm import Session

router = APIRouter()
access_key_service = AccessKeyService()


@router.get("/status")
def auth_status() -> dict[str, str]:
    return {"status": "configured", "provider": "seed_admin"}


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest) -> LoginResponse:
    if not verify_seed_password(request.email, request.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    user = CurrentUser(
        id="seed-admin",
        email=settings.seed_admin_email,
        name=settings.seed_admin_name,
        roles=["admin", "support"],
    )
    token = create_access_token(
        subject=user.id,
        claims={
            "email": user.email,
            "name": user.name,
            "roles": user.roles,
            "auth_method": "password",
        },
    )
    return LoginResponse(access_token=token, expires_in=settings.auth_token_ttl_seconds, user=user)


@router.post("/admin/login", response_model=LoginResponse)
def admin_login(request: LoginRequest) -> LoginResponse:
    return login(request)


@router.post("/key-login", response_model=LoginResponse)
def key_login(request: KeyLoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    item = access_key_service.authenticate(request.access_key, db)
    user = CurrentUser(
        id=f"access-key:{item.id}",
        email="",
        name=item.name,
        roles=["user"],
        auth_method="access_key",
        key_id=item.id,
        key_expires_at=item.expires_at.isoformat(),
    )
    token = create_access_token(
        subject=user.id,
        claims={
            "email": "",
            "name": user.name,
            "roles": user.roles,
            "auth_method": user.auth_method,
            "key_id": user.key_id,
            "key_expires_at": user.key_expires_at,
        },
    )
    return LoginResponse(access_token=token, expires_in=settings.auth_token_ttl_seconds, user=user)


@router.get("/me", response_model=CurrentUser)
def me(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    return current_user
