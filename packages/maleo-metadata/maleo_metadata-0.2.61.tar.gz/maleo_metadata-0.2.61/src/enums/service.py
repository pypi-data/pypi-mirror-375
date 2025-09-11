from enum import StrEnum
from maleo.enums.service import Key as BaseKey


class Granularity(StrEnum):
    BASIC = "basic"
    STANDARD = "standard"
    FULL = "full"


class IdentifierType(StrEnum):
    ID = "id"
    UUID = "uuid"
    KEY = "key"
    NAME = "name"


Key = BaseKey
