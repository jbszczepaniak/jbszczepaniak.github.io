import os
import requests
from datetime import datetime

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def get_updates():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    response = requests.get(url).json()
    messages = []
    
    if "result" in response:
        for update in response["result"]:
            if "message" in update and str(update["message"]["chat"]["id"]) == str(CHAT_ID):
                text = update["message"].get("text")
                if text and not text.startswith("/"):
                    messages.append(text)
    return messages

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, json=payload)

def save_to_markdown(messages):
    if not messages:
        return False
        
    now = datetime.now()
    year_month = now.strftime("%Y-%m") # np. "2026-10"
    day = now.strftime("%Y-%m-%d %H:%M")
    
    os.makedirs("til", exist_ok=True)
    filename = f"til/{year_month}.md"
    
    # Dopisujemy na górę pliku danego miesiąca
    new_entry = f"\n\n### {day}\n"
    for msg in messages:
        new_entry += f"- {msg}\n"
        
    existing_content = ""
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            existing_content = f.read()
            
    with open(filename, "w", encoding="utf-8") as f:
        f.write(new_entry + existing_content)
        
    return True

if __name__ == "__main__":
    send_telegram_message("Cześć! Co dzisiaj się nauczyłeś?")
    msgs = get_updates()
    if msgs:
        if save_to_markdown(msgs):
            send_telegram_message(f"Zapisano {len(msgs)} wpisów do Twojego TIL!")
