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
from maleo.mixins.general import Order
from maleo.mixins.parameter import IdentifierTypeValue
from maleo.types.base.integer import OptionalInteger
from maleo.types.base.string import OptionalString
from maleo.types.enums.status import ListOfDataStatuses
from ..enums.system_role import (
    Granularity as GranularityEnum,
    IdentifierType,
    Key as SystemRoleKey,
)
from ..mixins.system_role import Granularity, Key, Name
from ..types.system_role import IdentifierValueType


class CommonParameter(Granularity):
    pass


class CreateData(Name[str], Key, Order[OptionalInteger]):
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


class FullUpdateData(Name[str], Order[OptionalInteger]):
    pass


class PartialUpdateData(Name[OptionalString], Order[OptionalInteger]):
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


class BaseSystemRoleData(
    Name[str],
    Key,
    Order[OptionalInteger],
):
    pass


class BasicSystemRoleData(
    BaseSystemRoleData,
    DataStatus,
    DataIdentifier,
):
    pass


class StandardSystemRoleData(
    BaseSystemRoleData,
    DataStatus,
    DataLifecycleTimestamp,
    DataIdentifier,
):
    pass


class FullSystemRoleData(
    BaseSystemRoleData,
    DataStatus,
    DataTimestamp,
    DataIdentifier,
):
    pass


SystemRoleDataT = TypeVar(
    "SystemRoleDataT",
    BasicSystemRoleData,
    StandardSystemRoleData,
    FullSystemRoleData,
)


SystemRoleT = TypeVar(
    "SystemRoleT",
    SystemRoleKey,
    BasicSystemRoleData,
    StandardSystemRoleData,
    FullSystemRoleData,
)


class SystemRoleMixin(BaseModel, Generic[SystemRoleT]):
    system_role: SystemRoleT = Field(..., description="System role")


class OptionalSystemRoleMixin(BaseModel, Generic[SystemRoleT]):
    system_role: Optional[SystemRoleT] = Field(..., description="System role")


class SystemRolesMixin(BaseModel, Generic[SystemRoleT]):
    system_roles: List[SystemRoleT] = Field(..., description="System roles")


class OptionalSystemRolesMixin(BaseModel, Generic[SystemRoleT]):
    system_roles: Optional[List[SystemRoleT]] = Field(..., description="System roles")
