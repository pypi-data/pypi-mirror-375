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
from ..enums.user_type import (
    Granularity as GranularityEnum,
    IdentifierType,
    Key as UserTypeKey,
)
from ..mixins.user_type import Granularity, Key, Name
from ..types.user_type import IdentifierValueType


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


class BaseUserTypeData(
    Name[str],
    Key,
    Order[OptionalInteger],
):
    pass


class BasicUserTypeData(
    BaseUserTypeData,
    DataStatus,
    DataIdentifier,
):
    pass


class StandardUserTypeData(
    BaseUserTypeData,
    DataStatus,
    DataLifecycleTimestamp,
    DataIdentifier,
):
    pass


class FullUserTypeData(
    BaseUserTypeData,
    DataStatus,
    DataTimestamp,
    DataIdentifier,
):
    pass


UserTypeDataT = TypeVar(
    "UserTypeDataT",
    BasicUserTypeData,
    StandardUserTypeData,
    FullUserTypeData,
)


UserTypeT = TypeVar(
    "UserTypeT",
    UserTypeKey,
    BasicUserTypeData,
    StandardUserTypeData,
    FullUserTypeData,
)


class UserTypeMixin(BaseModel, Generic[UserTypeT]):
    user_type: UserTypeT = Field(..., description="User type")


class OptionalUserTypeMixin(BaseModel, Generic[UserTypeT]):
    user_type: Optional[UserTypeT] = Field(..., description="User type")


class UserTypesMixin(BaseModel, Generic[UserTypeT]):
    user_types: List[UserTypeT] = Field(..., description="User types")


class OptionalUserTypesMixin(BaseModel, Generic[UserTypeT]):
    user_types: Optional[List[UserTypeT]] = Field(..., description="User types")
