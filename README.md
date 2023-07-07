# SpyderGPT

This program uses an offline GPT4All LLM, trained on documents retrieved from website and local repositories. Document metadata is stored locally in `ChromaDB`.

This is still in its early alpha stages and is constantly undergoing major changes.

## Installation

The package was built with `python 3.10` installed and I use [flit](https://flit.pypa.io/en/latest/cmdline.html) to build and install.

## Crawler Modification

Before building and deploying, you will need to modify the `Crawler._parse_html_table` and `Crawler._get_links` class methods to fit the target URL's content.

## Build and Install

Building with `Flit` is straightforward, and you can find the available options in the official docs. Let's do a local build and install the resulting package.

1. Remove working packages from previous installs: `pip uninstall -y spydergpt`.
2. Build a wheel and a sdist (tarball) from the source: `flit build`. When the build finishes, you should see a message similar to `Built wheel: dist\spydergpt-[version]-py3-none-any.whl` in the console.
3. Install using Pip to ensure the package is Pip-compatible: `pip install dist\spydergpt-[version]-py3-none-any.whl`.

Or if preferred, you can install directly from the repository `pip install git+<url>`

Automated testing, using `unittest` can be achieved from the package root via the commandline; this will execute all tests in one batch. Variations shown below.

```terminal
C:\>python -m unittest discover -s tests
C:\>python -m unittest discover -s tests/unit
C:\>python -m unittest discover -s tests/integration
```
