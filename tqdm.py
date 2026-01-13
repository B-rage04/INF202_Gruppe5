from typing import Any, Iterable, Optional


class _Tqdm:
    def __init__(self, total: Optional[int] = None, **_: Any):
        self.total = total

    def update(self, n: int = 1) -> None:
        return None

    def __enter__(self) -> "_Tqdm":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


def tqdm(iterable: Optional[Iterable] = None, **kwargs) -> Any:
    if iterable is None:
        return _Tqdm(**kwargs)
    return iterable
