from contextlib import suppress
from importlib.metadata import metadata
from pathlib import Path
from typing import Any, Dict, List

from deepmerge import always_merger
from langchain.embeddings import (
    HuggingFaceEmbeddings,
    HuggingFaceInstructEmbeddings,
)
from langchain.embeddings.base import Embeddings
from munch import Munch


def merge(a: Dict[Any, Any], b: Dict[Any, Any]) -> Dict[Any, Any]:
    """The objective of the 'merge' function is to merge two dictionaries
    'a' and 'b' into a new dictionary 'c', using the 'always_merger' function
    from the 'deepmerge' library. The resulting dictionary 'c' will contain
    all the key-value pairs from both 'a' and 'b', with any overlapping keys
    being resolved by the 'always_merger' function.

    Args:
        a (Dict[Any, Any]): a dictionary containing key-value pairs for merging
        b (Dict[Any, Any]): a dictionary containing key-value pairs for merging

    Returns:
        Dict[Any, Any]: a new dictionary containing all the key-value pairs
        from both 'a' and 'b', with any overlapping keys being resolved by the
        'always_merger' function
    """
    c = {}
    always_merger.merge(c, a)
    always_merger.merge(c, b)
    return c


def get_files(file_path: Path, extensions: list[str]) -> List[str]:
    """The objective of the 'get_files' function is to retrieve a list of file
    paths that match the specified file extensions within a given directory
    path.

    Args:
        file_path (Path): a Path object representing the directory path to
        search for files
        extensions (list[str]): a list of file extensions to search for,
        represented as strings

    Returns:
        List[str]: A list of file paths that match the specified file
        extensions within the given directory path
    """
    all_files = []
    for ext in extensions:
        all_files.extend(file_path.glob(ext))
    return all_files


def get_embeddings(settings: Munch) -> Embeddings:
    """The objective of the "get_embeddings" function is to return an instance
    of the "Embeddings" class based on the provided settings. The function
    checks if the model name in the settings starts with "hkunlp/" and if so,
    it returns an instance of the "HuggingFaceInstructEmbeddings" class.
    Otherwise, it returns an instance of the "HuggingFaceEmbeddings" class.

    Args:
        settings (Munch): a Munch object containing the settings for the
        embeddings. The object should have a "model_name" attribute that
        specifies the name of the model to use.

    Returns:
        Embeddings: An instance of the "Embeddings" class based on the
        provided settings.
    """
    if settings.embeddings.model_name.startswith("hkunlp/"):
        Provider = HuggingFaceInstructEmbeddings
    else:
        Provider = HuggingFaceEmbeddings
    return Provider(model_name=settings.embeddings.model_name)


def extract_version() -> str:
    """The objective of the "extract_version" function is to return the
    version of an installed package or the version found in a nearby
    pyproject.toml file.

    Returns:
        str: A string containing the version of the installed package or the version found in the pyproject.toml file.
    """
    with suppress(FileNotFoundError, StopIteration):
        with open(
            (root_dir := Path(__file__).parent.parent.parent)
            / "pyproject.toml",
            encoding="utf-8",
        ) as pyproject_toml:
            version = (
                next(
                    line
                    for line in pyproject_toml
                    if line.startswith("version")
                )
                .split(" = ")[1]
                .strip("'\"\n ")
            )
            return f"{version}-dev (at {root_dir})"
    return metadata.version(__name__.split(".", maxsplit=1)[0])
