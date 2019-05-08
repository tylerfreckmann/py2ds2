# py2ds2

Python package to create a SAS DS2 scoring package from a pickled scikit-learn pipeline.

## Installation

1. Clone this repo
2. `cd py2ds2`
3. `pip install py2ds2`

## Usage

```py
import py2ds2
py2ds2.create_from_pickle(pickle_filename, X, model_function='CLASSIFICATION')
```

Creates a SAS DS2 scoring package from a Python pickle file.

The pickle file should be a sci-kit learn pipeline that was fit on the pandas DataFrame `X`.
A python scoring file, a SAS DS2 scoring file that wraps the python scoring file,
and input/output variable info files are all created from the pickled scikit-learn pipeline.

See the examples directory to see an example of a jupyter notebook that builds a sci-kit learn
ML pipeline, pickles it, then uses py2ds2 to create the necessary SAS scoring files in pymodels/hmeq2
