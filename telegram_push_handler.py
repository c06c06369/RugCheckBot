import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_push(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram 資訊未設定")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print("推播失敗:", response.text)
    except Exception as e:
        print("推播錯誤:", e)

def format_push_message(mint, price, fdv, risk_note="無 rug 風險，可上車"):
    msg = f"""
*發現潛力幣種*

*Mint：* `{mint}`
*現價：* ${price:.6f} USDC
*FDV：* ${fdv:,}
*風控結果：* {risk_note}

建議追蹤，如後續主力進場＋熱度放大，可望爆發。
"""
    return msg.strip()
