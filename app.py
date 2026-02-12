from __future__ import annotations

import streamlit as st

from agentic_builder import AgenticBuilder, EvolutionState


st.set_page_config(page_title="Agentic AI Tool Builder", layout="wide")
st.title("Agentic AI Tool Builder")
st.caption("Upload a project folder path, watch the agent plan in chat, and iteratively evolve the solution.")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "state" not in st.session_state:
    st.session_state.state = EvolutionState()
if "builder" not in st.session_state:
    st.session_state.builder = AgenticBuilder()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

folder_path = st.text_input("Folder path to analyze", value=".")

with st.expander("Agent registry"):
    st.write("The builder auto-creates missing agents during execution without asking for confirmation.")
    for agent in st.session_state.builder.describe_agent_registry():
        status = "active" if agent["active"] else "idle"
        st.markdown(f"- **{agent['name']}** ({status}): {agent['description']}")

if st.button("Analyze Folder and Draft PR"):
    builder = st.session_state.builder
    progress_lines: list[str] = []
    progress_placeholder = st.empty()

    try:
        for update in builder.run_with_updates(folder_path):
            if isinstance(update, tuple) and update[0] == "done":
                result = update[1]
                break

            progress_lines.append(f"- {update}")
            progress_placeholder.markdown(
                "### Live agent narration\n"
                "I will narrate each phase in plain language as I work.\n\n"
                + "\n".join(progress_lines)
            )
        else:
            raise RuntimeError("Analysis ended before a final result was produced.")

        response = (
            "### Live agent narration\n"
            "I narrated my steps while working.\n\n"
            + "\n".join(progress_lines)
            + "\n\n### What I looked at\n"
            + result["inspection_note"]
            + "\n\n### Agent activity log\n"
            + result["chat_log"]
            + "\n\n### Final decision\n"
            + result["decision"]
            + "\n\n### New agents created this run\n"
            + result["created_agents"]
            + "\n\n### "
            + result["title"]
            + "\n\n"
            + result["summary"]
            + "\n\n**PR Title:** `"
            + result["pr_title"]
            + "`\n\n```markdown\n"
            + result["pr_body"]
            + "\n```"
        )
    except Exception as exc:  # noqa: BLE001
        response = f"Could not analyze folder: `{exc}`"

    progress_placeholder.empty()
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

feedback = st.chat_input("Share feedback so the tool can evolve naturally")
if feedback:
    st.session_state.messages.append({"role": "user", "content": feedback})
    suggestion = st.session_state.builder.evolve(feedback, st.session_state.state)
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": (
                "Captured feedback and updated evolution log.\n\n"
                f"**Next improvement candidate:** {suggestion}"
            ),
        }
    )
    st.rerun()

with st.expander("Evolution history"):
    if st.session_state.state.history:
        for item in st.session_state.state.history:
            st.markdown(f"- {item}")
    else:
        st.write("No evolution steps yet.")
