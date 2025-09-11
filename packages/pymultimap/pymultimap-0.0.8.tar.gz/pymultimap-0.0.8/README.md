# pymultimap

[![PyPI - Version](https://img.shields.io/pypi/v/pymultimap.svg)](https://pypi.org/project/pymultimap)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pymultimap.svg)](https://pypi.org/project/pymultimap)

-----

**Table of Contents**
- [MultiMap](#multimap)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## MultiMap

Python based Dictionary with support for duplicate keys and sorted data based on keys

## Installation

```console
pip install pymultimap
```

## Usage

```python
from pymultimap.multimap import MultiMap

mm = MultiMap()
mm["a"] = 1
mm["a"] = 2
mm["b"] = 3

print(mm)

Should print :
{a: [1, 2], b: [3]}

```

```python
from pymultimap.multimap import MultiMap

sorted_multimap = MultiMap(sorted=True, reverse=True)
sorted_multimap["a"] = 1
sorted_multimap["c"] = 3
sorted_multimap["b"] = 2

print(sorted_multimap)

Should print :
{c: [3], b: [2], a: [1]}

```

## License

`pymultimap` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
