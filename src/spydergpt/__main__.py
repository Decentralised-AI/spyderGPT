from pathlib import Path
from typing import Any

from docopt import docopt

from spydergpt.config import Constants
from spydergpt.operator import Operation
from spydergpt.enum import OperationsEnum
from spydergpt.exception import (
    InvalidOperationKeyError,
    NoNewDocumentsLoadedError,
)
from spydergpt.utils import extract_version

__version__ = f"{Path(__file__).parent.name} {extract_version()}"
# inherited to the docops class to generate the programs arguments
# and help document
__doc__ = """SpyderGPT is a chatbot powered by an offline GPT4All LLM, trained
on documents retrieved from website and local repositories.

Usage:
  spydergpt ingest (<worker>)... [--link=URLS]... [--settings=PATH]
  spydergpt chat
  spydergpt (-h | --help)
  spydergpt --version

Options:
  ingest <worker>  activates the specified worker
  chat             activates the chatbot
  -h --help        this help screen
  --link=URLS      one or more urls for direct download. Use with worker (url).
  --settings=PATH  merge with supplemental spydergpt.yml file
  --version        prints the version of the installed program

Arguments:
  worker: local - ingests from local directory
          web - crawls a website
          url - downloads a specific file
  URLS: One or more URL for the worker to download a file from
  PATH: The path to a supplemental spydergpt.yml file

"""


def validate_args(args):
    if args.get("chat"):
        return "Program exited. Chat feature is not yet implemented"

    invalid_args = set(args.get("<worker>")) - {"local", "web", "url"}

    try:
        if invalid_args:
            raise ValueError(f"Invalid <worker> args: {list(invalid_args)}")

        if "url" in args.get("<worker>") and not args.get("--link"):
            raise ValueError(
                "Incorrect usage. The '--link' option is required when using"
                " 'url' worker"
            )
    except ValueError as e:
        print(e.args[0] + "\n")
        print(__doc__)


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


def process_args(args: dict[str, Any]) -> str:
    """The objective of the process_args function is to process the command
    line arguments and return the processing results.

    Args:
        args (dict[str, Any]): dictionary of command line arguments

    Returns:
        str: the ingest processing results
    """
    validate_args(args)

    result = []

    try:
        # Try to get the settings from the Constants class using the
        # '--settings' argument from the input args
        settings = Constants.get_settings(args.get("--settings"))
        links = args.get("--link")

        # For each argument in the input args, if the argument is not None
        # and is in the operations dictionary, append the argument and the
        # result of calling the ingest function with the settings and argument
        # to the result list
        workers = args.get("<worker>")
        result = [
            f"{arg} {ingest(arg, settings=settings, links=links)}"
            for arg in workers
            if workers
            if args.get("ingest")
        ]

    # Since this is program can perform multiple operations, append the error
    # messages to the result list
    except (FileNotFoundError, ValueError) as e:
        result.append(f"An error occurred: {e}")
    except (NoNewDocumentsLoadedError, InvalidOperationKeyError) as e:
        result.append(e.args)

    # Join the res list with a comma and return the resulting string
    return ", ".join(result)


def initialize_program_with_args(args: dict[str, Any] = None) -> str:
    """The objective of the initialize_program function is to initialize the
    program with the given arguments and return the processing results by
    calling the process_args function.

    Args:
        args (dict, optional): A dictionary of arguments to initialize the
        program with. It is an optional input and defaults to None.

    Returns:
        str: The processing results returned by the process_args function.
    """
    # If the args input is not a dictionary, it is set to an empty dictionary.
    args = args or {}
    return process_args(args)


if __name__ == "__main__":
    args = docopt(__doc__, version=__version__)
    print(initialize_program_with_args(args))
