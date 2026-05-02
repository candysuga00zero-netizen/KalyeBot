from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Palitan mo to ng sarili mong tokens
GEMINI_API_KEY = "AIzaSyBNrmxukG9okbPqEPoX08MpLWT6r9cX5R4"
VERIFY_TOKEN = "kalyeusokbot"
PAGE_ACCESS_TOKEN = "EAAbmQmT7UPwBRVZBGy40POECsi4NZAATyY8fozfaIubL6zcqH4DUDpCMZB0rUo10zNN2gGhR4vQTOOpu0bAWZADYb5ifOHwFokYRuMUhJ9ZAcEyzX64GKiKZCfLpIprQcM3je2mB9BVaBb7SCOnToI6EQiRpEZCLLygRPZCswfGpBbIyHFUgo9uZANZAYvibtB2dG2vZAYDKZC2k0AZDZD"

def ask_gemini(user_message):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [{
            "parts": [{"text": f"Ikaw ay helpful na kaibigan sa GC. Sumagot ka in Tagalog, casual, 1-2 sentences lang. Tanong: {user_message}"}]
        }]
    }

    response = requests.post(url, json=payload)
    data = response.json()

    try:
        return data['candidates'][0]['content']['parts'][0]['text']
    except:
        return "Uy nag-error ako. Try mo ulit mamaya."

def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    requests.post(url, json=payload)

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get('hub.verify_token') == VERIFY_TOKEN:
            return request.args.get('hub.challenge')
        return 'Invalid verify token'

    if request.method == 'POST':
        data = request.json
        for entry in data['entry']:
            for messaging in entry['messaging']:
                if 'message' in messaging:
                    sender_id = messaging['sender']['id']
                    user_text = messaging['message'].get('text')

                    if user_text:
                        ai_reply = ask_gemini(user_text)
                        send_message(sender_id, ai_reply)

        return 'OK', 200

if __name__ == '__main__':
    app.run(port=5000)
