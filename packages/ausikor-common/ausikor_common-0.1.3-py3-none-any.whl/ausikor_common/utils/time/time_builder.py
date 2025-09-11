from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone


# ✅ 1. TimeBuilder: 특정 시간 조작을 위한 빌더 패턴 적용
class TimeBuilder:
    def __init__(self):
        self._time = datetime.now(timezone("Asia/Seoul"))

    def now(self):
        """현재 시간을 설정"""
        self._time = datetime.now(timezone("Asia/Seoul"))
        return self

    def days(self, days: int):
        """일 수 추가"""
        self._time += timedelta(days=days)
        return self

    def years(self, years: int):
        """연도 추가"""
        self._time += relativedelta(years=years)
        return self

    def to_string(self, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        """문자열로 변환"""
        return self._time.strftime(fmt)

    def build(self) -> datetime:
        """최종 시간 객체 반환"""
        return self._time