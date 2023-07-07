from pathlib import Path
from typing import Any, Dict, List

from langchain.docstore.document import Document
from munch import Munch

from spydergpt.loader import DocumentLoader
from spydergpt.exception import NoNewDocumentsLoadedError
from spydergpt.worker import WorkerBase


class LocalWorker(WorkerBase):
    """The LocalWorker class is a subclass of the abstract base class
    WorkerBase and provides methods for ingesting and processing local
    documents to create embeddings. It defines the _gather method for
    gathering documents, which loads documents from a specified directory
    and processes them using the DocumentLoader class. It also defines
    the ingest method, which creates a new vectorstore or updates an
    existing one with the processed documents and persists the vectorstore.
    """

    def __init__(self, settings: Munch):
        """initializes the LocalWorker class

        Args:
            settings (Munch): application settings
        """
        super().__init__(settings)

    def _gather(self, collection: Dict[str, Any] = None) -> List[Document]:
        """gathers documents to be ingested and processed by loading documents
        from a specified directory and processing them using the DocumentLoader
        class.

        Args:
            collection (Dict[str, Any], optional): collection of file metadata.
            Defaults to None.

        Raises:
            FileNotFoundError: raised if source is not found
            NoNewDocumentsLoadedError: raised if there was not any new
            documents to load

        Returns:
            List[Document]: collection of loaded Documents
        """
        print("gathering documents")
        sourcedocuments = Path(self.settings.sourcedocuments)

        if not sourcedocuments.exists():
            msg = (
                "sourcedocuments path not found."
                "Verify the setting in the config file and try again."
            )
            raise FileNotFoundError(msg)

        ignored_files = (
            [metadata["source"] for metadata in collection["metadatas"]]
            if collection
            else []
        )

        loader = DocumentLoader(
            ignored_files=ignored_files, settings=self.settings
        )
        loader.load(source_dir=sourcedocuments)
        loader.process()

        if not loader.processed_texts:
            raise NoNewDocumentsLoadedError("No new documents to load")
        else:
            print(f"Loaded {len(loader.processed_texts)} new chunks")

        return loader.processed_texts
