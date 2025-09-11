from abc import ABC, abstractmethod
from datetime import datetime, timezone
from threading import Lock
from typing import Dict, Optional, List
import pytz


from app.common.config.base_config import BaseConfig





class TimezoneObserver(ABC):
    """타임존 변경 관찰자 인터페이스"""
    
    @abstractmethod
    def on_timezone_changed(self, old_timezone: str, new_timezone: str, user_id: Optional[str] = None):
        """타임존 변경 시 호출되는 메서드"""
        pass


class TimezoneLogger(TimezoneObserver):
    """타임존 변경 로깅 관찰자"""
    
    def on_timezone_changed(self, old_timezone: str, new_timezone: str, user_id: Optional[str] = None):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user_info = f"User: {user_id}" if user_id else "Global"
        print(f"[{timestamp}] Timezone changed - {user_info} | {old_timezone} → {new_timezone}")


class TimezoneNotifier(TimezoneObserver):
    """타임존 변경 알림 관찰자"""
    
    def on_timezone_changed(self, old_timezone: str, new_timezone: str, user_id: Optional[str] = None):
        # 실제 구현에서는 웹소켓이나 이벤트 시스템을 통해 클라이언트에 알림
        print(f"Notifying clients about timezone change: {old_timezone} → {new_timezone}")


class TimezoneStrategy(ABC):
    """타임존 결정 전략 인터페이스"""
    
    @abstractmethod
    def determine_timezone(self, user_context: Dict) -> str:
        """사용자 컨텍스트를 기반으로 타임존 결정"""
        pass


class UserPreferenceTimezoneStrategy(TimezoneStrategy):
    """사용자 설정 기반 타임존 전략"""
    
    def determine_timezone(self, user_context: Dict) -> str:
        return user_context.get('user_timezone', TimezoneRegion.ASIA_SEOUL.value)


class GeoLocationTimezoneStrategy(TimezoneStrategy):
    """지리적 위치 기반 타임존 전략"""
    
    def determine_timezone(self, user_context: Dict) -> str:
        country = user_context.get('country', 'KR')
        timezone_mapping = {
            'KR': TimezoneRegion.ASIA_SEOUL.value,
            'US': TimezoneRegion.AMERICA_NEW_YORK.value,
            'GB': TimezoneRegion.EUROPE_LONDON.value,
            'JP': TimezoneRegion.ASIA_TOKYO.value,
            'CN': TimezoneRegion.ASIA_SHANGHAI.value,
            'FR': TimezoneRegion.EUROPE_PARIS.value,
            'AU': TimezoneRegion.AUSTRALIA_SYDNEY.value,
        }
        return timezone_mapping.get(country, TimezoneRegion.ASIA_SEOUL.value)


class BrowserTimezoneStrategy(TimezoneStrategy):
    """브라우저 설정 기반 타임존 전략"""
    
    def determine_timezone(self, user_context: Dict) -> str:
        browser_timezone = user_context.get('browser_timezone')
        if browser_timezone and self._is_valid_timezone(browser_timezone):
            return browser_timezone
        return TimezoneRegion.ASIA_SEOUL.value
    
    def _is_valid_timezone(self, timezone_str: str) -> bool:
        try:
            pytz.timezone(timezone_str)
            return True
        except pytz.exceptions.UnknownTimeZoneError:
            return False


