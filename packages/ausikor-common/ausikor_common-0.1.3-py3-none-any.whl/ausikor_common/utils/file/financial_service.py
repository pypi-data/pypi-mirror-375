from abc import ABC, abstractmethod
from decimal import Decimal
import math
from typing import Any, Union


class NumberFormatter:
    """숫자 포맷팅을 담당하는 유틸리티 클래스"""
    
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


class TaxCalculationStrategy(ABC):
    """세금 계산 전략 인터페이스"""
    
    @abstractmethod
    def calculate_supply_amount(self, total_amount: str) -> str:
        """공급가액 계산"""
        pass
    
    @abstractmethod
    def calculate_tax_amount(self, total_amount: str) -> str:
        """세액 계산"""
        pass


class KoreanVATStrategy(TaxCalculationStrategy):
    """한국 부가가치세 계산 전략 (10%)"""
    
    VAT_RATE = Decimal("0.1")
    SUPPLY_RATE = Decimal("0.909")  # 1 / 1.1
    TAX_RATE = Decimal("0.091")     # 0.1 / 1.1
    
    def calculate_supply_amount(self, total_amount: str) -> str:
        """공급가액 = 총액 / 1.1"""
        return str(math.floor(Decimal(total_amount) * self.SUPPLY_RATE))
    
    def calculate_tax_amount(self, total_amount: str) -> str:
        """부가세 = 총액 * 0.1 / 1.1"""
        return str(math.ceil(Decimal(total_amount) * self.TAX_RATE))


class USATaxStrategy(TaxCalculationStrategy):
    """미국 세금 계산 전략 (예시)"""
    
    def __init__(self, tax_rate: float = 0.08):
        self.tax_rate = Decimal(str(tax_rate))
        self.supply_rate = Decimal("1") / (Decimal("1") + self.tax_rate)
        self.tax_calculation_rate = self.tax_rate / (Decimal("1") + self.tax_rate)
    
    def calculate_supply_amount(self, total_amount: str) -> str:
        return str(math.floor(Decimal(total_amount) * self.supply_rate))
    
    def calculate_tax_amount(self, total_amount: str) -> str:
        return str(math.ceil(Decimal(total_amount) * self.tax_calculation_rate))


class TaxCalculator:
    """Context 클래스 - 세금 계산 전략을 사용"""
    
    def __init__(self, strategy: TaxCalculationStrategy = None):
        self._strategy = strategy or KoreanVATStrategy()
    
    def set_strategy(self, strategy: TaxCalculationStrategy):
        """계산 전략 변경"""
        self._strategy = strategy
    
    def get_supply_cost(self, total_amount: str) -> str:
        """공급가액 계산"""
        return self._strategy.calculate_supply_amount(total_amount)
    
    def get_tax(self, total_amount: str) -> str:
        """세액 계산"""
        return self._strategy.calculate_tax_amount(total_amount)
    
    def get_breakdown(self, total_amount: str) -> dict:
        """총액 분해 (공급가액 + 세액)"""
        supply_amount = self.get_supply_cost(total_amount)
        tax_amount = self.get_tax(total_amount)
        return {
            "total_amount": total_amount,
            "supply_amount": supply_amount,
            "tax_amount": tax_amount
        }


class FinancialCalculatorFactory:
    """Factory Pattern - 지역별 세금 계산기 생성"""
    
    @staticmethod
    def create_korean_calculator() -> TaxCalculator:
        """한국 부가세 계산기 생성"""
        return TaxCalculator(KoreanVATStrategy())
    
    @staticmethod
    def create_usa_calculator(tax_rate: float = 0.08) -> TaxCalculator:
        """미국 세금 계산기 생성"""
        return TaxCalculator(USATaxStrategy(tax_rate))
    
    @staticmethod
    def create_custom_calculator(strategy: TaxCalculationStrategy) -> TaxCalculator:
        """커스텀 전략 계산기 생성"""
        return TaxCalculator(strategy)
    



# 하위 호환성을 위한 기존 인터페이스 유지
class Number:
    """기존 코드와의 호환성을 위한 래퍼 클래스"""
    
    _calculator = TaxCalculator()
    
    @staticmethod
    def format_number(value: Any) -> str:
        return NumberFormatter.format_number(value)
    
    @staticmethod
    def remove_point_zero(value: Any) -> Union[str, None]:
        return NumberFormatter.remove_trailing_zero(value)

    @staticmethod
    def get_supply_cost(total_amount: str) -> str:
        return Number._calculator.get_supply_cost(total_amount)

    @staticmethod
    def get_tax(total_amount: str) -> str:
        return Number._calculator.get_tax(total_amount) 