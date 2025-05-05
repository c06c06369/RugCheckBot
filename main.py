from solana_scanner import scan_recent_tokens
from rugcheck_engine import is_safe_token
from jupiter_price_engine import get_token_price_in_usdc
from telegram_push_handler import send_alert_to_group

def run_bot():
    tokens = scan_recent_tokens(limit=10)
    for mint in tokens:
        if is_safe_token(mint):
            result = get_token_price_in_usdc(mint)
            if result and result["is_tradable"] and result["fdv"] < 300000:
                msg = f"可上車幣種：{mint}\n價格：${result['price']:.6f}\nFDV：約 ${result['fdv']:,}"
                send_alert_to_group(msg)

if __name__ == "__main__":
    run_bot()
