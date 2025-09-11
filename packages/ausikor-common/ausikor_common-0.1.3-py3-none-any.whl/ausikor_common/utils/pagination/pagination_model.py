

from pydantic import BaseModel, ConfigDict


class PaginationModel(BaseModel):
    """페이지네이션 기본값 관리"""
    
    model_config = ConfigDict(
        frozen=True,
        validate_assignment=True,
        extra="forbid"
    )
    
    # 페이지네이션 기본값들
    default_block_number: int = 1
    default_block_size: int = 10
    default_page_number: int = 1
    default_admin_page_size: int = 15
    default_page_size: int = 10
    default_limit: int = 120
    default_product_list_page_size: int = 100