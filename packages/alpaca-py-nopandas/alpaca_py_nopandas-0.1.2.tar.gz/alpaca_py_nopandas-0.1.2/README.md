[![Python Versions](https://img.shields.io/pypi/pyversions/alpaca-py.svg?logo=python&logoColor=white)](https://pypi.org/project/alpaca-py-nopandas)
[![GitHub](https://img.shields.io/github/license/alpacahq/alpaca-py?color=blue)](https://github.com/alpacahq/alpaca-py/blob/master/LICENSE.md)
[![PyPI](https://img.shields.io/pypi/v/alpaca-py?color=blue)](https://pypi.org/project/alpaca-py-nopandas/)

Forked version of alpaca-py project with Pandas dependency removed.

See https://github.com/alpacahq/alpaca-py

# Build and Deploy

`poetry build`

`uvx twine upload dist/*`