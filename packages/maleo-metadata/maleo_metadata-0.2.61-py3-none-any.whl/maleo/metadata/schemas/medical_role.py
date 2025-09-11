from maleo.schemas.request import (
    ReadSingleQuery as BaseReadSingleQuery,
    ReadPaginatedMultipleQuery,
)
from ..mixins.medical_role import Granularity


class CommonQuery(Granularity):
    pass


class ReadSingleQuery(CommonQuery, BaseReadSingleQuery):
    pass


class ReadMultipleQuery(CommonQuery, ReadPaginatedMultipleQuery):
    pass
