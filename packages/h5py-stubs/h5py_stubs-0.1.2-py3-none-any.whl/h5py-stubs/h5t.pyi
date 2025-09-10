import numpy as np

from typing import Any
from typing import Literal

class string_info(tuple[str, int]): ...

def string_dtype(
    encoding: Literal["utf-8", "ascii"] = "utf-8", length: int | None = None
) -> np.dtype[np.bytes_] | np.dtype[np.object_]: ...
def check_string_dtype(*args: Any, **kwargs: Any) -> string_info | None: ...
