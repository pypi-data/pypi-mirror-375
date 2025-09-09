# PyRestr

PyRestr is a small Python library for working with dictionaries, strings, and numbers easily.

## Features

- Dictionary utilities
- String utilities
- Number utilities

## Usage Examples

```python
import pyrestr

# Dictionaries
pyrestr.keybyval({"a": 1, "b": 2}, 2)  # returns "b"

# Strings
pyrestr.rev("Python")                   # returns "nohtyP"
pyrestr.titlecase("hello world")       # returns "Hello World"

# Numbers
pyrestr.is_even(10)                     # returns True
pyrestr.factorial(5)                    # returns 120
