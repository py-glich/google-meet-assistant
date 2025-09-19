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
    api_key="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",  # Replace with your key
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
        service = Service()
        options = webdriver.ChromeOptions()
        options.add_argument("--use-fake-ui-for-media-stream")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--mute-audio")
        driver = webdriver.Chrome(service=service, options=options)

        driver.get("https://meet.google.com/")
        status_bar.info("Please log in manually in the browser...")
        time.sleep(5)

        meeting_link = f"https://meet.google.com/{meet_code}"
        driver.get(meeting_link)
        time.sleep(10)
        status_bar.success("✅ Google Meet opened successfully!")

        # Background loop for subtitles
        while True:
            subtitles = driver.find_elements(By.CLASS_NAME, "iOzk7")
            if subtitles:
                last_subtitle = subtitles[-1].text.strip()
                subtitles_box.write("**📝 Subtitles:**\n" + last_subtitle)

                # Get AI response
                answer = ask_ai(last_subtitle)
                response_box.write("**🤖 AI Response:**\n" + answer)

            time.sleep(2)

    except Exception as e:
        status_bar.error(f"🛑 Error: {e}")

# -------------------------------
# Start Button
# -------------------------------
if st.button("🚀 Start Assistant") and meet_code:
    Thread(target=start_meeting, args=(meet_code,), daemon=True).start()















