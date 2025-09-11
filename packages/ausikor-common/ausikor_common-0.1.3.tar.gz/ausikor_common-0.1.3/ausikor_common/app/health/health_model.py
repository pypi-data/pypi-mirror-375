from pydantic import BaseModel


class HealthModel(BaseModel):
    """서비스 상태 확인 응답 모델"""
    message: str
    status: str

    
    class Config:
        from_attributes = True  # Pydantic v2+ 에서 ORM 객체 매핑을 위해 필요