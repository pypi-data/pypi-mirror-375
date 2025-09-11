from abc import ABC, abstractmethod
import re

class PhoneService:
    @staticmethod
    def attach_hyphen_to_cell_phone(cell_phone: str) -> str:
        if not cell_phone:
            return ""
        return f"{cell_phone[:3]}-{cell_phone[3:7]}-{cell_phone[7:]}" if len(cell_phone) >= 11 else f"{cell_phone[:3]}-{cell_phone[3:6]}-{cell_phone[6:]}"
    
    @staticmethod
    def format_phone_number(phone_number: str, spacing: bool = False) -> str:
        separator = " - " if spacing else "-"
        
        if len(phone_number) <= 2:
            return phone_number
        if phone_number.startswith("02"):
            patterns = [(r'(\d{2})(\d{1,3})', r'\1' + separator + r'\2'),
                        (r'(\d{2})(\d{3})(\d{1,4})', r'\1' + separator + r'\2' + separator + r'\3'),
                        (r'(\d{2})(\d{4})(\d{4})', r'\1' + separator + r'\2' + separator + r'\3')]
        else:
            patterns = [(r'(\d{3})(\d{1,3})', r'\1' + separator + r'\2'),
                        (r'(\d{3})(\d{3})(\d{1,4})', r'\1' + separator + r'\2' + separator + r'\3'),
                        (r'(\d{3})(\d{4})(\d{4})', r'\1' + separator + r'\2' + separator + r'\3')]
        
        for pattern, replacement in patterns:
            phone_number = re.sub(pattern, replacement, phone_number)
        return phone_number