# Code Context Analyzer

> Analyze the structural context of codebases with file discovery, parsing, summarization, and CLI support.

**Code Context Analyzer** is a Python tool that inspects a codebase (local or GitHub) and provides a structured summary of its layout — including modules, classes, functions, and constants — with support for Python and JavaScript.

---

## 🔧 Features

- 📁 **Codebase discovery** with `.gitignore` respect
- 🧠 **Parsers for Python and JavaScript**
- 📋 **Clipboard export**
- 🖨️ **CLI output formatting** with depth and hierarchy controls
- 🌐 **Supports local paths or GitHub URLs**
- 🧪 **Extensible parser and formatter architecture**

---

## 🚀 Installation

```bash
pip install code-context-analyzer
```
Or clone it with 
```bash
git clone https://github.com/youruser/code-context-analyzer.git
cd code-context-analyzer
pip install .
```

## 🧪 Example Usage
```bash
cca /path/to/the/project
```
Or
```bash
cca /path/to/the/project --ignore assests/
```
Or
```bash
cca https://github.com/pallets/flask
```

## 📦 Used configurable flags
| Flag                |                  Description                  |
|:--------------------|:---------------------------------------------:|
| -h --help           |        show this help message and exit        |
| --branch            | Branch name (for GitHub repos) default "main" |
| --ignore            |      Comma-separated ignore patterns (dist/*, *min.js/, main.py)      |
| --max-files         |                 Max files to analyze             |
| --ignore-tests      |            Ignore all tests that start with 'tests' (true/false)           |
| --no-clipboard      |            Do not copy to clipboard           |

## 🧩 Architecture Overview
```plaintext
code_context_analyzer/
├── /
│   ├── main.py
│   └── __init__.py
├── analyzer/
│   ├── clipboard.py
│   ├── discovery.py
│   └── __init__.py
├── analyzer\parsers/
│   ├── base.py
│   ├── js_parser.py
│   ├── python_parser.py
│   └── __init__.py
├── cli/
│   └── __init__.py
├── dto/
│   ├── models.py
│   └── __init__.py
├── formatters/
│   ├── base.py
│   ├── default.py
│   ├── factory.py
│   ├── html_formatter.py
│   ├── json_formatter.py
│   ├── yaml_formatter.py
│   └── __init__.py
├── repo_system/
│   ├── handler.py
│   ├── session.py
│   └── __init__.py
└── utils/
    ├── dto_converter.py
    ├── temp_dir.py
    └── __init__.py
```

## 🛠️ Development
Install dev dependencies:
```bash
pip install -r requirements.txt
```
Run tests:
```bash
pytest
```

## 📚 Documentation
Generated using MkDocs
Run locally:
```bash
pip install mkdocs
mkdocs serve
```
Or visit here for docs:

- [https://ahasanular.github.io/code-context-analyzer/](https://ahasanular.github.io/code-context-analyzer/)


## 🪪 License
MIT License © **Md. Ahasanul Arafath**
