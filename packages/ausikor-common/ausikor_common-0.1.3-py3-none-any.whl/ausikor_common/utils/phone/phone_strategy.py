from abc import ABC, abstractmethod
import re

class PhoneNumberStrategy(ABC):
    """전화번호 포맷팅 전략 인터페이스"""
    
    @abstractmethod
    def format(self, phone_number: str) -> str:
        pass

class KoreanPhoneNumberStrategy(PhoneNumberStrategy):
    """한국 전화번호 포맷팅 전략"""
    
    def format(self, phone_number: str) -> str:
        """한국 전화번호에 하이픈 추가"""
        if len(phone_number) <= 2:
            return phone_number
            
        if phone_number.startswith("02"):
            return self._format_seoul_number(phone_number)
        else:
            return self._format_mobile_number(phone_number)
    
    def _format_seoul_number(self, phone_number: str) -> str:
        """서울 지역번호 포맷팅"""
        if 3 <= len(phone_number) <= 5:
            return re.sub(r'(\d{2})(\d{1,3})', r'\1-\2', phone_number)
        elif 6 <= len(phone_number) <= 9:
            return re.sub(r'(\d{2})(\d{3})(\d{1,4})', r'\1-\2-\3', phone_number)
        elif len(phone_number) == 10:
            return re.sub(r'(\d{2})(\d{4})(\d{4})', r'\1-\2-\3', phone_number)
        return phone_number
    
    def _format_mobile_number(self, phone_number: str) -> str:
        """휴대폰 번호 포맷팅"""
        if 3 <= len(phone_number) <= 6:
            return re.sub(r'(\d{3})(\d{1,3})', r'\1-\2', phone_number)
        elif 7 <= len(phone_number) <= 10:
            return re.sub(r'(\d{3})(\d{3})(\d{1,4})', r'\1-\2-\3', phone_number)
        elif len(phone_number) == 11:
            return re.sub(r'(\d{3})(\d{4})(\d{4})', r'\1-\2-\3', phone_number)
        return phone_number


class SpacedPhoneNumberStrategy(KoreanPhoneNumberStrategy):
    """공백이 포함된 하이픈 전화번호 포맷팅 전략"""
    
    def _format_seoul_number(self, phone_number: str) -> str:
        """서울 지역번호 포맷팅 (공백 포함)"""
        if 3 <= len(phone_number) <= 5:
            return re.sub(r'(\d{2})(\d{1,3})', r'\1 - \2', phone_number)
        elif 6 <= len(phone_number) <= 9:
            return re.sub(r'(\d{2})(\d{3})(\d{1,4})', r'\1 - \2 - \3', phone_number)
        elif len(phone_number) == 10:
            return re.sub(r'(\d{2})(\d{4})(\d{4})', r'\1 - \2 - \3', phone_number)
        return phone_number
    
    def _format_mobile_number(self, phone_number: str) -> str:
        """휴대폰 번호 포맷팅 (공백 포함)"""
        if 3 <= len(phone_number) <= 6:
            return re.sub(r'(\d{3})(\d{1,3})', r'\1 - \2', phone_number)
        elif 7 <= len(phone_number) <= 10:
            return re.sub(r'(\d{3})(\d{3})(\d{1,4})', r'\1 - \2 - \3', phone_number)
        elif len(phone_number) == 11:
            return re.sub(r'(\d{3})(\d{4})(\d{4})', r'\1 - \2 - \3', phone_number)
        return phone_number


class PhoneNumberFormatter:
    """전화번호 포맷터 (Context 클래스)"""
    
    def __init__(self, strategy: PhoneNumberStrategy = None):
        self._strategy = strategy or KoreanPhoneNumberStrategy()
    
    def set_strategy(self, strategy: PhoneNumberStrategy):
        """포맷팅 전략 변경"""
        self._strategy = strategy
    
    def format(self, phone_number: str) -> str:
        """전화번호 포맷팅"""
        return self._strategy.format(phone_number)
    
    @staticmethod
    def format_cell_phone(cell_phone: str) -> str:
        """휴대폰 번호에 하이픈 추가 (기존 호환성)"""
        if not cell_phone:
            return ""
        if len(cell_phone) >= 11:
            return f"{cell_phone[:3]}-{cell_phone[3:7]}-{cell_phone[7:]}"
        else:
            return f"{cell_phone[:3]}-{cell_phone[3:6]}-{cell_phone[6:]}"
        
