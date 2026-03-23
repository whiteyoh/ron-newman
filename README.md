# OpenShift 4.16 Must-Gather Incident Analyzer

A Python tool that rewrites this repository around a new use case: **analyzing an OpenShift 4.16 must-gather bundle for a specific incident date and producing a clear root-cause-analysis report**.

## What it does

- Accepts a must-gather **directory** or compressed **tar/tgz archive**.
- Unpacks the archive automatically when needed.
- Filters log and text evidence to a **specific date**.
- Produces:
  - a concise **terminal summary**, and
  - a standalone **HTML report** designed to be easy for humans to read.
- Highlights:
  - likely root-cause candidates,
  - hotspot namespaces, nodes, and pods,
  - timeline evidence for the requested day,
  - recommended next investigation steps.

## Supported use case

This project is now aimed at incident review workflows such as:

> “Analyze this OpenShift 4.16 must-gather for 2026-03-15 and tell me the most likely root cause of the cluster incident.”

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Usage

### Terminal-only report

```bash
openshift-must-gather-analyzer ./must-gather.tar.gz --incident-date 2026-03-15
```

### Terminal + HTML report

```bash
openshift-must-gather-analyzer ./must-gather.tgz \
  --incident-date 2026-03-15 \
  --html-output report.html
```

## Output overview

The text report includes:

- executive summary of likely root causes,
- severity breakdown,
- busiest namespaces and nodes,
- dated timeline highlights,
- recommended next steps.

The HTML report includes:

- an executive summary section,
- evidence-backed root-cause cards,
- hotspot panels for namespaces, nodes, and pods,
- an evidence timeline table.

## Development

Run tests with:

```bash
pytest
```
