import streamlit as st
import time
import openai
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from threading import Thread

# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="Google Meet Assistant", layout="wide")

st.title("🌌 Google Meet Assistant")
meet_code = st.text_input("Enter Google Meet Code (e.g., txe-ditf-qgs):")

# Panels
subtitles_box = st.empty()
response_box = st.empty()
status_bar = st.empty()

# -------------------------------
# OpenAI Setup (OpenRouter)
# -------------------------------
client = openai.OpenAI(
    api_key="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",  # 🔑 your key
    base_url="https://openrouter.ai/api/v1"
)

def ask_ai(question):
    try:
        response = client.chat.completions.create(
            model="google/gemini-2.0-flash-lite-001",
            messages=[{"role": "user", "content": question}]
        )
        if response and hasattr(response, 'choices') and response.choices:
            return response.choices[0].message.content.strip()
        return "⚠ No valid response from AI"
    except Exception as e:
        return f"🚨 API Error: {str(e)}"

# -------------------------------
# Meeting Bot
# -------------------------------
def start_meeting(meet_code):
    try:
        service = Service()  # make sure chromedriver is installed
        options = webdriver.ChromeOptions()
        options.add_argument("--use-fake-ui-for-media-stream")  # allow mic/cam automatically
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--mute-audio")

        driver = webdriver.Chrome(service=service, options=options)

        # Open Google Meet directly
        meeting_link = f"https://meet.google.com/{meet_code}"
        driver.get(meeting_link)

        status_bar.info("🌐 Opening Google Meet... Please log in and press 'Join now' manually if required.")
        time.sleep(15)  # wait for login & meeting to load

        status_bar.success("✅ Google Meet opened!")

        last_seen = ""
        while True:
            subtitles = driver.find_elements(By.CLASS_NAME, "iOzk7")
            if subtitles:
                latest = subtitles[-1].text.strip()
                if latest != last_seen:
                    last_seen = latest
                    subtitles_box.write(f"**📝 Subtitles:**\n{latest}")

                    # Send to AI
                    answer = ask_ai(latest)
                    response_box.write(f"**🤖 AI Response:**\n{answer}")

            time.sleep(2)

    except Exception as e:
        status_bar.error(f"🛑 Error: {e}")

# -------------------------------
# Button: Join Meeting
# -------------------------------
if st.button("🚀 Join Meeting") and meet_code:
    Thread(target=start_meeting, args=(meet_code,), daemon=True).start()



















