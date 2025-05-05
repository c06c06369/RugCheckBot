import requests

HELIUS_API_KEY = "933b7a3d-87bf-443e-a840-e68a60ca2ce1"
HELIUS_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"

def scan_recent_tokens(limit=10):
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [
            "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",  # Token Program
            {"limit": limit}
        ]
    }

    try:
        response = requests.post(HELIUS_URL, json=payload, headers=headers)
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
            tx_response = requests.post(HELIUS_URL, json=tx_data, headers=headers)
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
        print("scan_recent_tokens error:", e)
        return []
