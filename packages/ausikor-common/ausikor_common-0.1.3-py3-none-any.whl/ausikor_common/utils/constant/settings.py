import os
from dotenv import load_dotenv

# Railway 환경이 아닌 경우에만 .env 파일을 로드
if os.getenv("RAILWAY_ENVIRONMENT") != "true":
    load_dotenv()


class Settings:
    # Gateway 설정
    PORT = int(os.getenv("PORT", 8080))
    SERVICE_NAME = os.getenv("SERVICE_NAME", "gateway")

    # 백엔드 서비스 URL들
    ACCOUNT_SERVICE_URL = os.getenv("ACCOUNT_SERVICE_URL")
    CHAT_SERVICE_URL = os.getenv("CHAT_SERVICE_URL")
    CONTRACT_SERVICE_URL = os.getenv("CONTRACT_SERVICE_URL")
    FINANCE_SERVICE_URL = os.getenv("FINANCE_SERVICE_URL")
    ORGANIZATION_SERVICE_URL = os.getenv("ORGANIZATION_SERVICE_URL")
    POST_SERVICE_URL = os.getenv("POST_SERVICE_URL")
    PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL")

    # Google OAuth
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
    GOOGLE_TOKEN_URL = os.getenv("GOOGLE_TOKEN_URL", "https://oauth2.googleapis.com/token")
    GOOGLE_USER_INFO_URL = os.getenv("GOOGLE_USER_INFO_URL", "https://www.googleapis.com/oauth2/v2/userinfo")

    # JWT
    JWT_SECRET = os.getenv("JWT_SECRET")

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")


# 인스턴스를 전역으로 생성하여 import 시 바로 사용 가능
settings = Settings()