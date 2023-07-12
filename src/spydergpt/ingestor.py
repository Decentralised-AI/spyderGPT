from .operator import Operation
from .enum.operationsenum import OperationsEnum
from .exception.exceptions import InvalidOperationKeyError


def ingest(
    arg: str,
    **kwargs: str,
) -> str:
    """The objective of the ingest function is to take in a settings location
    and an argument, and return the results of a dictionary mapping.

    Args:
        settings (str): path to alternate application YAML settings. Optional.
        arg (str): argument string to extract from dictionary mapping.
        operations (dict[str, Any]): dictionary of callable operations

    Returns:
        str: ingesting results
    """
    # Check if the argument is valid by checking if it is in the operations
    # dictionary.
    op = Operation()

    try:
        # call and return the corresponding function from the operations
        # dictionary with the settings location as the argument.

        if callable(op.operations[OperationsEnum(arg)]):
            return op.perform_operation(OperationsEnum(arg), kwargs)
        else:
            raise ValueError(f"Invalid operation: {arg}")
    except (ValueError, InvalidOperationKeyError) as e:
        # If an exception is raised during the function call, raise it to
        # the top of the stack
        raise e
