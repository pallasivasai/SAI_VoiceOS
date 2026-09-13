import streamlit as st
from sai_voiceos.core import SAICommandEngine
from sai_voiceos.config import APP_NAME, VERSION

st.set_page_config(page_title=APP_NAME, page_icon="🎙️", layout="wide")
st.title("🎙️ SAI VoiceOS")
st.caption(f"Voice-first accessibility environment • Prototype v{VERSION}")

if "engine" not in st.session_state:
    st.session_state.engine = SAICommandEngine()
engine = st.session_state.engine

st.info("Prototype for a voice-first accessibility environment. Text input simulates voice commands.")

command = st.text_input("🗣️ Voice Command", placeholder="e.g. open calculator")
if st.button("▶ Execute Command", use_container_width=True):
    if command.strip():
        st.session_state.result = engine.execute(command)
    else:
        st.warning("Please enter a command.")

st.subheader("Quick Commands")
cols = st.columns(4)
for col, cmd in zip(cols, ["help", "system status", "list files", "open calculator"]):
    if col.button(cmd, use_container_width=True):
        st.session_state.result = engine.execute(cmd)

if "result" in st.session_state:
    r = st.session_state.result
    (st.success if r.success else st.error)(r.message)

st.divider()
st.subheader("Command History")
for row in reversed(engine.history()[-10:]):
    st.write(f"**{row['command']}** → {row['status']} — {row['message']}")

st.sidebar.header("MVP Modules")
for x in ["Command engine","Safe OS actions","File operations","Application launcher","SQLite history","Voice layer ready for integration"]:
    st.sidebar.write("• " + x)
