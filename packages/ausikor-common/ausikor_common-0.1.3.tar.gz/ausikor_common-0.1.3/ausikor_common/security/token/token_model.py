from pydantic import BaseModel


class TokenModel(BaseModel):
    access_token: str
    token_type: str = "bearer"
    # user: UserModel  # 토큰과 함께 사용자 정보를 반환

    
    class Config:
        from_attributes = True  # Pydantic v2+ 에서 ORM 객체 매핑을 위해 필요
