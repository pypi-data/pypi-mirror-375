import secrets
import string
from typing import Dict, Any
from passlib.context import CryptContext
import re


class PasswordHashingStrategy:
    """패스워드 해싱 전략 인터페이스"""
    
    def hash_password(self, password: str) -> str:
        raise NotImplementedError
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        raise NotImplementedError


class BcryptStrategy(PasswordHashingStrategy):
    """Bcrypt 해싱 전략"""
    
    def __init__(self, rounds: int = 12):
        self.context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=rounds)
    
    def hash_password(self, password: str) -> str:
        return self.context.hash(password)
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        return self.context.verify(password, hashed_password)


class Argon2Strategy(PasswordHashingStrategy):
    """Argon2 해싱 전략"""
    
    def __init__(self):
        self.context = CryptContext(schemes=["argon2"], deprecated="auto")
    
    def hash_password(self, password: str) -> str:
        return self.context.hash(password)
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        return self.context.verify(password, hashed_password)


class PBKDF2Strategy(PasswordHashingStrategy):
    """PBKDF2 해싱 전략"""
    
    def __init__(self, rounds: int = 100000):
        self.context = CryptContext(
            schemes=["pbkdf2_sha256"], 
            deprecated="auto",
            pbkdf2_sha256__rounds=rounds
        )
    
    def hash_password(self, password: str) -> str:
        return self.context.hash(password)
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        return self.context.verify(password, hashed_password)


class PasswordValidator:
    """패스워드 유효성 검증 클래스"""
    
    @staticmethod
    def validate_strength(password: str, min_length: int = 8) -> Dict[str, Any]:
        """패스워드 강도 검증"""
        result = {
            "is_valid": True,
            "errors": [],
            "strength_score": 0
        }
        
        # 길이 검증
        if len(password) < min_length:
            result["is_valid"] = False
            result["errors"].append(f"패스워드는 최소 {min_length}자 이상이어야 합니다.")
        else:
            result["strength_score"] += 1
        
        # 대문자 포함 검증
        if not re.search(r'[A-Z]', password):
            result["errors"].append("대문자를 포함해야 합니다.")
        else:
            result["strength_score"] += 1
        
        # 소문자 포함 검증
        if not re.search(r'[a-z]', password):
            result["errors"].append("소문자를 포함해야 합니다.")
        else:
            result["strength_score"] += 1
        
        # 숫자 포함 검증
        if not re.search(r'\d', password):
            result["errors"].append("숫자를 포함해야 합니다.")
        else:
            result["strength_score"] += 1
        
        # 특수문자 포함 검증
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            result["errors"].append("특수문자를 포함해야 합니다.")
        else:
            result["strength_score"] += 1
        
        # 전체 유효성 판단
        if result["errors"]:
            result["is_valid"] = False
        
        return result
    
    @staticmethod
    def check_common_passwords(password: str) -> bool:
        """일반적인 패스워드 체크"""
        common_passwords = [
            "password", "123456", "password123", "admin", "qwerty",
            "letmein", "welcome", "monkey", "1234567890", "abc123"
        ]
        return password.lower() not in common_passwords


class PasswordGenerator:
    """패스워드 생성 클래스"""
    
    @staticmethod
    def generate_random_password(
        length: int = 12,
        include_uppercase: bool = True,
        include_lowercase: bool = True,
        include_digits: bool = True,
        include_symbols: bool = True,
        exclude_ambiguous: bool = True
    ) -> str:
        """랜덤 패스워드 생성"""
        
        characters = ""
        
        if include_lowercase:
            chars = string.ascii_lowercase
            if exclude_ambiguous:
                chars = chars.replace('l', '').replace('o', '')
            characters += chars
        
        if include_uppercase:
            chars = string.ascii_uppercase
            if exclude_ambiguous:
                chars = chars.replace('I', '').replace('O', '')
            characters += chars
        
        if include_digits:
            chars = string.digits
            if exclude_ambiguous:
                chars = chars.replace('0', '').replace('1', '')
            characters += chars
        
        if include_symbols:
            chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            characters += chars
        
        if not characters:
            raise ValueError("최소 하나의 문자 타입은 포함되어야 합니다.")
        
        password = ''.join(secrets.choice(characters) for _ in range(length))
        return password
    
    @staticmethod
    def generate_memorable_password(word_count: int = 4, separator: str = "-") -> str:
        """기억하기 쉬운 패스워드 생성"""
        words = [
            "apple", "banana", "cherry", "dragon", "eagle", "forest",
            "guitar", "happy", "island", "jungle", "kitten", "lemon",
            "mountain", "ocean", "piano", "quiet", "river", "sunset",
            "tiger", "umbrella", "violet", "winter", "yellow", "zebra"
        ]
        
        selected_words = [secrets.choice(words) for _ in range(word_count)]
        password = separator.join(selected_words)
        
        # 랜덤 숫자 추가
        password += str(secrets.randbelow(100))
        
        return password


class PasswordFactory:
    """패스워드 관련 기능을 제공하는 팩토리 클래스"""
    
    def __init__(self, strategy: str = "bcrypt"):
        """
        패스워드 팩토리 초기화
        
        Args:
            strategy: 해싱 전략 ("bcrypt", "argon2", "pbkdf2")
        """
        self.strategies = {
            "bcrypt": BcryptStrategy(),
            "argon2": Argon2Strategy(),
            "pbkdf2": PBKDF2Strategy()
        }
        
        if strategy not in self.strategies:
            raise ValueError(f"지원하지 않는 해싱 전략: {strategy}")
        
        self.current_strategy = self.strategies[strategy]
        self.validator = PasswordValidator()
        self.generator = PasswordGenerator()
    
    def hash_password(self, password: str) -> str:
        """패스워드 해싱"""
        return self.current_strategy.hash_password(password)
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """패스워드 검증"""
        return self.current_strategy.verify_password(password, hashed_password)
    
    def validate_password(self, password: str, min_length: int = 8) -> Dict[str, Any]:
        """패스워드 유효성 검증"""
        return self.validator.validate_strength(password, min_length)
    
    def generate_password(self, length: int = 12, **kwargs) -> str:
        """랜덤 패스워드 생성"""
        return self.generator.generate_random_password(length, **kwargs)
    
    def generate_memorable_password(self, word_count: int = 4) -> str:
        """기억하기 쉬운 패스워드 생성"""
        return self.generator.generate_memorable_password(word_count)
    
    def change_strategy(self, strategy: str):
        """해싱 전략 변경"""
        if strategy not in self.strategies:
            raise ValueError(f"지원하지 않는 해싱 전략: {strategy}")
        self.current_strategy = self.strategies[strategy]
    
    def is_password_compromised(self, password: str) -> bool:
        """일반적인 패스워드인지 확인"""
        return not self.validator.check_common_passwords(password)


# 사용 예시
if __name__ == "__main__":
    # 팩토리 생성
    password_factory = PasswordFactory("bcrypt")
    
    # 패스워드 생성
    new_password = password_factory.generate_password(12)
    print(f"생성된 패스워드: {new_password}")
    
    # 패스워드 해싱
    hashed = password_factory.hash_password(new_password)
    print(f"해싱된 패스워드: {hashed}")
    
    # 패스워드 검증
    is_valid = password_factory.verify_password(new_password, hashed)
    print(f"패스워드 검증 결과: {is_valid}")
    
    # 패스워드 강도 검증
    validation_result = password_factory.validate_password(new_password)
    print(f"패스워드 강도: {validation_result}")
