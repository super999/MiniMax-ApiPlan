from datetime import datetime, timezone
from typing import Optional

from jose import jwt

from core.settings import settings
from core.logger import get_logger

logger = get_logger(__name__)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        import bcrypt
        password_bytes = plain_password[:72].encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception as e:
        logger.error(f"密码验证失败: {e}")
        return False


def get_password_hash(password: str) -> str:
    import bcrypt
    password_bytes = password[:72].encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def create_access_token(subject: int, expires_delta: Optional[int] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + settings.jwt.access_token_expire_delta

    to_encode = {"sub": str(subject), "exp": expire}
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt.secret_key,
        algorithm=settings.jwt.algorithm,
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(
            token,
            settings.jwt.secret_key,
            algorithms=[settings.jwt.algorithm],
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return int(user_id)
    except jwt.JWTError as e:
        logger.warning(f"JWT 解码失败: {e}")
        return None
