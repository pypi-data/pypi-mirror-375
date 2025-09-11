This respository is to build any python package and push it ot PyPI repository


Procedure (Detailed):
=====================

***1. Project Structure***
--------------------

Organize your project like this:

```text
your_project/
│
├── src/your_package/          # Your actual Python code
│   ├── __init__.py
│   ├── module1.py
│   └── module2.py
│
├── tests/                     # Optional tests
│   └── test_module1.py
│
├── pyproject.toml             # Modern way to declare build system
├── setup.cfg                  # Metadata & configs
├── README.md                  # Description (shown on PyPI)
├── LICENSE                    # License (MIT, Apache2, etc.)
└── MANIFEST.in                # (optional) include non-Python files
```


***2. pyproject.toml***
-----------------

This tells pip how to build your package. Example:
```text
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "your-package-name"         # must be unique on PyPI
version = "0.1.0"
description = "A short description of your package"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
authors = [
  {name = "Your Name", email = "you@example.com"}
]
dependencies = [
  "requests>=2.0",
]

[project.urls]
Homepage = "https://github.com/yourusername/your_project"
```


***3. setup.cfg (optional, metadata in pyproject.toml is enough, but you can split)***
-----
```python
[metadata]
name = your-package-name
version = 0.1.0
author = Your Name
author_email = you@example.com
description = A short description
long_description = file: README.md
long_description_content_type = text/markdown
url = https://github.com/yourusername/your_project
license = MIT

[options]
package_dir =
    = src
packages = find:
python_requires = >=3.8

[options.packages.find]
where = src
```

***4. Build the Package***
--

First install the tools:
```python
pip install build twine
```

Then build your distribution:

```python
python -m build
```

This creates:
```python
dist/
  your_package_name-0.1.0.tar.gz
  your_package_name-0.1.0-py3-none-any.whl
```

***5. Install Locally (test before uploading)***
--
```python
pip install dist/your_package_name-0.1.0-py3-none-any.whl
```


or for development mode:
```python
pip install -e .
```


***6. Upload to PyPI***
--

```python
Create a PyPI account: https://pypi.org/account/register/

Upload with Twine:

python -m twine upload dist/*

If you want to test before real PyPI, use TestPyPI:

python -m twine upload --repository testpypi dist/*
```

✅ Now your module is pip install your-package-name ready!




Procedure (Simplified):
=======================

***🔹 1. Install Required Tools***
---

Make sure you have the build & upload tools installed:

pip install build twine


***🔹 2. Build Your Package***
---

From your project root (where pyproject.toml / setup.cfg lives):
```python
python -m build


This creates a dist/ folder with files like:

dist/
  your_package-0.1.0-py3-none-any.whl
  your_package-0.1.0.tar.gz
```

***🔹 3. Upload With Twine***
---
Upload to PyPI (public)
```python
twine upload dist/*
```

Upload to TestPyPI (sandbox)
```python
twine upload --repository testpypi dist/*
```


***🔹 4. Authentication***
---

The first time, Twine will ask for your PyPI username and password.
Best practice now is to use API tokens instead of your account password.

```text
Go to your PyPI account → Account settings → API tokens.

Create a token with scope “Entire account” (or project-specific).

Copy the token (looks like pypi-AgENdGVzdC5weXBpLm9yZw...).

Then use it when prompted:

username = __token__

password = <your-api-token>
```

***🔹 5. Store Credentials Securely (Optional)***
---

Instead of typing credentials every time, you can set them up in ~/.pypirc:

```
[pypi]
  username = __token__
  password = pypi-AgENdGVzd...

[testpypi]
  repository = https://test.pypi.org/legacy/
  username = __token__
  password = pypi-AgENdGVzd...
```

Now you can upload with:
```
twine upload -r pypi dist/*
```

or
```
twine upload -r testpypi dist/*
```

***🔹 6. Verify Upload***
---

After a successful upload:
```
PyPI: https://pypi.org/project/your-package-name/
```
```
TestPyPI: https://test.pypi.org/project/your-package-name/
```
Users can then install:
```
pip install your-package-name
```

or from TestPyPI:
```
pip install --index-url https://test.pypi.org/simple/ your-package-name
```

✅ That’s the complete flow:
build → upload with twine → authenticate → verify.