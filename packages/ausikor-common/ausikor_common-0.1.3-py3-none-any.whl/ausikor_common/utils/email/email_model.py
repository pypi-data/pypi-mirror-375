import threading
import os
from typing import Optional
from pydantic import BaseModel


class EmailModel(BaseModel):
    """이메일 SMTP 설정 (싱글톤 패턴 적용)"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
                cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """SMTP 설정값 초기화"""
        # SMTP 서버 설정
        self.smtp_host: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_use_tls: bool = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        self.smtp_use_ssl: bool = os.getenv("SMTP_USE_SSL", "false").lower() == "true"
        
        # 인증 정보
        self.smtp_sender_email: str = os.getenv("SMTP_SENDER_EMAIL", "")
        self.smtp_sender_password: str = os.getenv("SMTP_SENDER_PASSWORD", "")
        self.smtp_sender_name: str = os.getenv("SMTP_SENDER_NAME", "Dover Platform")
        
        # 이메일 템플릿 설정
        self.default_charset: str = "utf-8"
        self.email_timeout: int = int(os.getenv("EMAIL_TIMEOUT", "30"))
        
        # 검증
        if not self.smtp_sender_email or not self.smtp_sender_password:
            raise ValueError("SMTP_SENDER_EMAIL과 SMTP_SENDER_PASSWORD 환경변수가 필요합니다.")
    
    def get_smtp_config(self) -> dict:
        """SMTP 설정 딕셔너리 반환"""
        return {
            "host": self.smtp_host,
            "port": self.smtp_port,
            "use_tls": self.smtp_use_tls,
            "use_ssl": self.smtp_use_ssl,
            "sender_email": self.smtp_sender_email,
            "sender_password": self.smtp_sender_password,
            "sender_name": self.smtp_sender_name,
            "timeout": self.email_timeout
        }
    
    def is_configured(self) -> bool:
        """SMTP 설정이 완료되었는지 확인"""
        return bool(self.smtp_sender_email and self.smtp_sender_password)

# ✅ 싱글톤 인스턴스 생성
email_provider = EmailModel()