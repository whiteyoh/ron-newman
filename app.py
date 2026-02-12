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

if st.button("Analyze Folder and Draft PR"):
    builder = st.session_state.builder
    try:
        result = builder.run(folder_path)
        response = (
            f"### {result['title']}\n\n"
            f"{result['summary']}\n\n"
            f"**PR Title:** `{result['pr_title']}`\n\n"
            f"```markdown\n{result['pr_body']}\n```"
        )
    except Exception as exc:  # noqa: BLE001
        response = f"Could not analyze folder: `{exc}`"

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
