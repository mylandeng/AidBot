import hashlib
import hmac
import secrets
from datetime import timezone, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.access_key import AccessKey
from app.models.conversation import utcnow
from app.schemas.access_key import AccessKeyCreateRequest, AccessKeyDuration, AccessKeyResponse, AccessKeyUpdateRequest
from app.schemas.auth import CurrentUser


KEY_PREFIX_LENGTH = 18


class AccessKeyService:
    def create(self, request: AccessKeyCreateRequest, current_user: CurrentUser, db: Session) -> tuple[AccessKey, str]:
        plain_key = f"aidbot_live_{secrets.token_urlsafe(24)}"
        item = AccessKey(
            name=request.name.strip(),
            key_prefix=plain_key[:KEY_PREFIX_LENGTH],
            key_hash=self._hash_key(plain_key),
            expires_at=self._expires_at(request.expires_in),
            max_requests=request.max_requests,
            max_tokens=request.max_tokens,
            note=request.note.strip(),
            created_by=current_user.id,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item, plain_key

    def list(self, db: Session, include_deleted: bool = False) -> list[AccessKey]:
        query = select(AccessKey).order_by(AccessKey.created_at.desc())
        if not include_deleted:
            query = query.where(AccessKey.status != "deleted")
        return list(db.scalars(query).all())

    def update(self, key_id: str, request: AccessKeyUpdateRequest, db: Session) -> AccessKey:
        item = self.get_existing(key_id, db)
        if item.status == "deleted":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Access key has been deleted")
        if request.name is not None:
            item.name = request.name.strip()
        if request.expires_in is not None:
            item.expires_at = self._expires_at(request.expires_in)
        if request.max_requests is not None:
            item.max_requests = request.max_requests
        if request.max_tokens is not None:
            item.max_tokens = request.max_tokens
        if request.note is not None:
            item.note = request.note.strip()
        item.updated_at = utcnow()
        db.commit()
        db.refresh(item)
        return item

    def disable(self, key_id: str, db: Session) -> AccessKey:
        item = self.get_existing(key_id, db)
        if item.status == "deleted":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Access key has been deleted")
        item.status = "disabled"
        item.disabled_at = utcnow()
        item.updated_at = utcnow()
        db.commit()
        db.refresh(item)
        return item

    def enable(self, key_id: str, db: Session) -> AccessKey:
        item = self.get_existing(key_id, db)
        if item.status == "deleted":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Access key has been deleted")
        item.status = "active"
        item.disabled_at = None
        item.updated_at = utcnow()
        db.commit()
        db.refresh(item)
        return item

    def delete(self, key_id: str, db: Session) -> AccessKey:
        item = self.get_existing(key_id, db)
        item.status = "deleted"
        item.deleted_at = utcnow()
        item.updated_at = utcnow()
        db.commit()
        db.refresh(item)
        return item

    def authenticate(self, plain_key: str, db: Session) -> AccessKey:
        key = plain_key.strip()
        if len(key) < KEY_PREFIX_LENGTH:
            raise self._invalid_key()
        item = db.scalar(select(AccessKey).where(AccessKey.key_prefix == key[:KEY_PREFIX_LENGTH]))
        if item is None or not hmac.compare_digest(item.key_hash, self._hash_key(key)):
            raise self._invalid_key()
        if item.status == "deleted":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"code": "KEY_DELETED", "message": "访问码已删除，请联系管理员。"})
        if item.status == "disabled":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"code": "KEY_DISABLED", "message": "访问码已禁用，请联系管理员。"})
        if self._is_expired(item):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"code": "KEY_EXPIRED", "message": "访问码已过期，请联系管理员。"})
        if item.max_requests is not None and item.used_requests >= item.max_requests:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": "QUOTA_EXCEEDED", "message": "访问码额度已用完，请联系管理员。"})
        item.last_used_at = utcnow()
        item.updated_at = utcnow()
        db.commit()
        db.refresh(item)
        return item

    def record_request(self, key_id: str | None, db: Session) -> None:
        if not key_id:
            return
        item = db.get(AccessKey, key_id)
        if item is None:
            return
        item.used_requests += 1
        item.last_used_at = utcnow()
        item.updated_at = utcnow()
        db.commit()

    def ensure_session_key_is_usable(self, key_id: str | None, db: Session) -> None:
        if not key_id:
            return
        item = self.get_existing(key_id, db)
        if item.status == "deleted":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"code": "KEY_DELETED", "message": "访问码已删除，请联系管理员。"})
        if item.status == "disabled":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"code": "KEY_DISABLED", "message": "访问码已禁用，请联系管理员。"})
        if self._is_expired(item):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"code": "KEY_EXPIRED", "message": "访问码已过期，请联系管理员。"})
        if item.max_requests is not None and item.used_requests >= item.max_requests:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": "QUOTA_EXCEEDED", "message": "访问码额度已用完，请联系管理员。"})

    def get_existing(self, key_id: str, db: Session) -> AccessKey:
        item = db.get(AccessKey, key_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Access key not found")
        return item

    def response(self, item: AccessKey) -> AccessKeyResponse:
        return AccessKeyResponse(
            id=item.id,
            name=item.name,
            key_prefix=item.key_prefix,
            status=item.status,
            expires_at=item.expires_at.isoformat(),
            max_requests=item.max_requests,
            used_requests=item.used_requests,
            max_tokens=item.max_tokens,
            used_tokens=item.used_tokens,
            note=item.note,
            last_used_at=item.last_used_at.isoformat() if item.last_used_at else None,
            created_at=item.created_at.isoformat(),
            updated_at=item.updated_at.isoformat(),
        )

    def _hash_key(self, plain_key: str) -> str:
        return hmac.new(settings.auth_secret_key.encode("utf-8"), plain_key.encode("utf-8"), hashlib.sha256).hexdigest()

    def _expires_at(self, duration: AccessKeyDuration):
        days = {"7d": 7, "30d": 30, "180d": 180, "365d": 365}[duration]
        return utcnow() + timedelta(days=days)

    def _is_expired(self, item: AccessKey) -> bool:
        expires_at = item.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return expires_at <= utcnow()

    def _invalid_key(self) -> HTTPException:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"code": "INVALID_KEY", "message": "访问码无效。"})
