[![PyPI version](https://badge.fury.io/py/llm_dep_extractor.svg)](https://badge.fury.io/py/llm_dep_extractor)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/badge/llm_dep_extractor)](https://pepy.tech/project/llm_dep_extractor)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue)](https://www.linkedin.com/in/eugene-evstafev-716669181/)

# llm_dep_extractor

`llm_dep_extractor` is a Python package designed for extracting required pip package names from Python code snippets using LLMs and llmatch.

## Installation

To install `llm_dep_extractor`, use pip:

```bash
pip install llm_dep_extractor
```

## Usage

Here's a simple example demonstrating how to use the package:

```python
from llm_dep_extractor import extract_required_pip_packages
from langchain_llm7 import ChatLLM7
# Initialize your LLM model
llm = ChatLLM7()

code_sample = '''
import numpy as np
import pandas as pd
# some code here
'''

# Extract package names
packages = extract_required_pip_packages(code_sample, llm)
print(packages)
```

## Features

- Extracts up to 10 package names from Python code snippets
- Uses LLMs with a defined prompt pattern
- Ensures unique, properly formatted package names

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/chigwell/llm_dep_extractor/issues).

## License

`llm_dep_extractor` is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).

## Author

Eugene Evstafev &lt;hi@eugene.plus&gt;