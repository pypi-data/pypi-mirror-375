from pydantic import BaseModel, Field
from typing import Generic, Optional, TypeVar
from uuid import UUID
from maleo.enums.service import (
    ServiceType as ServiceTypeEnum,
    Category as CategoryEnum,
)
from maleo.types.base.string import OptionalString
from ..enums.service import Granularity as GranularityEnum


class Granularity(BaseModel):
    granularity: GranularityEnum = Field(
        GranularityEnum.BASIC, description="Granularity"
    )


ServiceTypeT = TypeVar("ServiceTypeT", bound=Optional[ServiceTypeEnum])


class ServiceType(BaseModel, Generic[ServiceTypeT]):
    type: ServiceTypeT = Field(..., description="Service's type")


CategoryT = TypeVar("CategoryT", bound=Optional[CategoryEnum])


class Category(BaseModel, Generic[CategoryT]):
    category: CategoryT = Field(..., description="Service's category")


class OptionalCategory(BaseModel):
    category: Optional[CategoryEnum] = Field(
        None, description="Service's category. (Optional)"
    )


class Key(BaseModel):
    key: str = Field(..., max_length=20, description="Service's key")


NameT = TypeVar("NameT", bound=OptionalString)


class Name(BaseModel, Generic[NameT]):
    name: NameT = Field(..., max_length=20, description="Service's name")


class Secret(BaseModel):
    secret: UUID = Field(..., description="Service's secret")
