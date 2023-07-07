from enum import Enum

from spydergpt.enum import MetaEnum


class OperationsEnum(Enum, metaclass=MetaEnum):
    """The OperationsEnum class is an enumeration class that defines two
    possible values for an operation: WEB and LOCAL. It inherits from the
    Enum class and uses the MetaEnum metaclass to ensure that only valid
    members are allowed in the enumeration.
    """

    WEB = "web"
    LOCAL = "local"
    URL = "url"
