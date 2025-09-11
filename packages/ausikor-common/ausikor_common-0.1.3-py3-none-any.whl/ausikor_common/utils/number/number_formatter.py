
from typing import Any, Union

class NumberFormatter:
    """숫자 포맷팅 유틸리티 클래스"""
    
    @staticmethod
    def format_number(value: Any) -> str:
        """숫자를 포맷팅 (소수점 처리)"""
        if value is not None:
            value = float(value)
            return str(int(value)) if value.is_integer() else str(round(value, 1))
        return ''
    
    @staticmethod
    def remove_trailing_zero(value: Any) -> Union[str, None]:
        """소수점 뒤 0 제거"""
        if value is not None:
            value = float(value)
            return str(int(value)) if value.is_integer() else str(value)
        return None
    
    @staticmethod
    def convert_bytes(num: float) -> str:
        """바이트를 읽기 쉬운 단위로 변환"""
        for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
            if num < 1024.0:
                return f"{num:3.1f}{unit}"
            num /= 1024.0
        return f"{num:3.1f}PB"