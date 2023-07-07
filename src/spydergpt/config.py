from collections import namedtuple
from pathlib import Path
from typing import Any, Dict, Optional, Type, Union

import yaml
from langchain.document_loaders import (
    CSVLoader,
    PDFMinerLoader,
    TextLoader,
    UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader,
)
from munch import Munch, munchify

from spydergpt.wrapper import EmlLoaderWrapper
from spydergpt.utils import merge


def _get_config(path: Union[Path, str], filename: str) -> Dict[Any, Any]:
    """read the contents of a YAML file and return it as a dictionary.

    Args:
        path (Union[Path, str]): path to YAML file
        filename (str): the yml file name

    Returns:
        Dict[Any, Any]: contents of yml
    """
    path = Path(path)
    if path.is_dir():
        path = path / filename
    with open(path) as f:
        return yaml.safe_load(f)


def get_config(path: Optional[Union[Path, str]] = None) -> Dict[Any, Any]:
    """read the contents of a YAML file and return it as a dictionary. It also
    merges the default configuration with the user-defined configuration, if
    provided.

    Args:
        path (Optional[Union[Path, str]], optional): path to YAML file.
        Defaults to None.

    Returns:
        Dict[Any, Any]: contents of yml
    """
    filename = "spydergpt.yml"
    default_config = _get_config(Path(__file__).parent / "data", filename)

    if path is None:
        path = Path() / filename
        if not path.is_file():
            return default_config
    config = _get_config(path, filename) if path else None

    return merge(default_config, config)


Loader = namedtuple("Loader", ["loader_type", "loader_settings"])


class LoaderFactory:
    """The LoaderFactory class is responsible for creating the appropriate
    loader for a given file extension. It contains a single class method,
    create_loader, which takes an extension string as input and returns the
    corresponding loader class. This class is used by the Constants class to
    create a mapping between file extensions and loader classes.
    """

    @classmethod
    def create_loader(cls, extension: str) -> Type[Loader]:
        """class method that takes an extension string as input and returns
        the corresponding loader class. It uses a match statement to determine
        the appropriate loader based on the extension.

        Args:
            extension (str): the file extension

        Raises:
            ValueError: raised if extension is empty or not supported

        Returns:
            Type[Loader]: the appropriate loader for the given file extension
        """
        if not extension:
            raise ValueError("Extension cannot be empty or None")

        match extension:
            case ".csv":
                return CSVLoader
            case ".doc" | ".docx":
                return UnstructuredWordDocumentLoader
            case ".eml":
                return EmlLoaderWrapper
            case ".pdf":
                return PDFMinerLoader
            case ".ppt" | ".pptx":
                return UnstructuredPowerPointLoader
            case ".txt":
                return TextLoader
            case _:  # unsupported extension
                raise ValueError(f"Unsupported file extension: {extension}")


class Constants:
    """The Constants class is responsible for providing access to the
    configuration settings stored in a YAML file. It uses the get_config
    function to read the contents of the YAML file and merge the default
    configuration with the user-defined configuration, if provided. The
    class also creates a Munch object from the configuration dictionary,
    which allows for easy access to the configuration settings as attributes.
    """

    # mapped file extensions to document loaders and their arguments.
    LOADER_MAPPING: Dict[str, Loader] = {
        extension: Loader(LoaderFactory().create_loader(extension), {})
        for extension in (
            ".csv",
            ".doc",
            ".docx",
            ".eml",
            ".pdf",
            ".ppt",
            ".pptx",
            ".txt",
        )
    }

    # stores the Munch object created from the configuration dictionary. It is
    # initialized to None and only created when the get_settings method is
    # called.
    _settings: Munch = None

    @classmethod
    def get_settings(cls, path: Optional[Union[Path, str]] = None):
        """Class method that takes an optional path argument and returns the
        configuration settings as a Munch object. If the _settings field is
        None, it creates a Munch object from the configuration dictionary
        returned by the get_config function.

        Args:
            path (Optional[Union[Path, str]], optional): path to YAML file.
            Defaults to None.

        Raises:
            Exception: raised if munchify failed

        Returns:
            Munch: A Munchified yml file
        """
        config = get_config(path)
        if cls._settings is None:
            if config is not None:
                try:
                    cls._settings = munchify(config)
                except Exception as e:
                    raise Exception(f"Error while creating Munch object: {e}")
        return cls._settings


class ChromaSettings:
    """The ChromaSettings class is designed to store and manage settings
    related to Chroma, a Python package for working with color spaces. It
    takes in a Munch object containing the necessary settings and initializes
    the class with the relevant attributes. The class provides properties for
    accessing the settings, vectorstore, parquet, and persist_directory fields.
    """

    def __init__(self, settings: Munch):
        """initializes the class with the given settings.

        Args:
            settings (Munch): settings related to Chroma

        Raises:
            AttributeError: raised if the settings do not contain the required
            chroma field
        """
        try:
            chroma = settings.chroma
            self._settings = chroma.settings
            self._vectorstore = chroma.vectorstore
            self._parquet = chroma.parquet
            self._persist_directory = chroma.settings.persist_directory
        except AttributeError as e:
            raise AttributeError(f"Settings must contain chroma, {e}")

    @property
    def settings(self: Dict[Any, Any] = {}) -> Dict[Any, Any]:
        """contains the settings related to Chroma

        Args:
            self (dict, optional): settings related to Chroma. Defaults to {}.

        Returns:
            Dict[Any, Any]: dictionary of settings
        """
        return self._settings

    @property
    def vectorstore(self: Dict[Any, Any] = {}) -> Dict[Any, Any]:
        """contains the vectorstore related to Chroma

        Args:
            self (dict, optional): settings related to Chroma. Defaults to {}.

        Returns:
            Dict[Any, Any]: dictionary of settings
        """
        return self._vectorstore

    @property
    def parquet(self: Dict[Any, Any] = {}) -> Dict[Any, Any]:
        """contains the parquet related to Chroma

        Args:
            self (dict, optional): settings related to Chroma. Defaults to {}.

        Returns:
            Dict[Any, Any]: dictionary of settings
        """
        return self._parquet

    @property
    def persist_directory(self: str = None) -> str:
        """contains the persist_directory related to Chroma

        Args:
            self (str): setting related to Chroma. Defaults to {}.

        Returns:
           str: chroma setting
        """
        return self._persist_directory
