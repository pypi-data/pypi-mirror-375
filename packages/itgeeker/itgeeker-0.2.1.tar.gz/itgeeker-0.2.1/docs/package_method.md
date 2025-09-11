pip install build
python -m build
uv build

pip install -e .
or
uv run src\itgeeker\main.py

# layout
flat layout
src layout

# setuptools
```ini
[build-system]
requires = ["setuptools>=40.8.0"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]
```

# hatchling
https://pypi.org/project/hatchling/
https://hatch.pypa.io/latest/
pip install hatchling
add __init__.py
```ini
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```


# build with Hatch
hatch build /path/to/project

# twine
https://pypi.org/project/twine/
pip install twine
twine upload dist/*

Using this token
To use this API token:
◦ Set your username to __token__
◦ Set your password to the token value, including the pypi- prefix
For example, if you are using Twine to upload your projects to PyPI, set up your $HOME/.pypirc file like this:
```ini
[pypi]
  username = __token__
  password = pypi-AgEIcHlwaS5vcmcCJGIwZjMwMmNkLWM2MDEtNDUwZS1hODA2LTY4ZWUwYWYwYWVjZAACKlszLCJmYzg2ODlkYy1lMmQxLTQxNzktYmU1Yi03MzAxNjQ0NTRhMDgiXQAABiDSPUjrGilLDdglnWmwV8-t6angme_6fkTDg8J_CMP5-Q
```
For further instructions on how to use this token, visit the PyPI help page.

https://pypi.org/project/itgeeker/0.1.0/
https://pypi.org/project/itgeeker/0.2.0/