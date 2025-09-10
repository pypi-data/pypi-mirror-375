# demo137

A sample Python package for demonstration purposes.

[![PyPI version](https://badge.fury.io/py/demo137.svg)](https://badge.fury.io/py/demo137)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/badge/demo137)](https://pepy.tech/project/demo137)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue)](https://www.linkedin.com/in/eugene-evstafev-716669181/)

demo137 is a small, pure-Python package that provides a handy utility for summarizing a list of integers.

Installation
-------------
pip install demo137

Usage
-----
The package exposes a single pure function:

- summarize_numbers(numbers)
  - Input: a sequence of integers (e.g., list or tuple)
  - Output: a dictionary with the following keys:
    - count: number of elements
    - total: sum of elements
    - min: minimum value or None if empty
    - max: maximum value or None if empty
    - average: arithmetic mean or None if empty

Example
-------
```python
from demo137 import summarize_numbers

numbers = [1, 2, 3, 4, 5]
summary = summarize_numbers(numbers)
print(summary)
# Output: {'count': 5, 'total': 15, 'min': 1, 'max': 5, 'average': 3.0}
```

License
-------
MIT License

Author
------
Eugene Evstafev <hi@eugene.plus>

Repository
----------
https://github.com/chigwell/demo137