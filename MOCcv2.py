import numpy as np
from pathlib import Path
from typing import Any


def imread(path: str) -> Any:
    # Return a tiny dummy image array if the file exists, otherwise None
    p = Path(path)
    if not p.exists():
        return None
    # return a small 3-channel image
    return np.zeros((2, 2, 3), dtype=np.uint8)


def VideoWriter_fourcc(*_args: str) -> int:
    return 0


class VideoWriter:
    def __init__(self, filename: str, fourcc: int, fps: float, size: Any):
        self.filename = filename
        self.fourcc = fourcc
        self.fps = fps
        self.size = size

    def write(self, frame: Any) -> None:
        # no-op for tests
        return None

    def release(self) -> None:
        return None
