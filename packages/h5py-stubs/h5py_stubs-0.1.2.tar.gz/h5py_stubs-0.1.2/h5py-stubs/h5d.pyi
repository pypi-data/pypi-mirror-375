import numpy as np

from . import _objects as __h5py__objects

class DatasetID(__h5py__objects.ObjectID):
    @property
    def dtype(self) -> np.generic: ...
