def kalyebot(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"

    system_prompt = """Ikaw si KalyeBot, pinaka-maangas sa GC. Roast king ka. Lahat ng reply mo may kasamang pang-aasar pero tropa vibes pa rin. 1 sentence lang lagi. Walang filter."""

    full_prompt = f"{system_prompt}\n\nTropa: {prompt}\nKalyebot:"

    payload = {
        "contents": [{
            "parts": [{"text": full_prompt}]
        }],
        "generationConfig": {
            "temperature": 0.9,
            "maxOutputTokens": 60
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Gemini Status: {response.status_code}") # Para makita sa logs
        print(f"Gemini Response: {response.text}") # Para makita exact error

        response.raise_for_status()
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print(f"Gemini Error: {e}")
        return "Nag-error ako tol, try mo ulit mamaya"
