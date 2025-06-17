# Python Project Requirements Generation & Dependency Management

Automate your `requirements.txt` generation for Python data lake, AWS Glue, or general scripting projects. This solution is robust against SSL/certificate errors and Windows Unicode issues—ideal for enterprise and cloud environments.

---

## 🚀 Features

- Scans all Python scripts (excluding venvs, hidden/system folders)
- Uses [pipreqs](https://github.com/bndr/pipreqs) for requirements generation (with `--use-local` for SSL-resilience: Use ONLY local package info instead of querying PyPI)
- Handles encoding for cross-platform compatibility
- Consolidates requirements from subfolders
- One-click install for all dependencies

---

## 🛠 Prerequisites

- **Python 3.7+** (Windows, Mac, or Linux)
- **pip** installed
- **pipreqs** package (install with: `pip install pipreqs`)
- (Recommended) Use a virtual environment:
  ```sh
  python -m venv venv
  # On Linux/Mac:
  source venv/bin/activate
  # On Windows:
  venv\Scripts\activate
