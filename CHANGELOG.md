# Changelog

## Version 0.1.0a

* project initialization
* allows ingestion of files using either a file system or a web crawler option
* options available:

  ```terminal
  SpyderGPT is a chatbot powered by an offline GPT4All LLM, trained
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
  ```

## Version 0.2.0

* Dropped the `a` from version for `PEP 440``
* Modified package namespace to use `.` notation
