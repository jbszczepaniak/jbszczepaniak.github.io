import os
import requests
from datetime import datetime

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def get_and_clear_updates():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    response = requests.get(url).json()
    messages = []
    max_update_id = 0
    
    if "result" in response and response["result"]:
        for update in response["result"]:
            update_id = update["update_id"]
            if update_id > max_update_id:
                max_update_id = update_id
                
            if "message" in update and str(update["message"]["chat"]["id"]) == str(CHAT_ID):
                text = update["message"].get("text")
                # Ignore commands like /start
                if text and not text.startswith("/"):
                    messages.append(text)
        
        # Acknowledge processed messages so Telegram doesn't send them again
        if max_update_id > 0:
            requests.get(f"{url}?offset={max_update_id + 1}")
            
    return messages

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, json=payload)

def save_to_markdown(messages):
    if not messages:
        return False
        
    now = datetime.now()
    year_month = now.strftime("%Y-%m")
    day = now.strftime("%Y-%m-%d %H:%M")
    
    os.makedirs("til", exist_ok=True)
    filename = f"til/{year_month}.md"
    
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
    # 1. Retrieve all pending messages sent since last run
    msgs = get_and_clear_updates()
    
    # 2. Nuanced response branch
    if msgs:
        if save_to_markdown(msgs):
            count = len(msgs)
            entry_str = "entry" if count == 1 else "entries"
            send_telegram_message(f"Saved {count} new TIL {entry_str} to GitHub! 🚀")
    else:
        # Prompt if nothing was logged today
        send_telegram_message("What did you learn today?")
