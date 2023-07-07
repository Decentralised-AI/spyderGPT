import glob
import multiprocessing
from functools import partial
from multiprocessing import Pool
from pathlib import Path
from typing import Any, Dict, List

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm

from spydergpt.config import Constants
from spydergpt.exception import NoNewDocumentsLoadedError


class DocumentLoader:
    ignored_files: List[str] = None
    settings: Dict[str, Any] = None

    documents: List[Document] = []
    processed_texts: List[Document] = []

    def __init__(self, ignored_files: List[str], settings: Dict[str, Any]):
        self.ignored_files = ignored_files
        self.settings = settings

    def _load_single_document(self, file_path: str):
        ext = Path(file_path).suffix

        if ext in Constants.LOADER_MAPPING:
            try:
                loader_class, loader_args = Constants.LOADER_MAPPING[ext]
                loader = loader_class(file_path, **loader_args)
                return loader.load()[0]
            except KeyError:
                raise ValueError(f"Unsupported file extension '{ext}'")
            except Exception as e:
                raise ValueError(f"Error loading file '{file_path}': {str(e)}")

        raise ValueError(f"Unsupported file extension '{ext}'")

    def load(self, source_dir: Path):
        print(f"Loading documents from {source_dir}")

        all_files = []
        for ext in Constants.LOADER_MAPPING:
            source = str(source_dir / f"**/*{ext}")
            all_files.extend(glob.glob(source, recursive=True))

        filtered_files = [
            file_path
            for file_path in all_files
            if file_path not in self.ignored_files
        ]

        with Pool(processes=multiprocessing.cpu_count()) as pool:
            with tqdm(
                total=len(filtered_files),
                desc="Loading new documents",
                ncols=80,
            ) as pbar:
                pool_enum = enumerate(
                    pool.imap_unordered(
                        partial(self._load_single_document), filtered_files
                    )
                )
                for i, doc in pool_enum:
                    self.documents.append(doc)
                    pbar.update()

    def process(self):
        if not self.documents:
            raise NoNewDocumentsLoadedError(
                "No new documents were loaded during processing"
            )

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.textsplitter.size,
            chunk_overlap=self.settings.textsplitter.overlap,
        )

        texts = text_splitter.split_documents(self.documents)
        self.processed_texts = texts

        print(
            f"Split into {len(texts)} chunks of text "
            f"(max. {self.settings.textsplitter.size} tokens each)"
        )
