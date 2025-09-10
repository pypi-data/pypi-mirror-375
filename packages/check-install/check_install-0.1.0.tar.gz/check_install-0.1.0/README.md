# check-install (`check_install`)

[![PyPI version](https://img.shields.io/pypi/v/check-install.svg?color=brightgreen)](https://pypi.org/project/check-install/)
[![Python versions](https://img.shields.io/pypi/pyversions/check-install.svg)](https://pypi.org/project/check-install/)
[![License](https://img.shields.io/pypi/l/check-install.svg)](LICENSE)
[![Downloads](https://static.pepy.tech/badge/check-install)](https://pepy.tech/project/check-install)

Automatically detect and install missing Python modules at runtime or pre-execution using pip.

## 📥 Installation

```bash
pip install check-install
```

---

## 💡 What It Does

When imported and invoked early in your Python scripts, `check_install` scans for missing imports:

* Prompts to install them using `pip`.
* Restarts the script seamlessly after installation.
* Works both during import time and runtime (`ModuleNotFoundError`).
* Optionally displays nice output with `rich`, but works without it.
* Great for prototyping, scratch scripts, or educational notebooks.

---

## ✅ Quick Start

Add this to the very top of your script:

```python
import check_install
check_install.install_hooks_and_preflight()
```

That’s it! If any module is missing, you’ll be prompted to install it.

---

## 📦 Example

Say your script contains:

```python
import check_install
check_install.install_hooks_and_preflight()
import numpy
import yaml
```

And you don't have `numpy` or `PyYAML` installed — you’ll see an interactive prompt:

```plaintext
Missing Dependencies Detected
Import name     PyPI package
──────────────  ─────────────
numpy           numpy
yaml            PyYAML

Attempt to auto-install missing 2 package(s) now? [Y/n]:
```

It will install and re-execute the script.

---

## 🧠 How It Works

* Uses `ast` to statically analyze the current script and extract imports.
* Catches `ModuleNotFoundError` at runtime using a custom `sys.excepthook`.
* Attempts installation via `subprocess.run([python -m pip install ...])`.
* Tracks attempted installations to avoid loops.

---

## ⚠️ Notes

* Meant for **dev/test scripts** — not production!
* Respects existing venvs, shows interpreter context.
* Maps known import names to their PyPI equivalents (`PIL` → `pillow`, etc).
* Requires no external config, arguments, or setup.

---

## 🔒 Security & Safety

* Does **not** use `eval`, `exec`, or shell calls.
* Uses `subprocess` securely to invoke `pip`.
* Gracefully exits or restarts using `os.execv`.

---

## 🚫 Limitations

* Won’t resolve C/C++ build errors or OS-level dependencies.
* Assumes `pip` is functional and available in the current Python environment.

---

## 🧪 Want Tests?

Let me know and I’ll whip up a test suite for you! 🧪

---

## 📜 License

MIT License — see the [LICENSE](LICENSE) file for full text.

