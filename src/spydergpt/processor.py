from .worker.localworker import LocalWorker
from .worker.urlworker import UrlWorker
from .worker.webworker import WebWorker


def process_from_local(kwargs):
    """Imports files into the vectorstore from a local path.

    Args:
        settings: A dictionary containing the settings for the importer.
    """
    importer = LocalWorker(kwargs["settings"])
    return (
        "Files imported successfully"
        if importer.ingest()
        else "No files were imported locally"
    )


def process_from_web(kwargs):
    """Imports files into the vectorstore from the web.

    Args:
        settings: A dictionary containing the settings for the crawler.
    """
    importer = WebWorker(kwargs["settings"])
    return (
        "Automated download and import was successful"
        if importer.ingest()
        else "No files were imported from the web"
    )


def url_direct_download(kwargs):
    success = True

    for link in kwargs["links"]:
        importer = UrlWorker(link, kwargs["settings"])
        success &= importer.ingest()

    return (
        "Automated download and import was successful"
        if success
        else "A file was not imported from an URL"
    )
