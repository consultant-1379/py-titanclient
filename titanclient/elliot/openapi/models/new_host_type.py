from enum import Enum


class NewHostType(str, Enum):
    SIMULATOR = "simulator"
    TRAFFIC = "traffic"

    def __str__(self) -> str:
        return str(self.value)
