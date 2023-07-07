import os
import tempfile
from concurrent.futures import ThreadPoolExecutor
from mimetypes import guess_extension
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import requests
from bs4 import BeautifulSoup
from langchain.docstore.document import Document
from munch import Munch
from pandas import DataFrame

from spydergpt.loader import DocumentLoader
from spydergpt.exception import NoNewDocumentsLoadedError
from spydergpt.worker import WorkerBase


class WebWorker(WorkerBase):
    """The WebImporter class is a subclass of ImporterBase and provides methods
    for crawling web pages, downloading files, and processing them to create
    embeddings. It defines methods for parsing HTML tables, extracting links,
    and downloading files from URLs. It also provides a method for gathering
    documents to be ingested and processed.
    """

    def __init__(self, settings: Munch):
        """initializes the WebImporter class.

        Args:
            settings (Munch): application settings
        """
        super().__init__(settings)

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

    def _parse_html_table(self, url: str) -> str:
        """parses an HTML table from a given URL and returns it as a string.

        Args:
            url (str): URL to retrieve page content from

        Raises:
            ValueError: raised if an error occurred with the URL

        Returns:
            str: table data parsed from URL
        """
        try:
            self._mount_http_session()
            page = self._session.get(url, timeout=10)
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error loading URL '{url}': {str(e)}")

        soup = BeautifulSoup(page.content, "html.parser")
        return str(soup.find("table", {"id": "rpt"}))

    def _get_links(self, table: str) -> DataFrame:
        """extracts links from an HTML table and returns them as a Pandas
        DataFrame.

        Args:
            table (str): table data parsed from HTML

        Returns:
            DataFrame: Pandas Dataframe containing columnar table data
        """
        df = pd.read_html(table, extract_links="body")[0]
        col_number = df.columns[0]
        col_title = df.columns[1]

        df["Title"], df["url"] = df[col_title].str[0], df[col_title].str[1]
        df["ShortTitle"] = col_number.split()[0] + " " + df[col_number].str[0]

        df = df[df["url"].notna()]

        return df[["ShortTitle", "url"]]

    def _download_single_file(self, url: str, dest_folder: str, title: str):
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
            r = self._session.get(url, stream=True)
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error loading URL '{url}': {str(e)}")

        if r.ok:
            response_headers = r.headers
            file_extension = guess_extension(
                response_headers["content-type"].partition(";")[0].strip()
            )

            file_path = Path(dest_folder) / f"{title}{file_extension}"

            print("saving to", str(file_path))
            with open(file_path, "wb") as f:
                f.write(r.content)
        else:  # HTTP status code 4XX/5XX
            msg = f"Download failed: status code {r.status_code}\n{r.text}"
            print(msg)

    def _download(self, data_dict: list[dict], dest_folder: str):
        """downloads files from a list of dictionaries containing URLs and
        titles and saves them to a destination folder.

        Args:
            data_dict (list[dict]): Dict containing URLs and document title
            dest_folder (str): path where files are stored
        """
        crawler = self.settings.crawler

        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            futures = []
            for dic in data_dict:
                title = dic["ShortTitle"]
                url = crawler.root + dic["url"]
                futures.append(
                    executor.submit(
                        self._download_single_file, url, dest_folder, title
                    )
                )

            for future in futures:
                future.result()

    def _gather(self, collection: Dict[str, Any] = None) -> List[Document]:
        """gathers documents to be ingested and processed by downloading files
        from URLs and processing them to create embeddings.

        Args:
            collection (Dict[str, Any], optional): vectorestore metadata.
            Defaults to None.

        Raises:
            ValueError: raised if the URL and path are not complete
            NoNewDocumentsLoadedError: raised if documents were not loaded

        Returns:
            List[Document]: documents gathered from web parser
        """
        crawler = self.settings.crawler

        if not crawler.root or not crawler.paths:
            raise ValueError("Crawler needs complete URL and paths")

        ignored_files = (
            [metadata["source"] for metadata in collection["metadatas"]]
            if collection
            else []
        )

        with tempfile.TemporaryDirectory() as tmpdirname:
            loader = DocumentLoader(
                ignored_files=ignored_files, settings=self.settings
            )

            for path in crawler.paths:
                pubs_url = crawler.root + path
                temp_dir = Path(tmpdirname)

                df = self._get_links(self._parse_html_table(pubs_url))
                self._download(df.to_dict("records"), temp_dir)

                loader.load(source_dir=temp_dir)

                try:
                    loader.process()

                    if not loader.processed_texts:
                        raise NoNewDocumentsLoadedError(
                            "No new documents to load"
                        )
                    else:
                        print(
                            f"Loaded {len(loader.processed_texts)} new chunks"
                        )
                except NoNewDocumentsLoadedError as e:
                    raise e

        return loader.processed_texts
