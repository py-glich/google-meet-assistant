import streamlit as st
import time

# Try importing OpenAI
try:
    import openai
except Exception:
    st.error("❌ Missing `openai` package. Make sure it's in requirements.txt")
    raise

# ----------------------------
# OpenAI / OpenRouter setup
# ----------------------------
# Load API key & base URL from Streamlit Secrets
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY")
OPENAI_BASE_URL = st.secrets.get("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")

if not OPENAI_API_KEY:
    st.warning("⚠️ OPENAI_API_KEY is not set. Add it in Streamlit Cloud Secrets to enable AI calls.")

# Create client only if API key is set
client = None
if OPENAI_API_KEY:
    client = openai.OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)

# ----------------------------
# Helper function
# ----------------------------
def ask_ai(question: str) -> str:
    """Send a question to OpenAI / OpenRouter and return the response"""
    if not client:
        return "🔒 API key not set (add OPENAI_API_KEY in Secrets)."
    try:
        resp = client.chat.completions.create(
            model="google/gemini-2.0-flash-lite-001",
            messages=[{"role": "user", "content": question}]
        )
        if resp and hasattr(resp, "choices") and resp.choices:
            return resp.choices[0].message.content.strip()
        return "⚠️ No valid response from AI"
    except Exception as e:
        return f"🚨 API Error: {e}"

# ----------------------------
# Streamlit UI
# ----------------------------
st.set_page_config(page_title="Google Meet Assistant", layout="centered")
st.title("🎙 Google Meet Assistant (Streamlit Demo)")

# Session state
if "subs" not in st.session_state:
    st.session_state.subs = []
if "resps" not in st.session_state:
    st.session_state.resps = []

st.markdown("**Manual mode:** Paste or type a subtitle/question and press *Send to AI*.")

col1, col2 = st.columns([3, 1])
with col1:
    subtitle = st.text_area("Subtitle / Question", placeholder="Paste a Meet subtitle here", height=120)
with col2:
    if st.button("Send to AI"):
        text = subtitle.strip()
        if not text:
            st.warning("⚠️ Type or paste a subtitle first.")
        else:
            st.session_state.subs.append(text)
            with st.spinner("🤔 Asking AI..."):
                ans = ask_ai(text)
            st.session_state.resps.append(ans)
            st.success("✅ Response added to history")

# Demo button
st.markdown("---")
st.markdown("**Quick demo:** Add a sample subtitle (no Meet needed).")
if st.button("Add sample subtitle"):
    demo_text = f"Sample subtitle at {time.strftime('%H:%M:%S')}"
    st.session_state.subs.append(demo_text)
    st.session_state.resps.append(ask_ai(demo_text))

# History
st.markdown("### 📜 History (latest first)")
for s, r in zip(reversed(st.session_state.subs), reversed(st.session_state.resps)):
    st.markdown(f"**Subtitle:** {s}")
    st.markdown(f"**AI:** {r}")
    st.markdown("---")

st.caption("ℹ️ Note: Selenium live capture won’t run on Streamlit Cloud. Use manual input or demo mode.")













