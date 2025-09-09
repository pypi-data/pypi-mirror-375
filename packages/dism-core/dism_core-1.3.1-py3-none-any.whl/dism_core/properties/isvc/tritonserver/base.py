from pathlib import Path
from typing import Optional

from ..base import InferenceServiceProperties
from .types import PlatformType


class TritonserverProperties(InferenceServiceProperties):
    MaxBatchSize: int
    ModelRepositoryUri: Optional[Path] = None
    Platform: PlatformType

    def __setattr__(self, name, value):
        if name == "Platform":
            raise AttributeError("Platform is a constant and cannot be changed.")
        super().__setattr__(name, value)
