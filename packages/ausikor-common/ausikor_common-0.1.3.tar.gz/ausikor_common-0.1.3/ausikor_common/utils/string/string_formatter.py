
import re

class StringFormatter:
    """문자열 포맷팅 유틸리티 클래스"""
    
    @staticmethod
    def to_camel_case(text: str) -> str:
        """스네이크 케이스를 카멜 케이스로 변환"""
        parts = re.split(pattern=r"[\s_]+", string=text)
        return parts[0] + "".join(part.title() for part in parts[1:])
    
    @staticmethod
    def camel_to_snake(text: str) -> str:
        """카멜 케이스를 스네이크 케이스로 변환"""
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', text).lower()
    
    @staticmethod
    def to_camel_case_dict(data: dict) -> dict:
        """딕셔너리 키를 카멜 케이스로 변환"""
        return {StringFormatter.to_camel_case(key): value for key, value in data.items()}
    
    @staticmethod
    def hide_name_with_asterisk(name: str) -> str:
        """이름을 별표로 마스킹"""
        if not name:
            return ""
        length = len(name)
        if length == 2:
            return name[0] + "*"
        else:
            return name[0] + "*" * (length - 2) + name[length - 1]

class String:
    @staticmethod
    def to_camel_case(text: str) -> str:
        parts = re.split(r"[\s_]+", text)
        return parts[0] + "".join(part.title() for part in parts[1:])
    
    @staticmethod
    def to_snake_case(text: str) -> str:
        return re.sub(r'(?<!^)(?=[A-Z])', '_', text).lower()

    @staticmethod
    def hide_name_with_aster(name: str) -> str:
        if not name:
            return ""
        length = len(name)
        return name[0] + "*" * (length - 2) + name[-1] if length > 2 else name[0] + "*"