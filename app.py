import streamlit as st

# ============================================================
# SAI VOICE OS — INTERFACE ONLY
# ============================================================

st.set_page_config(
    page_title="SAI Voice OS",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

* {
    box-sizing: border-box;
}

#MainMenu {
    visibility: hidden;
}

header {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

.stApp {
    background:
        radial-gradient(
            circle at 50% 20%,
            rgba(99,102,241,0.12),
            transparent 35%
        ),
        linear-gradient(
            135deg,
            #f8fafc 0%,
            #eef2ff 50%,
            #f8fafc 100%
        );
    min-height: 100vh;
}

/* Main container */

.block-container {
    max-width: 1150px;
    padding-top: 35px;
    padding-bottom: 30px;
}

/* Header */

.sai-header {
    text-align: center;
    margin-top: 15px;
    margin-bottom: 25px;
}

.sai-logo {
    font-size: 72px;
    margin-bottom: 5px;
}

.sai-title {
    font-size: 48px;
    font-weight: 800;
    letter-spacing: -2px;
    color: #171923;
}

.sai-subtitle {
    color: #667085;
    font-size: 18px;
    margin-top: 5px;
}

/* Status */

.status-wrapper {
    display: flex;
    justify-content: center;
    margin: 25px 0;
}

.status {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 10px 20px;
    border-radius: 50px;
    background: rgba(255,255,255,0.8);
    border: 1px solid #e5e7eb;
    box-shadow: 0 5px 20px rgba(0,0,0,0.05);
    font-size: 15px;
    color: #344054;
}

.status-dot {
    width: 10px;
    height: 10px;
    background: #22c55e;
    border-radius: 50%;
    box-shadow: 0 0 12px rgba(34,197,94,0.7);
}

/* Voice circle */

.voice-area {
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 35px 0 30px 0;
}

.voice-ring {
    width: 210px;
    height: 210px;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;

    background:
        radial-gradient(
            circle,
            #ffffff 42%,
            #eef2ff 43%,
            #e0e7ff 58%,
            transparent 59%
        );

    box-shadow:
        0 0 0 18px rgba(99,102,241,0.04),
        0 0 0 36px rgba(99,102,241,0.025),
        0 25px 60px rgba(79,70,229,0.16);
}

.voice-mic {
    font-size: 72px;
}

/* Listening text */

.listening {
    text-align: center;
    font-size: 22px;
    font-weight: 650;
    color: #252936;
    margin-top: 10px;
}

.listening-small {
    text-align: center;
    font-size: 15px;
    color: #667085;
    margin-top: 8px;
}

/* Cards */

.card-row {
    display: flex;
    gap: 18px;
    margin-top: 45px;
}

.card {
    flex: 1;
    background: rgba(255,255,255,0.72);
    border: 1px solid rgba(226,232,240,0.9);
    border-radius: 20px;
    padding: 23px;
    box-shadow: 0 10px 30px rgba(15,23,42,0.05);
}

.card-icon {
    font-size: 28px;
    margin-bottom: 12px;
}

.card-title {
    font-size: 17px;
    font-weight: 700;
    color: #252936;
}

.card-text {
    color: #667085;
    font-size: 14px;
    margin-top: 6px;
    line-height: 1.5;
}

/* Bottom */

.footer-text {
    text-align: center;
    margin-top: 45px;
    color: #98a2b3;
    font-size: 13px;
}

/* Mobile */

@media (max-width: 700px) {

    .sai-title {
        font-size: 38px;
    }

    .sai-logo {
        font-size: 58px;
    }

    .voice-ring {
        width: 175px;
        height: 175px;
    }

    .voice-mic {
        font-size: 60px;
    }

    .card-row {
        flex-direction: column;
    }
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="sai-header">

    <div class="sai-logo">🎙️</div>

    <div class="sai-title">
        SAI Voice OS
    </div>

    <div class="sai-subtitle">
        Voice-first accessibility operating system
    </div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# STATUS
# ============================================================

st.markdown("""
<div class="status-wrapper">

    <div class="status">

        <span class="status-dot"></span>

        SAI Voice System Ready

    </div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# VOICE CENTER
# ============================================================

st.markdown("""
<div class="voice-area">

    <div class="voice-ring">

        <div class="voice-mic">
            🎙️
        </div>

    </div>

</div>

<div class="listening">
    Ready to Listen
</div>

<div class="listening-small">
    Your voice is the interface
</div>
""", unsafe_allow_html=True)


# ============================================================
# FEATURE CARDS
# ============================================================

st.markdown("""
<div class="card-row">

    <div class="card">

        <div class="card-icon">🖥️</div>

        <div class="card-title">
            Computer Control
        </div>

        <div class="card-text">
            Control applications and
            computer functions using voice.
        </div>

    </div>


    <div class="card">

        <div class="card-icon">🌐</div>

        <div class="card-title">
            Internet Access
        </div>

        <div class="card-text">
            Search the web, access information
            and interact with online services.
        </div>

    </div>


    <div class="card">

        <div class="card-icon">📄</div>

        <div class="card-title">
            Document Access
        </div>

        <div class="card-text">
            Access and understand documents
            through voice interaction.
        </div>

    </div>


    <div class="card">

        <div class="card-icon">♿</div>

        <div class="card-title">
            Accessibility
        </div>

        <div class="card-text">
            Designed around a voice-first
            computing experience.
        </div>

    </div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div class="footer-text">
    SAI Voice OS • Accessible Computing through Voice
</div>
""", unsafe_allow_html=True)
