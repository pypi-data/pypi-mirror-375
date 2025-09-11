import threading
from sqlalchemy.orm import declarative_base

try:
    from app.domain.user.entity.user_entity import UserEntity  # optional, may not exist in this package
except Exception:
    UserEntity = None


Base = declarative_base()

class DBFactory:
    """ORM 테이블 모델을 초기화하는 싱글톤 + 팩토리 클래스"""
    
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """ORM 테이블을 등록"""
        self.models = []
        if UserEntity is not None:
            self.register(UserEntity)

    def register(self, model):
        """새로운 ORM 모델을 등록"""
        if model not in self.models:
            self.models.append(model)

    def get_models(self):
        """등록된 모든 ORM 모델을 반환"""
        return self.models

# ✅ 싱글톤 인스턴스 생성
db_factory = DBFactory()