# OpenShift Log Analyzer

A focused Python tool that does three things:

1. Analyzes OpenShift logs.
2. Produces human-readable output.
3. Keeps usage simple with a clear README.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Usage

Analyze a log file and print a readable report:

```bash
openshift-log-analyzer /path/to/openshift.log
```

Optional:

```bash
openshift-log-analyzer /path/to/openshift.log --top 10
```

`--top` controls how many pods/namespaces/error lines are listed.

## What the report includes

- Log level breakdown (`INFO`, `WARN`, `ERROR`, etc.)
- Most frequent pods
- Most frequent namespaces
- Notable error/failure lines

## Run tests

```bash
pytest
```
