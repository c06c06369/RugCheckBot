import requests
import os
import time

HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")
RPC_URL = f"https://rpc.helius.xyz/?api-key={HELIUS_API_KEY}"

def scan_recent_tokens(limit=10, mode="mint"):  # mode 可選 'mint' 或 'swap'
    return scan_by_mint(limit) if mode == "mint" else scan_by_swap(limit)

# 方法一：透過 initializeMint 掃描創幣
def scan_by_mint(limit):
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [
            "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
            {"limit": limit}
        ]
    }

    try:
        response = requests.post(RPC_URL, json=payload, headers=headers)
        result = response.json().get("result", [])
        mints = []

        for entry in result:
            sig = entry["signature"]
            tx_data = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTransaction",
                "params": [sig, {"encoding": "jsonParsed"}]
            }
            tx_response = requests.post(RPC_URL, json=tx_data, headers=headers)
            tx = tx_response.json().get("result", {})
            if not tx:
                continue

            instructions = tx.get("transaction", {}).get("message", {}).get("instructions", [])
            for ix in instructions:
                if isinstance(ix, dict) and ix.get("program") == "spl-token":
                    parsed = ix.get("parsed", {})
                    if parsed.get("type") == "initializeMint":
                        mint = parsed.get("info", {}).get("mint")
                        if mint and mint not in mints:
                            mints.append(mint)
        return mints
    except Exception as e:
        print("scan_by_mint error:", e)
        return []

# 方法二：透過 Raydium Swap 抓剛開盤可交易代幣
def scan_by_swap(limit):
    seen = set()
    results = []

    for _ in range(limit * 2):
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getSignaturesForAddress",
                "params": [
                    "9xQeWvG816bUx9EPnDjoPjzJ1yD5R9QmD2uNxDrKWWkJ",  # Raydium
                    {"limit": 100}
                ]
            }

            response = requests.post(RPC_URL, json=payload)
            txs = response.json()["result"]

            for tx in txs:
                sig = tx["signature"]
                if sig in seen:
                    continue
                seen.add(sig)

                info = get_tx_details(sig)
                if info:
                    mint = extract_mint(info)
                    if mint and mint not in results:
                        results.append(mint)
                        if len(results) >= limit:
                            return results
            time.sleep(1)
        except Exception as e:
            print(f"scan_by_swap error: {e}")
            continue
    return results

def get_tx_details(signature):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [signature, {"encoding": "jsonParsed"}]
    }
    try:
        response = requests.post(RPC_URL, json=payload)
        return response.json().get("result")
    except:
        return None

def extract_mint(tx_info):
    try:
        instructions = tx_info["transaction"]["message"]["instructions"]
        for ix in instructions:
            if ix.get("parsed", {}).get("type") == "swap":
                return ix["parsed"]["info"].get("destinationMint")
    except:
        return None
