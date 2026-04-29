# Level 1: Autocomplete

## Scenario this level demonstrates

Quick next-text completion from a short phrase when you only need likely continuation.

## Tangible things this example can handle

- Completing sentence stems for writing assistance.
- Suggesting likely phrase endings in chat or notes.

## How to trigger this example

1. Start the app:
   
   ```bash
   export OPENAI_API_KEY="your_key_here"
   python app.py
   ```
2. Open <http://127.0.0.1:8000>.
3. Click **Level 1**.
4. Review the trace output shown in the dashboard.

## AI behavior demonstrated

This level runs a live LLM-backed workflow from `app.py` and prints the execution trace in the dashboard.
