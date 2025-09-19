# app.py
import time
import openai
from flask import Flask, render_template, request, jsonify
from threading import Thread
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# ------------------------------
# 🔹 Flask Setup
# ------------------------------
app = Flask(__name__)

subtitles_data = []
responses_data = []
meet_code = None

# ------------------------------
# 🔹 Selenium ChromeDriver
# ------------------------------
def start_meeting(meet_code):
    global subtitles_data, responses_data
    try:
        service = Service()
        options = webdriver.ChromeOptions()
        options.add_argument("--use-fake-ui-for-media-stream")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--mute-audio")

        driver = webdriver.Chrome(service=service, options=options)
        driver.get("https://meet.google.com/")
        time.sleep(5)

        meeting_link = f"https://meet.google.com/{meet_code}"
        driver.get(meeting_link)
        time.sleep(10)

        # Run loop
        while True:
            subtitles = driver.find_elements(By.CLASS_NAME, "iOzk7")
            if subtitles:
                last_subtitle = subtitles[-1].text.strip()
                if not subtitles_data or subtitles_data[-1] != last_subtitle:
                    subtitles_data.append(last_subtitle)

                    # AI response
                    answer = ask_ai(last_subtitle)
                    responses_data.append(answer)

            time.sleep(2)

    except Exception as e:
        print("🛑 Error:", e)


# ------------------------------
# 🔹 OpenAI / OpenRouter API Setup
# ------------------------------
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


# ------------------------------
# 🔹 Flask Routes
# ------------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start", methods=["POST"])
def start():
    global meet_code
    meet_code = request.json.get("meet_code")
    thread = Thread(target=start_meeting, args=(meet_code,))
    thread.daemon = True
    thread.start()
    return jsonify({"status": "Meeting bot started!"})

@app.route("/data")
def data():
    return jsonify({
        "subtitles": subtitles_data,
        "responses": responses_data
    })


# ------------------------------
# 🔹 Run Flask App
# ------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)








