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
    api_key="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",  # 🔑 Your key
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
# Selenium Setup
# -------------------------------
def start_meeting(meet_code):
    try:
        service = Service()  # requires chromedriver installed
        options = webdriver.ChromeOptions()
        options.add_argument("--use-fake-ui-for-media-stream")  # auto allow mic/cam
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--mute-audio")

        driver = webdriver.Chrome(service=service, options=options)

        # Open Google Meet login
        driver.get("https://meet.google.com/")
        status_bar.info("Please log in manually in the browser window...")
        time.sleep(10)  # give time for login

        # Join meeting
        meeting_link = f"https://meet.google.com/{meet_code}"
        driver.get(meeting_link)
        time.sleep(15)  # wait for meeting to load
        status_bar.success("✅ Google Meet opened and joined!")

        # Loop: grab subtitles + send to AI
        last_seen = ""
        while True:
            subtitles = driver.find_elements(By.CLASS_NAME, "iOzk7")
            if subtitles:
                latest = subtitles[-1].text.strip()
                if latest != last_seen:  # only process new lines
                    last_seen = latest
                    subtitles_box.write(f"**📝 Subtitles:**\n{latest}")

                    # Send to AI
                    answer = ask_ai(latest)
                    response_box.write(f"**🤖 AI Response:**\n{answer}")

            time.sleep(2)

    except Exception as e:
        status_bar.error(f"🛑 Error: {e}")

# -------------------------------
# Start Button
# -------------------------------
if st.button("🚀 Start Assistant") and meet_code:
    Thread(target=start_meeting, args=(meet_code,), daemon=True).start()

















