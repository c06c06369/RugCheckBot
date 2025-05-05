import requests

def get_token_price_in_usdc(mint):
    try:
        url = f"https://quote-api.jup.ag/v6/quote?inputMint={mint}&outputMint=Es9vMFrzaCER59jZ88fYjBG7mGqDDFMhc5a3wY5PvQfS&amount=1000000&slippage=1"
        response = requests.get(url)
        data = response.json()

        if "data" in data and data["data"]:
            best = data["data"][0]
            out_amount = int(best["outAmount"]) / (10 ** 6)  # USDC decimals
            return {
                "price": out_amount,
                "is_tradable": out_amount > 0.001  # 可調整條件
            }
        else:
            return None
    except Exception as e:
        print("price error:", e)
        return None
