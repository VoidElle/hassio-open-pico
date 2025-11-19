from dataclasses import dataclass


@dataclass
class SystemInfoModel:
    """System information and diagnostics"""
    counter: int  # cntr
    memory_free: int  # memfree
    uptime: int  # up_time (in seconds presumably)
    date: str
    time: str
    week: int

    @property
    def has_rtc(self) -> bool:
        """Check if RTC (Real-Time Clock) is available"""
        return self.date != "NO RTC"

    @property
    def uptime_hours(self) -> float:
        """Uptime in hours"""
        return self.uptime / 3600 if self.uptime > 0 else 0

    @property
    def uptime_days(self) -> float:
        """Uptime in days"""
        return self.uptime / 86400 if self.uptime > 0 else 0

    @property
    def memory_free_kb(self) -> float:
        """Free memory in KB"""
        return self.memory_free / 1024