from enum import StrEnum


class Granularity(StrEnum):
    BASIC = "basic"
    STANDARD = "standard"
    FULL = "full"


class IdentifierType(StrEnum):
    ID = "id"
    UUID = "uuid"
    KEY = "key"
    NAME = "name"


class Key(StrEnum):
    UNDISCLOSED = "undisclosed"
    FEMALE = "female"
    MALE = "male"
