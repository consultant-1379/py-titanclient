from enum import Enum


class GetProjectPidValueNameName(str, Enum):
    ALL = "all"
    CONFIG = "config"
    GPL = "gpl"
    LATENCY = "latency"
    STATUS_CODES = "status_codes"
    TRAFFIC = "traffic"

    def __str__(self) -> str:
        return str(self.value)
