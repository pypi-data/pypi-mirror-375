from typing import Optional

from pydantic import BaseModel, model_validator


class InferenceOnConditions(BaseModel):
    MinRunNumber: Optional[int]
    MaxRunNumber: Optional[int]
    StableBeams: Optional[bool]
    FillType: Optional[str]
    MinNumberOfLumisection: Optional[int]
    MinDeliveredLuminosity: Optional[float]
    MinRecordedLuminosity: Optional[float]
    MinBField: Optional[float]
    MinEnergy: Optional[float]
    Clock: Optional[str]
    Sequence: Optional[str]
    L1KeyMatch: Optional[str]
    L1MenuMatch: Optional[str]
    HLTConfigMatch: Optional[str]
    NoComponentOut: Optional[bool]
    AllowedComponentsOut: Optional[list[str]]
    AllowedPrimaryDatasets: Optional[list[str]]

    @model_validator(mode="after")
    def check_components_props(self) -> "InferenceOnConditions":
        if self.NoComponentOut is not None and self.AllowedComponentsOut is not None:
            raise ValueError("The `NoComponentOut` field cannot be declared if `AllowedComponentsOut` is provided.")
        return self
