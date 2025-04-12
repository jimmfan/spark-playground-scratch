# Python Project Structures & Build Systems

_From `setup.py` to `pyproject.toml` — what every data scientist should know_

---

## Why This Matters
- 🧑‍🤝‍🧑 Collaboration: shared, consistent project structure
- 📦 Reusability: install and import your code like any library
- 🤖 Automation: enables testing, packaging, CI/CD
- 🧪 Environments: avoid "works on my machine" issues

---

## Anatomy of a Legacy Project
```
my_project/

├── Makefile
├── src/
│   └── my_package/
│       └── __init__.py
├── README.rst
├── setup.cfg
├── setup.py
```

- `setup.py`: install logic
- `setup.cfg`: declarative metadata
- `Makefile`: glue commands (e.g., `make install`, `make test`)

---

## Teaching Strategy: “Explain Like I’m New to Python Builds”
Think of the `setup.cfg` file as the **"blueprint" or recipe** that tells Python how to package, install, and run your project. It’s kind of like filling out the metadata and settings for a software product.

---

## [metadata] — Who and what is this package?
```ini
[metadata]
name = my_package
description = Project description
url = "https://example.url.com"
long_description = file: README.rst, CHANGELOG.rst, LICENSE.rst
maintainer = Bob
maintainer_email = bob@example_email.com
```
**Explanation:**
- If your project were a book, this section is the cover page.
- It gives your project a name, who wrote it, and some additional documentation.
- The `long_description` tells tools like PyPI what to show on the project page.


---

## [options] — How do we install and use this package?
```ini
[options]
package_dir=
    =src
include_package_data = True    
packages=find:
install_requires =
    requests
    pandas;
```
**Explanation:**
- This tells Python **where your code lives** (`src/`) and how to find your package.
- `install_requires` lists the libraries your code needs to run. Like `requirements.txt` but for installers.
- `packages=find:` automatically finds your subfolders that contain `__init__.py`.

**Explanation:**
> “Instead of manually listing every folder with code, we say ‘please find all packages under the `src/` directory’.”

---

## [options.packages.find] — Narrow the search
```ini
[options.packages.find]
where=src
```
**Explanation:**
- “Only look in `src/` to find the code packages.”

---

## [options.package_data] — Extra files to include
```ini
[options.package_data]
* = *.yaml,*.yml,*.sh,*.json
```
**Explanation:**
- You sometimes have config files, scripts, etc., that are **not Python**, but still part of the project.
- This tells the installer: “Please also include `.yaml`, `.sh`, etc.”

---

## [options.extras_require] — Optional dependency bundles
```ini
[options.extras_require]
dev = black; mypy==0.812
test = tox; mypy==0.812
docs = Sphinx
```
**Explanation:**
- These are optional “add-on kits.”
- Want to develop or test the project? Install with:
```bash
pip install .[dev]
pip install .[test]
```
- This keeps the base install lightweight, but still lets devs get full tooling when needed.

---

## Modern Python: pyproject.toml
- Introduced in **PEP 518**, standardized by **PEP 621**
- Replaces `setup.py` and `setup.cfg`
- One file for everything: metadata, dependencies, build system

```toml
[project]
name = "my_package"
dependencies = ["requests", "pandas"]

[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"
```

---

## What is a Build System?
🧱 A build system converts your source code into something installable.

- `python3 setup.py install` → legacy
- `pip3 install .` → modern
- `pyproject.toml` → future-ready

**Tools**: setuptools, poetry, hatch, pdm

---

## CI/CD — What’s the Point?
🤖 CI/CD = Continuous Integration / Continuous Deployment

- Run tests automatically on push/PR
- Package your project for PyPI or Docker
- GitHub Actions example:
```yaml
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -e .[dev]
      - run: pytest
```

---

## Summary — What You Should Remember
| Concept               | What It Does                        |
|----------------------|--------------------------------------|
| `setup.cfg`          | Project metadata + install settings |
| `src/` layout        | Clean code separation               |
| `entry_points`       | Run Python code as CLI tools        |
| `pyproject.toml`     | The future of Python packaging      |
| Extras like `[dev]`  | Isolate tools for different tasks   |
| CI/CD                | Automate testing + deployment       |

---
