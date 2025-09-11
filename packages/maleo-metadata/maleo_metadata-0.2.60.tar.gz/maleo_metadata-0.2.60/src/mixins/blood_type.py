from pydantic import BaseModel, Field
from typing import Generic, TypeVar
from maleo.types.base.string import OptionalString
from ..enums.blood_type import Granularity as GranularityEnum


class Granularity(BaseModel):
    granularity: GranularityEnum = Field(
        GranularityEnum.BASIC, description="Granularity"
    )


class Key(BaseModel):
    key: str = Field(..., max_length=2, description="Blood type's key")


NameT = TypeVar("NameT", bound=OptionalString)


class Name(BaseModel, Generic[NameT]):
    name: NameT = Field(..., max_length=2, description="Blood type's name")
