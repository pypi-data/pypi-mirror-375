import numpy as np
from numpy.typing import NDArray

from typing import Any
from typing import Iterator

from . import base
from .base import Empty

class AttributeManager(
    base.MutableMappingHDF5[str, Empty | NDArray[np.generic] | np.generic],
    base.CommonStateObject,
):
    def __delitem__(self, name: str) -> None: ...
    def __getitem__(self, name: str) -> Empty | NDArray[np.generic] | np.generic: ...
    def __setitem__(self, name: str, value: Any) -> None: ...
    def __iter__(self) -> Iterator[str]: ...
    def __len__(self) -> int: ...
