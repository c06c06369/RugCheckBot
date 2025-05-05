import requests

HELIUS_API_KEY = "933b7a3d-87bf-443e-a840-e68a60ca2ce1"
HELIUS_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"

def is_safe_token(mint_address):
    try:
        headers = {"Content-Type": "application/json"}

        # 查詢 token metadata
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTokenLargestAccounts",
            "params": [mint_address]
        }
        response = requests.post(HELIUS_URL, json=payload, headers=headers)
        result = response.json().get("result", {}).get("value", [])

        if not result:
            return False  # 無有效帳戶

        # 查詢 LP 資訊
        for acct in result:
            if int(acct.get("amount", 0)) > 0:
                token_account = acct.get("address")

                check_lp = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getAccountInfo",
                    "params": [token_account, {"encoding": "jsonParsed"}]
                }
                r2 = requests.post(HELIUS_URL, json=check_lp, headers=headers)
                parsed = r2.json().get("result", {}).get("value", {}).get("data", {}).get("parsed", {})
                if parsed.get("type") == "account":
                    owner = parsed.get("info", {}).get("owner")
                    if owner and owner != "11111111111111111111111111111111":
                        return True  # 有正常 LP

        return False

    except Exception as e:
        print("rugcheck error:", e)
        return False
