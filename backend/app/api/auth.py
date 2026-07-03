from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import settings
from app.core.security import create_access_token, get_current_user, verify_seed_password
from app.schemas.auth import CurrentUser, LoginRequest, LoginResponse

router = APIRouter()


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
        },
    )
    return LoginResponse(access_token=token, expires_in=settings.auth_token_ttl_seconds, user=user)


@router.get("/me", response_model=CurrentUser)
def me(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    return current_user
