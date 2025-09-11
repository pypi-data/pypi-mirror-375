"""
비동기 데이터베이스 연결 및 세션 관리
"""

import os
from datetime import datetime, timedelta, timezone
import asyncio
try:
    from dotenv import load_dotenv
except Exception:
    def load_dotenv(*args, **kwargs):
        return False
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator, Any, Dict, Optional
import psycopg2
from psycopg2.extras import Json
from jose import jwt

# 환경변수 로드 (로컬에서만)
if os.getenv("ENV", "local") == "local":
    load_dotenv()

# 데이터베이스 URL (asyncpg 포맷이어야 함)
DATABASE_URL = os.getenv("DATABASE_URL")

print("📴📵🚸🚼 DATABASE_URL in runtime:", DATABASE_URL)

if not DATABASE_URL:
    raise ValueError("DATABASE_URL 환경변수가 없습니다.")

# 비동기 엔진 생성
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# 비동기 세션팩토리
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

# Base 선언
Base = declarative_base()

# 세션 제공 의존성 함수
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# 테이블 자동 생성 제거됨 (Base.metadata.create_all 삭제)

# ------------------------------
# Google OAuth 동기 upsert 유틸
# ------------------------------

def _build_dsn() -> str:
    dsn = (
        os.getenv("DATABASE_URL")
        or os.getenv("POSTGRES_URL")
        or os.getenv("RAILWAY_DATABASE_URL")
        or ""
    )
    if not dsn:
        raise RuntimeError("DATABASE_URL not configured")

    # SQLAlchemy async URL을 psycopg2 호환으로 보정
    if dsn.startswith("postgresql+asyncpg://"):
        dsn = dsn.replace("postgresql+asyncpg://", "postgresql://", 1)

    # sslmode=require 보장 (외부 접속 환경 호환)
    if "sslmode=" not in dsn:
        if "?" in dsn:
            dsn = f"{dsn}&sslmode=require"
        else:
            dsn = f"{dsn}?sslmode=require"
    return dsn


def _decode_id_token_unverified(id_token_jwt: str) -> Dict[str, Any]:
    if not id_token_jwt:
        return {}
    try:
        return jwt.get_unverified_claims(id_token_jwt) or {}
    except Exception:
        return {}


def upsert_google_login(
    *,
    token_response: Dict[str, Any],
    userinfo: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """
    google_oauth_accounts / google_oauth_tokens 에 upsert & insert.
    반환값: account_id (uuid) 또는 None
    """
    access_token = token_response.get("access_token")
    refresh_token = token_response.get("refresh_token")
    id_token_jwt = token_response.get("id_token")
    token_type = token_response.get("token_type")
    scope = token_response.get("scope")
    expires_in = token_response.get("expires_in")  # seconds

    claims = _decode_id_token_unverified(id_token_jwt or "")

    def _pick(*keys: str) -> Optional[str]:
        for k in keys:
            if userinfo and userinfo.get(k) is not None:
                return userinfo.get(k)  # type: ignore[return-value]
            if claims.get(k) is not None:
                return claims.get(k)  # type: ignore[return-value]
        return None

    google_sub = _pick("sub")
    if not google_sub:
        return None

    email = _pick("email")
    email_verified = _pick("email_verified")
    name = _pick("name")
    given_name = _pick("given_name")
    family_name = _pick("family_name")
    picture_url = _pick("picture", "picture_url")
    profile_url = _pick("profile", "profile_url")
    locale = _pick("locale")
    hd = _pick("hd")

    updated_at_claim: Optional[str] = None

    now = datetime.now(timezone.utc)
    expires_at: Optional[datetime] = None
    if isinstance(expires_in, (int, float)):
        expires_at = now + timedelta(seconds=int(expires_in))

    dsn = _build_dsn()
    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO google_oauth_accounts (
                  id, google_sub, email, email_verified, name, given_name, family_name,
                  picture_url, profile_url, locale, hd, updated_at_claim,
                  userinfo_json, id_token_claims, created_at, updated_at, last_login_at
                ) VALUES (
                  app_gen_uuid(), %s, %s, %s, %s, %s, %s,
                  %s, %s, %s, %s, %s,
                  %s, %s, %s, %s, %s
                )
                ON CONFLICT (google_sub) DO UPDATE SET
                  email = EXCLUDED.email,
                  email_verified = EXCLUDED.email_verified,
                  name = EXCLUDED.name,
                  given_name = EXCLUDED.given_name,
                  family_name = EXCLUDED.family_name,
                  picture_url = EXCLUDED.picture_url,
                  profile_url = EXCLUDED.profile_url,
                  locale = EXCLUDED.locale,
                  hd = EXCLUDED.hd,
                  updated_at_claim = EXCLUDED.updated_at_claim,
                  userinfo_json = EXCLUDED.userinfo_json,
                  id_token_claims = EXCLUDED.id_token_claims,
                  updated_at = now(),
                  last_login_at = now()
                RETURNING id;
                """,
                (
                    google_sub,
                    email,
                    email_verified,
                    name,
                    given_name,
                    family_name,
                    picture_url,
                    profile_url,
                    locale,
                    hd,
                    updated_at_claim,
                    Json(userinfo or {}),
                    Json(claims or {}),
                    now,
                    now,
                    now,
                ),
            )
            account_id = cur.fetchone()[0]

            cur.execute(
                "UPDATE google_oauth_tokens SET is_active = FALSE WHERE account_id = %s",
                (account_id,),
            )

            cur.execute(
                """
                INSERT INTO google_oauth_tokens (
                  id, account_id, access_token, refresh_token, id_token_jwt,
                  token_type, scope, expires_at, issued_at, token_response_json,
                  last_refreshed_at, revoked_at, created_at, updated_at, is_active
                ) VALUES (
                  app_gen_uuid(), %s, %s, %s, %s,
                  %s, %s, %s, %s, %s,
                  %s, NULL, %s, %s, TRUE
                );
                """,
                (
                    account_id,
                    access_token,
                    refresh_token,
                    id_token_jwt,
                    token_type,
                    scope,
                    expires_at,
                    now,
                    Json(token_response or {}),
                    now,
                    now,
                    now,
                ),
            )
            return str(account_id)


async def upsert_google_login_async(
    *,
    token_response: Dict[str, Any],
    userinfo: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """비동기 FastAPI 환경에서 블로킹 방지를 위한 래퍼."""
    return await asyncio.to_thread(
        upsert_google_login,
        token_response=token_response,
        userinfo=userinfo,
    )
