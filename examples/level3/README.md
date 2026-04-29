# Level 3: Tool Use

## Scenario this level demonstrates

Tool-augmented accuracy for arithmetic tasks where deterministic calculation is required.

## Tangible things this example can handle

- Solving exact numeric expressions (for example, multiplication).
- Returning numeric results derived from tool output.

## How to trigger this example

1. Start the app:
   
   ```bash
   export OPENAI_API_KEY="your_key_here"
   python app.py
   ```
2. Open <http://127.0.0.1:8000>.
3. Click **Level 3**.
4. Review the trace output shown in the dashboard.

## AI behavior demonstrated

This level runs a live LLM-backed workflow from `app.py` and prints the execution trace in the dashboard.
