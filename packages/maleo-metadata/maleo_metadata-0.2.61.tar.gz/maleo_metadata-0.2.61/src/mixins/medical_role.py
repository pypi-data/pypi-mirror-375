from pydantic import BaseModel, Field
from typing import Generic, TypeVar
from maleo.types.base.string import OptionalString
from ..enums.medical_role import Granularity as GranularityEnum


class Granularity(BaseModel):
    granularity: GranularityEnum = Field(
        GranularityEnum.BASIC, description="Granularity"
    )


CodeT = TypeVar("CodeT", bound=OptionalString)


class Code(BaseModel, Generic[CodeT]):
    code: CodeT = Field(..., max_length=20, description="Medical role's code")


class Key(BaseModel):
    key: str = Field(..., max_length=255, description="Medical role's key")


NameT = TypeVar("NameT", bound=OptionalString)


class Name(BaseModel, Generic[NameT]):
    name: NameT = Field(..., max_length=255, description="Medical role's name")


class MedicalRoleId(BaseModel):
    medical_role_id: int = Field(..., ge=1, description="Medical role's id")
