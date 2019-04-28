# py2ds2

Python package to create a SAS DS2 scoring package.

## Installation

1. Clone this repo
2. `cd py2ds2`
3. `pip install py2ds2`

## Usage

```py
import py2ds2
py2ds2.create_package(path-to-python-scoring-file,
                      path-to-ds2-scoring-file,
                      path-to-inputVars-file,
                      path-to-outputVars-file)
```

`create_package` will write a SAS DS2 scoring package file the location you provide. The `inputVars` and `outputVars` files must match SAS Model Manager syntax:

```json
[
	{
		'name': 'varname',
		'type': 'decimal' or 'character',
		'role': 'input' or 'output'
	}
]
```