class GlobalTimezoneManager(BaseConfig):
    """글로벌 타임존 관리자 (싱글톤 + 옵저버 + 전략 패턴)"""

    _instance = None
    _lock = Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """초기화"""
        self._global_timezone = TimezoneRegion.ASIA_SEOUL.value
        self._user_timezones: Dict[str, str] = {}
        self._observers: List[TimezoneObserver] = []
        self._strategy: TimezoneStrategy = UserPreferenceTimezoneStrategy()
        
        # 기본 관찰자 등록
        self.add_observer(TimezoneLogger())
        self.add_observer(TimezoneNotifier())

    def add_observer(self, observer: TimezoneObserver):
        """관찰자 추가"""
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: TimezoneObserver):
        """관찰자 제거"""
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify_observers(self, old_timezone: str, new_timezone: str, user_id: Optional[str] = None):
        """모든 관찰자에게 타임존 변경 알림"""
        for observer in self._observers:
            observer.on_timezone_changed(old_timezone, new_timezone, user_id)

    def set_strategy(self, strategy: TimezoneStrategy):
        """타임존 결정 전략 변경"""
        self._strategy = strategy

    def set_global_timezone(self, timezone_str: str):
        """글로벌 타임존 설정"""
        if self._is_valid_timezone(timezone_str):
            old_timezone = self._global_timezone
            self._global_timezone = timezone_str
            self._notify_observers(old_timezone, timezone_str)
        else:
            raise ValueError(f"Invalid timezone: {timezone_str}")

    def set_user_timezone(self, user_id: str, timezone_str: str):
        """특정 사용자의 타임존 설정"""
        if self._is_valid_timezone(timezone_str):
            old_timezone = self._user_timezones.get(user_id, self._global_timezone)
            self._user_timezones[user_id] = timezone_str
            self._notify_observers(old_timezone, timezone_str, user_id)
        else:
            raise ValueError(f"Invalid timezone: {timezone_str}")

    def get_user_timezone(self, user_id: str) -> str:
        """사용자별 타임존 조회"""
        return self._user_timezones.get(user_id, self._global_timezone)

    def get_global_timezone(self) -> str:
        """글로벌 타임존 조회"""
        return self._global_timezone

    def auto_detect_timezone(self, user_id: str, user_context: Dict):
        """사용자 컨텍스트를 기반으로 타임존 자동 감지"""
        detected_timezone = self._strategy.determine_timezone(user_context)
        self.set_user_timezone(user_id, detected_timezone)

    def get_current_time(self, user_id: Optional[str] = None) -> datetime:
        """사용자별 현재 시간 조회"""
        timezone_str = self.get_user_timezone(user_id) if user_id else self._global_timezone
        tz = pytz.timezone(timezone_str)
        return datetime.now(tz)

    def convert_time(self, dt: datetime, target_user_id: Optional[str] = None) -> datetime:
        """시간을 특정 사용자의 타임존으로 변환"""
        target_timezone_str = self.get_user_timezone(target_user_id) if target_user_id else self._global_timezone
        target_tz = pytz.timezone(target_timezone_str)
        
        if dt.tzinfo is None:
            # naive datetime인 경우 UTC로 가정
            dt = pytz.UTC.localize(dt)
        
        return dt.astimezone(target_tz)

    def remove_user_timezone(self, user_id: str):
        """사용자별 타임존 설정 제거 (글로벌 타임존 사용)"""
        if user_id in self._user_timezones:
            old_timezone = self._user_timezones[user_id]
            del self._user_timezones[user_id]
            self._notify_observers(old_timezone, self._global_timezone, user_id)

    def get_supported_timezones(self) -> List[str]:
        """지원하는 타임존 목록 반환"""
        return [region.value for region in TimezoneRegion]

    def _is_valid_timezone(self, timezone_str: str) -> bool:
        """타임존 유효성 검사"""
        try:
            pytz.timezone(timezone_str)
            return True
        except pytz.exceptions.UnknownTimeZoneError:
            return False

    @property
    def scheduler_timezone(self) -> str:
        """스케줄러용 타임존 (하위 호환성)"""
        return self._global_timezone


class TimezoneFactory:
    """타임존 전략 팩토리"""
    
    @staticmethod
    def create_user_preference_strategy() -> TimezoneStrategy:
        """사용자 설정 기반 전략 생성"""
        return UserPreferenceTimezoneStrategy()
    
    @staticmethod
    def create_geolocation_strategy() -> TimezoneStrategy:
        """지리적 위치 기반 전략 생성"""
        return GeoLocationTimezoneStrategy()
    
    @staticmethod
    def create_browser_strategy() -> TimezoneStrategy:
        """브라우저 설정 기반 전략 생성"""
        return BrowserTimezoneStrategy()


# 싱글톤 인스턴스 생성
timezone_manager = GlobalTimezoneManager()

# 하위 호환성을 위한 기존 인터페이스
class TimeZone(BaseConfig):
    """기존 코드와의 호환성을 위한 래퍼 클래스"""
    
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def scheduler_timezone(self) -> str:
        return timezone_manager.get_global_timezone()


# 기존 코드 호환성
time_zone = TimeZone()