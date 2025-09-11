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
from ..enums.organization_type import (
    Granularity as GranularityEnum,
    IdentifierType,
    Key as OrganizationTypeKey,
)
from ..mixins.organization_type import Granularity, Key, Name
from ..types.organization_type import IdentifierValueType


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


class BaseOrganizationTypeData(
    Name[str],
    Key,
    Order[OptionalInteger],
):
    pass


class BasicOrganizationTypeData(
    BaseOrganizationTypeData,
    DataStatus,
    DataIdentifier,
):
    pass


class StandardOrganizationTypeData(
    BaseOrganizationTypeData,
    DataStatus,
    DataLifecycleTimestamp,
    DataIdentifier,
):
    pass


class FullOrganizationTypeData(
    BaseOrganizationTypeData,
    DataStatus,
    DataTimestamp,
    DataIdentifier,
):
    pass


OrganizationTypeDataT = TypeVar(
    "OrganizationTypeDataT",
    BasicOrganizationTypeData,
    StandardOrganizationTypeData,
    FullOrganizationTypeData,
)


OrganizationTypeT = TypeVar(
    "OrganizationTypeT",
    OrganizationTypeKey,
    BasicOrganizationTypeData,
    StandardOrganizationTypeData,
    FullOrganizationTypeData,
)


class OrganizationTypeMixin(BaseModel, Generic[OrganizationTypeT]):
    organization_type: OrganizationTypeT = Field(..., description="Organization type")


class OptionalOrganizationTypeMixin(BaseModel, Generic[OrganizationTypeT]):
    organization_type: Optional[OrganizationTypeT] = Field(
        ..., description="Organization type"
    )


class OrganizationTypesMixin(BaseModel, Generic[OrganizationTypeT]):
    organization_types: List[OrganizationTypeT] = Field(
        ..., description="Organization types"
    )


class OptionalOrganizationTypesMixin(BaseModel, Generic[OrganizationTypeT]):
    organization_types: Optional[List[OrganizationTypeT]] = Field(
        ..., description="Organization types"
    )
