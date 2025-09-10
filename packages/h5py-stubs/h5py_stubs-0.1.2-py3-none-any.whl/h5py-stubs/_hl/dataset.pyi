from numbers import Number
from types import EllipsisType
from typing import Any, Collection, Iterable, Literal, SupportsIndex, Union, overload

import numpy as np
import numpy.typing as npt
from numpy._typing import _ArrayLikeInt_co

from ..h5d import DatasetID
from .base import HLObject

SELECTOR = Union[
    None,
    EllipsisType,
    tuple[()],
    int,
    bool,
    SupportsIndex,
    slice,
    range,
    Iterable[int],
    Iterable[bool],
    _ArrayLikeInt_co,
]

class AstypeWrapper:
    """Wrapper to convert data on reading from a dataset."""

    def __init__(self, dset: Dataset, dtype: np.generic): ...
    def __getitem__(self, args: tuple[int, ...]) -> npt.NDArray[Any] | np.generic: ...
    def __enter__(self) -> AstypeWrapper: ...
    def __exit__(self, *args: None) -> None: ...
    def __len__(self) -> int: ...

class AsStrWrapper:
    """Wrapper to decode strings on reading the dataset"""

    def __init__(
        self,
        dset: Dataset,
        encoding: Literal["ascii", "utf-8"],
        errors: Literal["strict"] = "strict",
    ): ...
    def __getitem__(self, args: tuple[int, ...]) -> npt.NDArray[np.object_]: ...
    def __len__(self) -> int: ...

class ChunkIterator:
    def __iter__(self) -> ChunkIterator: ...
    def __next__(self) -> tuple[slice, ...]: ...

class Dataset(HLObject):
    def __init__(self, bind: DatasetID, *, readonly: bool = False): ...
    @overload
    def resize(self, size: int, axis: int) -> None: ...
    @overload
    def resize(self, size: Collection[int], axis: None = None) -> None: ...
    def __getitem__(
        self,
        args: SELECTOR | tuple[SELECTOR, ...],
        new_dtype: npt.DTypeLike | None = None,
    ) -> Any: ...
    def __setitem__(
        self,
        args: SELECTOR | tuple[SELECTOR, ...],
        val: npt.NDArray[Any] | Number | str,
    ) -> None: ...
    @property
    def ndim(self) -> int: ...
    @property
    def id(self) -> DatasetID: ...
    @property
    def dtype(self) -> np.dtype[np.generic]: ...
    @property
    def chunks(self) -> tuple[int, ...] | None: ...
    @property
    def shape(self) -> tuple[int, ...]: ...
    @property
    def size(self) -> int: ...
    def astype(self, dtype: npt.DTypeLike) -> AstypeWrapper: ...
    def asstr(
        self,
        encoding: Literal["ascii", "utf-8"] | None = None,
        errors: Literal["strict"] = "strict",
    ) -> AsStrWrapper: ...
    def __len__(self) -> int: ...
    def iter_chunks(
        self, sel: slice | tuple[slice, ...] | None = None
    ) -> ChunkIterator: ...
    def read_direct(
        self,
        dest: npt.NDArray[Any],
        source_sel: tuple[int | slice | Collection[int], ...] | None = None,
        dest_sel: tuple[int | slice | Collection[int], ...] | None = None,
    ) -> None: ...
    def write_direct(
        self,
        source: npt.NDArray[Any],
        source_sel: tuple[int | slice | Collection[int] | None, ...] | None = None,
        dest_sel: tuple[int | slice | Collection[int] | None, ...] | None = None,
    ) -> None: ...
