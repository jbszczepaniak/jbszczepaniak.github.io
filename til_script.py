import os
import requests
from datetime import datetime

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def get_and_clear_updates():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    response = requests.get(url).json()
    
    print("API getUpdates response:", response)
    
    messages = []
    max_update_id = 0
    
    if "result" in response and response["result"]:
        for update in response["result"]:
            update_id = update["update_id"]
            if update_id > max_update_id:
                max_update_id = update_id
                
            if "message" in update and str(update["message"]["chat"]["id"]) == str(CHAT_ID):
                text = update["message"].get("text")
                if text and not text.startswith("/"):
                    messages.append(text)
        
        print(f"Found max_update_id: {max_update_id}")
        print(f"Extracted messages: {messages}")
        
        if max_update_id > 0:
            clear_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
            clear_response = requests.get(clear_url, params={"offset": max_update_id + 1}).json()
            print(f"Clear offset response: {clear_response}")
            
    else:
        print("No updates found in response.")
        
    return messages

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    res = requests.post(url, json=payload)
    print(f"Send message response: {res.json()}")

def save_to_markdown(messages):
    if not messages:
        return False
        
    now = datetime.now()
    year_month = now.strftime("%Y-%m")
    day = now.strftime("%Y-%m-%d")
    
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
        
    print(f"Successfully saved to {filename}")
    return True

if __name__ == "__main__":
    msgs = get_and_clear_updates()
    
    if msgs:
        if save_to_markdown(msgs):
            count = len(msgs)
            entry_str = "entry" if count == 1 else "entries"
            send_telegram_message(f"Saved {count} new TIL {entry_str} to GitHub! 🚀")
    else:
        print("No new messages found, sending daily prompt.")
        send_telegram_message("What did you learn today?")
