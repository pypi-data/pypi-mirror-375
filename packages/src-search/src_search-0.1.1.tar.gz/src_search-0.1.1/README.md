# IBM Error Search

A tkinter GUI application for searching through IBM error codes with the following features:

- Search bar with minimum 2 character requirement
- Power generation filter (9, 10, 11)
- Source/code initial filter
- Left panel showing search results (max 100)
- Right panel showing HTML content of selected error code

## Installation

### From PyPI (when published)

```bash
pip install ibm-error-search
```

### From source

```bash
git clone <repository-url>
cd src-search
poetry install
```

## Usage

After installation, run the application:

```bash
ibm-error-search
```

Or if installed via Poetry:

```bash
poetry run ibm-error-search
```

## Development

This project uses Poetry for dependency management. To set up for development:

```bash
poetry install
poetry shell
```

## Requirements

- Python 3.8+
- tkinter (usually included with Python)

## Data File

The application requires a `ds.pkl.gz` file containing the IBM error code data. This file is included in the package.
