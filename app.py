import os
import requests
from flask import Flask, request

app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def kalyebot(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"

    system_prompt = """Ikaw si Kalyebot, pinaka-maangas sa GC. Roast king ka.
    Lahat ng reply mo may kasamang pang-aasar pero tropa vibes pa rin.
    1 sentence lang lagi. Walang filter."""

    full_prompt = f"{system_prompt}\n\nTropa: {prompt}\nKalyebot:"

    payload = {
        "contents": [{
            "parts": [{"text": full_prompt}]
        }]
    }

    try:
        response = requests.post(url, json=payload)
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    except:
        return "Nag-error ako tol, try mo ulit mamaya"

def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    requests.post(url, json=payload)

@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get('hub.verify_token') == VERIFY_TOKEN:
        return request.args.get('hub.challenge')
    return 'Invalid verify token'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if data['object'] == 'page':
        for entry in data['entry']:
            for messaging_event in entry['messaging']:
                if messaging_event.get('message'):
                    sender_id = messaging_event['sender']['id']
                    user_text = messaging_event['message'].get('text')

                    if user_text:
                        if '@bot' in user_text.lower():
                            clean_text = user_text.lower().replace('@bot', '').strip()
                            bot_reply = kalyebot(clean_text)
                            send_message(sender_id, bot_reply)

    return 'ok', 200

@app.route('/privacy')
def privacy():
    return """
    <h1>Privacy Policy for Kalyebot</h1>
    <p>Kalyebot is a Messenger chatbot for entertainment.</p>
    <p><b>Data:</b> We only process messages with @bot. No data stored.</p>
    <p><b>Third Party:</b> Uses Google Gemini API for AI responses.</p>
    <p><b>Contact:</b> your-email@gmail.com</p>
    <p>Last updated: May 2, 2026</p>
    """

@app.route('/')
def home():
    return 'Kalyebot is alive!'
