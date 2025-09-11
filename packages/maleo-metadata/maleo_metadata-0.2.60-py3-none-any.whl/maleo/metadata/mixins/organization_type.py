from pydantic import BaseModel, Field
from typing import Generic, TypeVar
from maleo.types.base.string import OptionalString
from ..enums.organization_type import Granularity as GranularityEnum


class Granularity(BaseModel):
    granularity: GranularityEnum = Field(
        GranularityEnum.BASIC, description="Granularity"
    )


class Key(BaseModel):
    key: str = Field(..., max_length=20, description="Organization type's key")


NameT = TypeVar("NameT", bound=OptionalString)


class Name(BaseModel, Generic[NameT]):
    name: NameT = Field(..., max_length=20, description="Organization type's name")
