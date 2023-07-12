from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List

from chromadb.config import Settings
from langchain.docstore.document import Document
from langchain.vectorstores import Chroma
from langchain.vectorstores.base import VectorStore
from munch import Munch

from ..config import ChromaSettings
from ..exception.exceptions import NoNewDocumentsLoadedError
from ..utils import get_files, get_embeddings


class WorkerBase(ABC):
    """The ImporterBase class is an abstract base class that provides methods
    for ingesting and processing documents to create embeddings. It defines
    methods for gathering documents, creating and updating a vectorstore, and
    persisting the vectorstore. It also provides methods for checking if a
    vectorstore already exists and for determining if there are enough index
    files present to create a new vectorstore.

    Args:
        ABC (ABC): Base class that provides a standard way to create an ABC
        using inheritance
    """

    # a Settings object that contains various settings for the vectorstore
    settings: Settings = None
    # a ChromaSettings object that contains settings specific to the Chroma
    # vectorstore, such as the persist directory, vectorstore settings, and
    # parquet settings.
    chromastore_settings: ChromaSettings = None

    def __init__(self, settings: Munch):
        """Initialize a new ImporterBase object

        Args:
            settings (Munch): Muchified yml settings
        """
        self.settings = settings
        self.chromastore_settings = ChromaSettings(settings)

    @abstractmethod
    def _gather(self, collection: Dict[str, Any] = None) -> List[Document]:
        """Abstract method designed to gather documents to be ingested and
        processed.

        Args:
            collection (Dict[str, Any], optional): A dictionary of Vectorstore
            fields. Defaults to None.
        """
        pass

    def _get_vectorstore(self, documents: List[Document] = None):
        """Creates a new Chroma vectorstore or updates an existing one

        Args:
            documents (List[Document], optional): the documents to train LLM.
            Defaults to None.

        Returns:
            VectorStore: Chroma client
        """
        # Update and store locally embeddings
        embeddings = get_embeddings(self.settings)

        if documents:
            return Chroma.from_documents(
                documents,
                embeddings,
                persist_directory=self.chromastore_settings.persist_directory,
                client_settings=Settings(**self.chromastore_settings.settings),
            )

        return Chroma(
            persist_directory=self.chromastore_settings.persist_directory,
            embedding_function=embeddings,
            client_settings=Settings(**self.chromastore_settings.settings),
        )

    def _does_vectorstore_exist(self) -> bool:
        """Checks if a vectorstore already exists

        Returns:
            bool: if vectorstore exists
        """
        vectorstore = self.chromastore_settings.vectorstore
        parquetstore = self.chromastore_settings.parquet

        persist_path = Path(self.chromastore_settings.persist_directory)
        index_path = persist_path / vectorstore.index
        collections = parquetstore.collections
        embeddings = parquetstore.embeddings
        v_bin = vectorstore.bin
        v_pickle = vectorstore.pickle

        collections_path = persist_path / collections
        embeddings_path = persist_path / embeddings

        list_index_files = get_files(index_path, [v_bin, v_pickle])

        return (
            index_path.is_dir()
            and collections_path.is_file()
            and embeddings_path.is_file()
            and len(list_index_files) >= 3
        )

    def _create_vectorstore(self, texts: List[Document]) -> VectorStore:
        """Creates a new vectorstore

        Args:
            texts (List[Document]): collection of Documents to be embedded

        Returns:
            VectorStore: ChromaDB client
        """
        return self._get_vectorstore(documents=texts)

    def ingest(self) -> bool:
        """Ingests and processes documents to create embeddings and persists
        the vectorstore

        Returns:
            bool: boolean value whether or not documents were loaded into
            vectorstore
        """
        print("Creating embeddings. May take some minutes...")

        try:
            if self._does_vectorstore_exist():
                print("Appending to existing vectorstore")
                db: VectorStore = self._get_vectorstore()
                collection = db.get()
                texts = self._gather(collection)
                db.add_documents(texts)
            else:
                # Create and store locally vectorstore
                print("Creating new vectorstore")
                texts = self._gather()
                db = self._create_vectorstore(texts)
        except NoNewDocumentsLoadedError:
            return False
        db.persist()
        db = None

        return True
