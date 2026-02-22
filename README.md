# OpenShift Log Analyzer

A focused Python tool that does three things:

1. Analyzes OpenShift logs.
2. Produces human-readable output.
3. Optionally asks a local Ollama model to act as an SRE agent over your logs.

## Agent architecture guarantees

The Ollama-backed agent now uses a workflow engine and guardrails designed for operations teams:

- **State machine / workflow engine**: explicit steps `CollectContext → Diagnose → Recommend → ExecuteFix → Verify`.
- **Typed tool interfaces**: JSON-schema-backed request/response schemas with runtime validation for tool invocations.
- **Observability**: per-step traces, latency metrics, and failure counters are emitted with every run.
- **Policy layer**: tool permission checks are enforced by tenant/namespace scope.
- **Test harness**: incident replay support validates agent behavior against past incident summaries.
- **Human-in-the-loop gates**: choose between propose-only and apply modes.

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

## Use a local Ollama model as an OpenShift log agent

You can have Ollama generate an operator-style action plan based on the analyzer output.

1. Start Ollama locally.

   ```bash
   ollama serve
   ```

2. Pull a local model (example: `llama3.2`).

   ```bash
   ollama pull llama3.2
   ```

3. Run the analyzer with the Ollama agent enabled.

   ```bash
   openshift-log-analyzer /path/to/openshift.log --ollama-agent --ollama-model llama3.2
   ```

By default, the tool sends the report to `http://127.0.0.1:11434/api/generate`.

If Ollama is running elsewhere, set a custom URL:

```bash
openshift-log-analyzer /path/to/openshift.log --ollama-agent --ollama-url http://192.168.1.20:11434
```

### Human approval gates

- **Propose only (default):**

  ```bash
  openshift-log-analyzer /path/to/openshift.log --ollama-agent --agent-mode propose_changes
  ```

- **Apply mode:**

  ```bash
  openshift-log-analyzer /path/to/openshift.log --ollama-agent --agent-mode apply_changes
  ```

You can pass policy context for multi-tenant OpenShift checks:

```bash
openshift-log-analyzer /path/to/openshift.log --ollama-agent --tenant acme --namespace prod
```

## What the report includes

- Log level breakdown (`INFO`, `WARN`, `ERROR`, etc.)
- Most frequent pods
- Most frequent namespaces
- Notable error/failure lines
- Agent traces and failure counts when `--ollama-agent` is enabled

## Run tests

```bash
pytest
```
