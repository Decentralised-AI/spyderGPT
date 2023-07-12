import os
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List
from munch import Munch

import requests
from langchain.docstore.document import Document

from ..loader import DocumentLoader
from ..exception.exceptions import NoNewDocumentsLoadedError
from .workerbase import WorkerBase


class UrlWorker(WorkerBase):
    """The WebImporter class is a subclass of ImporterBase and provides methods
    for crawling web pages, downloading files, and processing them to create
    embeddings. It defines methods for parsing HTML tables, extracting links,
    and downloading files from URLs. It also provides a method for gathering
    documents to be ingested and processed.
    """

    def __init__(self, url: str, settings: Munch):
        """initializes the WebImporter class."""
        super().__init__(settings)
        self.url = url

    def _mount_http_session(self):
        """creates an HTTP session and mounts an HTTP adapter for handling
        requests.
        """
        if not hasattr(self, "_session"):
            self._session = requests.Session()
            adapter = requests.adapters.HTTPAdapter(
                pool_connections=100, pool_maxsize=100
            )
            self._session.mount("https://", adapter)

    def _download_single_file(self, dest_folder: str, file_name: str):
        """downloads a file from a given URL and saves it to a destination
        folder with a given title.

        Args:
            url (str): the URL to be parsed
            dest_folder (str): path to retrieve documents from
            title (str): document title

        Raises:
            ValueError: error raised if URL failed to load
        """
        try:
            self._mount_http_session()
            r = self._session.get(self.url, stream=True, verify=False)
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error loading URL '{self.url}': {str(e)}")

        if r.ok:
            file_path = Path(dest_folder) / f"{file_name}"

            print("saving to", str(file_path))
            with open(file_path, "wb") as f:
                f.write(r.content)
        else:  # HTTP status code 4XX/5XX
            msg = f"Download failed: status code {r.status_code}\n{r.text}"
            print(msg)

    def _download(self, dest_folder: str):
        """downloads files from a list of dictionaries containing URLs and
        titles and saves them to a destination folder.

        Args:
            data_dict (list[dict]): Dict containing URLs and document title
            dest_folder (str): path where files are stored
        """
        if self.url:
            urlParts = self.url.split("/")
            filename = urlParts[len(urlParts) - 1]

        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            futures = []
            futures.append(
                executor.submit(
                    self._download_single_file, dest_folder, filename
                )
            )

            for future in futures:
                future.result()

    def _gather(self, collection: Dict[str, Any] = None) -> List[Document]:
        """gathers documents to be ingested and processed by downloading a file
        from a URL and processing them to create embeddings.

        Args:
            collection (Dict[str, Any], optional): vectorestore metadata.
            Defaults to None.

        Raises:
            ValueError: raised if the URL is not complete
            NoNewDocumentsLoadedError: raised if documents were not loaded

        Returns:
            List[Document]: documents gathered from web parser
        """
        ignored_files = (
            [metadata["source"] for metadata in collection["metadatas"]]
            if collection
            else []
        )

        with tempfile.TemporaryDirectory() as tmpdirname:
            loader = DocumentLoader(
                ignored_files=ignored_files, settings=self.settings
            )

            temp_dir = Path(tmpdirname)

            self._download(temp_dir)
            loader.load(source_dir=temp_dir)

            try:
                loader.process()

                if not loader.processed_texts:
                    raise NoNewDocumentsLoadedError("No new documents to load")
                else:
                    print(f"Loaded {len(loader.processed_texts)} new chunks")
            except NoNewDocumentsLoadedError as e:
                raise e

        return loader.processed_texts
