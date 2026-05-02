import os
import requests
from flask import Flask, request

app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
PAGE_ID = "1132180923304623" # Page ID mo nilagay ko na

def kalyebot(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    system_prompt = """Ikaw si KalyeBot, pinaka-maangas sa GC. Roast king ka. Lahat ng reply mo may kasamang pang-aasar pero tropa vibes pa rin. 1 sentence lang lagi. Walang filter."""

    full_prompt = f"{system_prompt}\n\nTropa: {prompt}\nKalyebot:"

    payload = {
        "contents": [{
            "parts": [{"text": full_prompt}]
        }]
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print(f"Gemini Error: {e}")
        return "Nag-error ako tol, try mo ulit mamaya"

def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    r = requests.post(url, json=payload)
    print(f"Send to {recipient_id} status: {r.status_code}, {r.text}")

@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get('hub.verify_token') == VERIFY_TOKEN:
        return request.args.get('hub.challenge')
    return 'Invalid verify token'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if data.get('object') == 'page':
        for entry in data.get('entry', []):
            for messaging_event in entry.get('messaging', []):

                # Skip echo messages galing sa bot mismo
                if messaging_event.get('message', {}).get('is_echo'):
                    continue

                sender_id = messaging_event.get('sender', {}).get('id')
                message = messaging_event.get('message', {})
                user_text = message.get('text')

                if not sender_id or not user_text:
                    continue

                # Check kung mentioned si KalyeBot
                is_mentioned = False
                mentions = message.get('mentions', [])

                # Method 1: Check mentions array - pinaka-accurate sa GC
                for mention in mentions:
                    if mention.get('id') == PAGE_ID:
                        is_mentioned = True
                        break

                # Method 2: Fallback check sa text
                text_lower = user_text.lower()
                if not is_mentioned and ('@kalyebot' in text_lower or 'kalyebot' in text_lower):
                    is_mentioned = True

                if is_mentioned:
                    # Tanggalin @KalyeBot sa message
                    clean_text = user_text
                    clean_text = clean_text.replace('@KalyeBot', '').replace('@kalyebot', '').replace('KalyeBot', '').replace('kalyebot', '').strip()

                    if not clean_text:
                        clean_text = "uy"

                    print(f"GC Message from {sender_id}: {clean_text}")
                    bot_reply = kalyebot(clean_text)
                    send_message(sender_id, bot_reply)

    return 'ok', 200

@app.route('/privacy')
def privacy():
    return """
    <h1>Privacy Policy for KalyeBot</h1>
    <p>Kalyebot is a Messenger chatbot for entertainment.</p>
    <p><b>Data:</b> We only process messages with @mention. No data stored.</p>
    <p><b>Third Party:</b> Uses Google Gemini API for AI responses.</p>
    <p><b>Contact:</b> your-email@gmail.com</p>
    <p>Last updated: May 2, 2026</p>
    """

@app.route('/')
def home():
    return 'Kalyebot is alive!'
