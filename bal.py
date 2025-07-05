import requests

def get_aptos_testnet_balance(address: str) -> float:
    """
    Fetch the APT balance of a wallet address on Aptos testnet.
    """
    url = f"https://api.testnet.aptoslabs.com/v1/accounts/{address}/balance/0x1::aptos_coin::AptosCoin"
    try:
        response = requests.get(url)
        response.raise_for_status()
        resources = response.json()
        balance = resources / 10**8
        return balance
    except requests.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return 0.0
    except Exception as e:
        print(f"Error: {e}")
        return 0.0      

# Example usage:
if __name__ == "__main__":
    a = get_aptos_testnet_balance("0xcb5bfe5908c48ec1631ad88a6d61b8e487e9c4bde9285ce74af8320a2f1a2ee5")
    print(a)