from enum import Enum


class ByteSize(Enum):
    B = 1
    KB = 1_024 * B  # type: ignore
    MB = 1024 * KB  # type: ignore
    GB = 1024 * MB  # type: ignore
