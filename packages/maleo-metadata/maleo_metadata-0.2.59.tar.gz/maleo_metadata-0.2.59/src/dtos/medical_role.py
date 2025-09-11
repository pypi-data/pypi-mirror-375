from pydantic import BaseModel, Field
from uuid import UUID
from typing import Generic, List, Literal, Optional, TypeVar, overload
from maleo.constants.status import FULL_STATUSES
from maleo.dtos.data import (
    DataIdentifier,
    DataStatus,
    DataLifecycleTimestamp,
    DataTimestamp,
)
from maleo.dtos.parameter import (
    ReadSingleParameter as BaseReadSingleParameter,
    ReadPaginatedMultipleParameter,
    StatusUpdateParameter as BaseStatusUpdateParameter,
)
from maleo.mixins.general import Order, ParentId
from maleo.mixins.parameter import IdentifierTypeValue
from maleo.types.base.integer import OptionalInteger
from maleo.types.base.string import OptionalString
from maleo.types.enums.status import ListOfDataStatuses
from ..enums.medical_role import (
    Granularity as GranularityEnum,
    IdentifierType,
    Key as MedicalRoleKey,
)
from ..mixins.medical_role import Granularity, Code, Key, Name
from ..types.medical_role import IdentifierValueType


class CommonParameter(Granularity):
    pass


class CreateData(
    Name[str],
    Key,
    Code[str],
    Order[OptionalInteger],
    ParentId[OptionalInteger],
):
    pass


class CreateDataMixin(BaseModel):
    data: CreateData = Field(..., description="Create data")


class CreateParameter(
    CommonParameter,
    CreateDataMixin,
):
    pass


class ReadSingleParameter(
    CommonParameter, BaseReadSingleParameter[IdentifierType, IdentifierValueType]
):
    @overload
    @classmethod
    def new(
        cls,
        identifier: Literal[IdentifierType.ID],
        value: int,
        statuses: ListOfDataStatuses = list(FULL_STATUSES),
        use_cache: bool = True,
        granularity: GranularityEnum = GranularityEnum.BASIC,
    ) -> "ReadSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier: Literal[IdentifierType.UUID],
        value: UUID,
        statuses: ListOfDataStatuses = list(FULL_STATUSES),
        use_cache: bool = True,
        granularity: GranularityEnum = GranularityEnum.BASIC,
    ) -> "ReadSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier: Literal[IdentifierType.KEY, IdentifierType.NAME],
        value: str,
        statuses: ListOfDataStatuses = list(FULL_STATUSES),
        use_cache: bool = True,
        granularity: GranularityEnum = GranularityEnum.BASIC,
    ) -> "ReadSingleParameter": ...
    @classmethod
    def new(
        cls,
        identifier: IdentifierType,
        value: IdentifierValueType,
        statuses: ListOfDataStatuses = list(FULL_STATUSES),
        use_cache: bool = True,
        granularity: GranularityEnum = GranularityEnum.BASIC,
    ) -> "ReadSingleParameter":
        return cls(
            identifier=identifier,
            value=value,
            statuses=statuses,
            use_cache=use_cache,
            granularity=granularity,
        )


class ReadMultipleParameter(
    CommonParameter,
    ReadPaginatedMultipleParameter,
):
    pass


class FullUpdateData(
    Name[str],
    Code[str],
    Order[OptionalInteger],
    ParentId[OptionalInteger],
):
    pass


class PartialUpdateData(
    Name[OptionalString],
    Code[OptionalString],
    Order[OptionalInteger],
    ParentId[OptionalInteger],
):
    pass


UpdateDataT = TypeVar("UpdateDataT", FullUpdateData, PartialUpdateData)


class UpdateDataMixin(BaseModel, Generic[UpdateDataT]):
    data: UpdateDataT = Field(..., description="Update data")


class UpdateParameter(
    CommonParameter,
    UpdateDataMixin[UpdateDataT],
    IdentifierTypeValue[
        IdentifierType,
        IdentifierValueType,
    ],
    Generic[UpdateDataT],
):
    pass


class StatusUpdateParameter(
    CommonParameter,
    BaseStatusUpdateParameter,
):
    pass


class BaseMedicalRoleData(
    Name[str],
    Key,
    Code[str],
    Order[OptionalInteger],
    ParentId[OptionalInteger],
):
    pass


class BasicMedicalRoleData(
    BaseMedicalRoleData,
    DataStatus,
    DataIdentifier,
):
    pass


class StandardMedicalRoleData(
    BaseMedicalRoleData,
    DataStatus,
    DataLifecycleTimestamp,
    DataIdentifier,
):
    pass


class FullMedicalRoleData(
    BaseMedicalRoleData,
    DataStatus,
    DataTimestamp,
    DataIdentifier,
):
    pass


MedicalRoleDataT = TypeVar(
    "MedicalRoleDataT",
    BasicMedicalRoleData,
    StandardMedicalRoleData,
    FullMedicalRoleData,
)


MedicalRoleT = TypeVar(
    "MedicalRoleT",
    MedicalRoleKey,
    BasicMedicalRoleData,
    StandardMedicalRoleData,
    FullMedicalRoleData,
)


class MedicalRoleMixin(BaseModel, Generic[MedicalRoleT]):
    medical_role: MedicalRoleT = Field(..., description="Medical role")


class OptionalMedicalRoleMixin(BaseModel, Generic[MedicalRoleT]):
    medical_role: Optional[MedicalRoleT] = Field(..., description="Medical role")


class MedicalRolesMixin(BaseModel, Generic[MedicalRoleT]):
    medical_roles: List[MedicalRoleT] = Field(..., description="Medical roles")


class OptionalMedicalRolesMixin(BaseModel, Generic[MedicalRoleT]):
    medical_roles: Optional[List[MedicalRoleT]] = Field(
        ..., description="Medical roles"
    )
