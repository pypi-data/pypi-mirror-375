from enum import Enum
from typing import Optional

from pydantic import BaseModel, model_validator


class SourceEnum(str, Enum):
    OMS = "OMS"


class EndpointEnum(str, Enum):
    lumisections = "lumisections"
    hltpathrates = "hltpathrates"
    datasetrates = "datasetrates"


class FilterOperationEnum(str, Enum):
    EQ = "EQ"
    LIST_AND_MATCH = "LIST_AND_MATCH"


class EndpointFilter(BaseModel):
    Name: str
    Value: str
    Operation: FilterOperationEnum = FilterOperationEnum.EQ


class InputMetadata(BaseModel):
    Name: str
    Source: SourceEnum
    Endpoint: EndpointEnum
    Attributes: list[str]
    Filter: Optional[list[EndpointFilter]] = None

    @model_validator(mode="after")
    def check_list_and_match_only_for_hltpathrates(self) -> "InputMetadata":
        if self.Filter:
            for f in self.Filter:
                if f.Operation == FilterOperationEnum.LIST_AND_MATCH and (
                    self.Endpoint != EndpointEnum.hltpathrates or f.Name != "path_name"
                ):
                    raise ValueError(
                        f"LIST_AND_MATCH operation can only be used with Endpoint '{EndpointEnum.hltpathrates}'. "
                        f"Got '{self.Endpoint}' instead."
                    )
        return self
