from enum import EnumMeta
from typing import Any


class MetaEnum(EnumMeta):
    """metaclass that checks if the given item is a valid member of the
    enumeration. It returns a boolean value of whether or not the item is in
    the enum
    """

    def __contains__(cls, item: Any):
        """Check if the given item is a valid member of the enumeration.

        Args:
            item (Any): the item to look validate in enum

        Returns:
            bool: boolean value of whether or not item is in enum
        """
        try:
            cls(item)
        except ValueError:
            return False
        else:
            return True
