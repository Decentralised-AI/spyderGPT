from .enum.operationsenum import OperationsEnum
from .exception.exceptions import InvalidOperationKeyError
from .processor import process_from_web, process_from_local, url_direct_download


class Operation:
    """Class to perform operations on files."""

    def __init__(self):
        """Initializes an instance of the Operations class.

        The 'operations' attribute is a dictionary containing the available
        operations.
        """
        self.operations = {
            OperationsEnum.WEB: process_from_web,
            OperationsEnum.LOCAL: process_from_local,
            OperationsEnum.URL: url_direct_download,
        }

    def perform_operation(self, operation_key, kwargs) -> str:
        """Performs the specified operation on files.

        Args:
            operation_key (OperationsEnum): the enum relevant to the operation
            settings (Munch, optional): application settings. Defaults to None.

        Raises:
            InvalidOperationKeyError: raised if key does not exist
            Exception: raises any exceptions from further down the stack

        Returns:
            str: completion status message
        """
        try:
            if operation_key in OperationsEnum:
                return self.operations[OperationsEnum(operation_key)](kwargs)
            else:
                raise InvalidOperationKeyError("Invalid operations key")
        except Exception as e:
            raise e
