from datetime import datetime
from typing import Any


class Printer:
    @staticmethod
    def print_sql(memo: str, messages: Any) -> None:
        print(messages)
        print("." * 70)
    
    @staticmethod
    def console(*messages: Any) -> None:
        print(*messages)
        print("." * 100)
    
    @staticmethod
    def measure_duration(start_time: datetime, end_time: datetime) -> None:
        duration = (end_time - start_time).total_seconds()
        Printer.console(f"요청 처리시간", f"{duration}초")