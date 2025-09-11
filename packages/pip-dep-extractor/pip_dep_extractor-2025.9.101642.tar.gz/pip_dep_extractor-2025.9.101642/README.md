[![PyPI version](https://badge.fury.io/py/pip_dep_extractor.svg)](https://badge.fury.io/py/pip_dep_extractor)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/badge/pip_dep_extractor)](https://pepy.tech/project/pip_dep_extractor)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue)](https://www.linkedin.com/in/eugene-evstafev-716669181/)

# pip_dep_extractor

`pip_dep_extractor` is a Python package designed to extract exactly 10 Python package names from an LLM response, using a specified pattern and validation.

## Installation

To install `pip_dep_extractor`, use pip:

```bash
pip install pip_dep_extractor
```

## Usage

Using `pip_dep_extractor` is straightforward. Here's an example:

```python
from pip_dep_extractor import extract_pip_dependencies
from langchain_llm7 import ChatLLM7

# Initialize your LLM instance here
llm = ChatLLM7(...)

custom_text = "This is a description of the package source."

try:
    dependencies = extract_pip_dependencies(llm, custom_text)
    print("Extracted dependencies:", dependencies)
except RuntimeError as e:
    print("Error:", e)
```

## Short Example

```python
from pip_dep_extractor import extract_pip_dependencies
from langchain_llm7 import ChatLLM7

llm = ChatLLM7()
custom_text = "Sample description of package that may include dependencies."

try:
    deps = extract_pip_dependencies(llm, custom_text)
    print("Dependencies:", deps)
except RuntimeError as e:
    print("Failed to extract dependencies:", e)
```

## Author

Eugene Evstafev <hi@eugene.plus>

Repository: https://github.com/chigwell/pip_dep_extractor