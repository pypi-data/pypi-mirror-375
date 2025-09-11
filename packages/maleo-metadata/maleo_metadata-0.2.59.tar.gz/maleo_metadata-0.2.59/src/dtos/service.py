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
from maleo.enums.service import ServiceType as ServiceTypeEnum, Category as CategoryEnum
from maleo.mixins.general import Order
from maleo.mixins.parameter import IdentifierTypeValue
from maleo.types.base.integer import OptionalInteger
from maleo.types.base.string import OptionalString
from maleo.types.enums.status import ListOfDataStatuses
from ..enums.service import (
    Granularity as GranularityEnum,
    IdentifierType,
    Key as ServiceKey,
)
from ..mixins.service import Granularity, ServiceType, Category, Key, Name, Secret
from ..types.service import IdentifierValueType


class CommonParameter(Granularity):
    pass


class CreateData(
    Name[str],
    Key,
    ServiceType[ServiceTypeEnum],
    Category[CategoryEnum],
    Order[OptionalInteger],
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
    ServiceType[ServiceTypeEnum],
    Category[CategoryEnum],
    Order[OptionalInteger],
):
    pass


class PartialUpdateData(
    Name[OptionalString],
    ServiceType[Optional[ServiceTypeEnum]],
    Category[Optional[CategoryEnum]],
    Order[OptionalInteger],
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


class BaseServiceData(
    Secret,
    Name[str],
    Key,
    ServiceType[ServiceTypeEnum],
    Category[CategoryEnum],
    Order[OptionalInteger],
):
    pass


class BasicServiceData(
    BaseServiceData,
    DataStatus,
    DataIdentifier,
):
    pass


class StandardServiceData(
    BaseServiceData,
    DataStatus,
    DataLifecycleTimestamp,
    DataIdentifier,
):
    pass


class FullServiceData(
    BaseServiceData,
    DataStatus,
    DataTimestamp,
    DataIdentifier,
):
    pass


ServiceDataT = TypeVar(
    "ServiceDataT",
    BasicServiceData,
    StandardServiceData,
    FullServiceData,
)


ServiceT = TypeVar(
    "ServiceT",
    ServiceKey,
    BasicServiceData,
    StandardServiceData,
    FullServiceData,
)


class ServiceMixin(BaseModel, Generic[ServiceT]):
    service: ServiceT = Field(..., description="Service")


class OptionalServiceMixin(BaseModel, Generic[ServiceT]):
    service: Optional[ServiceT] = Field(..., description="Service")


class ServicesMixin(BaseModel, Generic[ServiceT]):
    services: List[ServiceT] = Field(..., description="Services")


class OptionalServicesMixin(BaseModel, Generic[ServiceT]):
    services: Optional[List[ServiceT]] = Field(..., description="Services")
