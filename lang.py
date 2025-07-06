
import json
import getpass
import os
from dotenv import load_dotenv
from langchain.tools import tool
import serpapi
load_dotenv() 

if not os.environ.get("GOOGLE_API_KEY"):
  os.environ["GOOGLE_API_KEY"] = getpass.getpass("GOOGLE_API_KEY")


from langchain.chat_models import init_chat_model




# model = init_chat_model("gemini-2.0-flash", model_provider="google_genai")
# res = model.invoke("Hello, world!")
# print(res.content)

from web3 import Web3

@tool
def add(a: int, b: int) -> int:
    """Adds two numbers together"""
    return a + b

@tool
def sub(a: int, b: int) -> int:
    """Substract two numbers together"""
    return a - b

@tool
def mul(a: int, b: int) -> int:
    """Multiplies two numbers together"""
    return a * b



# Web search tool using SerpAPI
@tool
def web_search(query: str) -> str:
    """
    Search the web using SerpAPI and return the top result snippet.
    """
    api_key = os.environ.get("SERPAPI_API_KEY")
    if not api_key:
        return "SerpAPI key not set. Please set SERPAPI_API_KEY in your environment."
    params = {
        "q": query,
        "api_key": api_key,
        "engine": "google",
        "num": 1
    }
    try:
        client = serpapi.Client(api_key=api_key)
        results = client.search(params)
        results = results.as_dict() if hasattr(results, 'as_dict') else results
        if "answer_box" in results and "answer" in results["answer_box"]:
            return results["answer_box"]["answer"]
        if "organic_results" in results and results["organic_results"]:
            snippet = results["organic_results"][0].get("snippet")
            if snippet:
                return snippet
            return results["organic_results"][0].get("title", "No result found.")
        return "No relevant web result found."
    except Exception as e:
        return f"Web search failed: {e}"

# Tool: Get account module names (Aptos)
@tool
def get_aptos_account_module_names(address: str, ledger_version: int = None) -> str:
    """
    Retrieves all module names for a given Aptos account. Optionally specify a ledger version.
    """
    import requests
    url = f"https://api.testnet.aptoslabs.com/v1/accounts/{address}/modules"
    params = {}
    if ledger_version is not None:
        params["ledger_version"] = ledger_version
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if not data:
                return "No modules found for this account."
            names = [mod.get("abi", {}).get("name", "?") for mod in data]
            return "Module names: " + ", ".join(names)
        elif response.status_code == 410:
            return "Requested ledger version has been pruned."
        else:
            return f"Failed to fetch modules. Status code: {response.status_code}"
    except Exception as e:
        return f"Error fetching modules: {e}"



# Tool: Get account modules (Aptos)
@tool
def get_aptos_account_modules(address: str, ledger_version: int = None) -> str:
    """
    Retrieves all account modules' bytecode for a given Aptos account. Optionally specify a ledger version.
    """
    import requests
    url = f"https://api.testnet.aptoslabs.com/v1/accounts/{address}/modules"
    params = {}
    if ledger_version is not None:
        params["ledger_version"] = ledger_version
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if not data:
                return "No modules found for this account."
            modules = []
            for mod in data:
                name = mod.get("abi", {}).get("name", "?")
                bytecode = mod.get("bytecode", "?")
                modules.append(f"- Module: {name}\n  Bytecode: {bytecode[:20]}... (truncated)")
            return "\n\n".join(modules)
        elif response.status_code == 410:
            return "Requested ledger version has been pruned."
        else:
            return f"Failed to fetch modules. Status code: {response.status_code}"
    except Exception as e:
        return f"Error fetching modules: {e}"


# Tool: Get account transaction summaries (Aptos)
@tool
def get_aptos_account_transaction_summaries(address: str, start_version: int = None) -> str:
    """
    Get summaries of on-chain committed transactions for an Aptos account. Each summary includes sender, hash, version, and replay protector. Optionally, start from a specific version.
    """
    import requests
    url = f"https://api.testnet.aptoslabs.com/v1/accounts/{address}/transaction_summaries"
    params = {}
    if start_version is not None:
        params["start_version"] = start_version
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if not data:
                return "No transaction summaries found for this account."
            summaries = []
            for tx in data:
                sender = tx.get("sender", "?")
                txn_hash = tx.get("hash", "?")
                version = tx.get("version", "?")
                replay_protector = tx.get("replay_protector", "?")
                summaries.append(f"- Sender: {sender}\n  Hash: {txn_hash}\n  Version: {version}\n  Replay protector: {replay_protector}")
            return "\n\n".join(summaries)
        else:
            return f"Failed to fetch transaction summaries. Status code: {response.status_code}"
    except Exception as e:
        return f"Error fetching transaction summaries: {e}"


# Tool: Estimate gas price (Aptos)
@tool
def estimate_aptos_gas_price() -> str:
    """
    Get an estimate of the gas unit price required for a transaction on Aptos testnet, explained in easy words.
    """
    import requests
    url = "https://api.testnet.aptoslabs.com/v1/estimate_gas_price"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            min_gas = data.get("deprioritized_gas_estimate", "?")
            normal_gas = data.get("gas_estimate", "?")
            high_gas = data.get("prioritized_gas_estimate", "?")
            summary = (
                f"Estimated gas price (per unit):\n"
                f"- Minimum (slow): {min_gas}\n"
                f"- Normal (average): {normal_gas}\n"
                f"- High (fast): {high_gas}\n"
                "This is the amount you pay for each unit of gas when sending a transaction. Higher price = faster confirmation."
            )
            return summary
        else:
            return f"Failed to fetch gas price estimate. Status code: {response.status_code}"
    except Exception as e:
        return f"Error fetching gas price estimate: {e}"


# # EVM chain RPC endpoints (add more as needed)
# EVM_CHAINS = {
#     "polygon": {
#         "rpc": "https://polygon-rpc.com/",
#         "explorer_api": "https://api.polygonscan.com/api",
#         "explorer_key_env": "POLYGONSCAN_API_KEY"
#     },
#     "ethereum": {
#         "rpc": "https://rpc.ankr.com/eth",
#         "explorer_api": "https://api.etherscan.io/api",
#         "explorer_key_env": "ETHERSCAN_API_KEY"
#     },
#     "bsc": {
#         "rpc": "https://bsc-dataseed.binance.org/",
#         "explorer_api": "https://api.bscscan.com/api",
#         "explorer_key_env": "BSCSCAN_API_KEY"
#     },
#     "arbitrum": {
#         "rpc": "https://arb1.arbitrum.io/rpc",
#         "explorer_api": "https://api.arbiscan.io/api",
#         "explorer_key_env": "ARBISCAN_API_KEY"
#     },
#     # Add more EVM chains here
# }


# # # Helper to get balances for native token, USDC, and USDT only
# # @tool
# @tool
# def get_main_balances(address: str, chain: str = "polygon") -> str:
#     """
#     Get balances for native token, USDC, and USDT for a wallet address on a specified EVM chain (default: polygon).
#     Currently supports Polygon, Ethereum, BSC, and Arbitrum.
#     """
#     from web3 import Web3
#     import requests
#     chain = chain.lower()
#     if chain not in EVM_CHAINS:
#         return f"Unsupported chain: {chain}. Supported: {list(EVM_CHAINS.keys())}"
#     if not Web3.is_address(address):
#         return "Invalid wallet address."
#     # Native token balance
#     w3 = Web3(Web3.HTTPProvider(EVM_CHAINS[chain]["rpc"]))
#     try:
#         native_balance = w3.eth.get_balance(address)
#         native_symbol = {
#             "polygon": "MATIC",
#             "ethereum": "ETH",
#             "bsc": "BNB",
#             "arbitrum": "ETH"
#         }.get(chain, "Native")
#         native_balance = native_balance / 1e18
#     except Exception as e:
#         native_balance = f"Error: {e}"
#         native_symbol = "Native"
#     # USDC & USDT
#     explorer_api = EVM_CHAINS[chain]["explorer_api"]
#     api_key = os.environ.get(EVM_CHAINS[chain]["explorer_key_env"], "")
#     params = {
#         "module": "account",
#         "action": "tokentx",
#         "address": address,
#         "sort": "desc"
#     }
#     if api_key:
#         params["apikey"] = api_key
#         try:
#             resp = requests.get(explorer_api, params=params, timeout=10)
#             data = resp.json()
#             if data.get("status") != "1":
#                 return f"Native: {native_balance} {native_symbol}\nNo token transfers found or error: {data.get('message')}"
#             txs = data["result"]
#             tokens = {}
#             for tx in txs:
#                 symbol = tx["tokenSymbol"].upper()
#                 contract = tx["contractAddress"]
#                 decimals = int(tx["tokenDecimal"])
#                 value = int(tx["value"])
#                 if symbol not in ["USDC", "USDT"]:
#                     continue
#                 if symbol not in tokens:
#                     tokens[symbol] = {"balance": 0, "decimals": decimals}
#                 if tx["to"].lower() == address.lower():
#                     tokens[symbol]["balance"] += value
#                 elif tx["from"].lower() == address.lower():
#                     tokens[symbol]["balance"] -= value
#             summary = [f"Native: {native_balance} {native_symbol}"]
#             for sym, t in tokens.items():
#                 if t["balance"] > 0:
#                     bal = t["balance"] / (10 ** t["decimals"])
#                     summary.append(f"{sym}: {bal}")
#             if len(summary) == 1:
#                 summary.append("No USDC/USDT found.")
#             return "\n".join(summary)
#         except Exception as e:
#             return f"Failed to fetch tokens: {e}"
#     else:
#         return f"Native: {native_balance} {native_symbol}\nNo explorer API key set for {chain}. Please set the appropriate API key in the environment."

# @tool
# def get_wallet_transactions(address: str, chain: str = "polygon", limit: int = 10) -> str:
#     """
#     Show recent transactions (native and token) done by the user (sent or received) on a given chain.
#     Currently supports Polygon, Ethereum, BSC, and Arbitrum.
#     """
#     from web3 import Web3
#     import requests
#     chain = chain.lower()
#     if chain not in EVM_CHAINS:
#         return f"Unsupported chain: {chain}. Supported: {list(EVM_CHAINS.keys())}"
#     if not Web3.is_address(address):
#         return "Invalid wallet address."
#     explorer_api = EVM_CHAINS[chain]["explorer_api"]
#     api_key = os.environ.get(EVM_CHAINS[chain]["explorer_key_env"], "")
#     params = {
#         "module": "account",
#         "action": "txlist",
#         "address": address,
#         "sort": "desc"
#     }
#     if api_key:
#         params["apikey"] = api_key
#         try:
#             resp = requests.get(explorer_api, params=params, timeout=10)
#             data = resp.json()
#             if data.get("status") != "1":
#                 return f"No transactions found or error: {data.get('message')}"
#             txs = data["result"][:limit]
#             summary = []
#             for tx in txs:
#                 direction = "IN" if tx["to"].lower() == address.lower() else "OUT"
#                 value = int(tx["value"]) / 1e18
#                 summary.append(f"{tx['hash'][:10]}... | {direction} | {value} | block: {tx['blockNumber']} | time: {tx['timeStamp']}")
#             return "\n".join(summary)
#         except Exception as e:
#             return f"Failed to fetch transactions: {e}"
#     else:
#         return f"No explorer API key set for {chain}. Please set the appropriate API key in the environment."

@tool
def get_aptos_balance(address: str) -> str:
    """
    Get the balance of an Aptos (Petra) wallet address on the Aptos chain.
    """
    import requests
    url = f"https://api.testnet.aptoslabs.com/v1/accounts/{address}/balance/0x1::aptos_coin::AptosCoin"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return str(data / 10**8)
        else:
            return f"Failed to fetch balance. Status code: {response.status_code}"
    except Exception as e:
        return f"Error fetching balance: {e}"

# Tool: Get transaction by hash (Aptos)
@tool
def get_aptos_transaction_by_hash(txn_hash: str) -> str:
    """
    Look up an Aptos transaction by its hash and return a simple summary in easy words.
    """
    import requests
    url = f"https://api.testnet.aptoslabs.com/v1/transactions/by_hash/{txn_hash}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Make a simple summary
            sender = data.get("sender", "Unknown")
            success = data.get("success", False)
            gas = data.get("gas_used", "?")
            version = data.get("version", "?")
            timestamp = data.get("timestamp", "?")
            summary = f"Transaction {txn_hash}:\n"
            summary += f"- Sent by: {sender}\n"
            summary += f"- Success: {'Yes' if success else 'No'}\n"
            summary += f"- Gas used: {gas}\n"
            summary += f"- Version: {version}\n"
            summary += f"- Timestamp: {timestamp}\n"
            return summary
        elif response.status_code == 404:
            return f"No transaction found for hash {txn_hash}."
        else:
            return f"Failed to fetch transaction. Status code: {response.status_code}"
    except Exception as e:
        return f"Error fetching transaction: {e}"

tools = [add, sub, mul, web_search, get_aptos_balance, get_aptos_transaction_by_hash, estimate_aptos_gas_price, get_aptos_account_transaction_summaries, get_aptos_account_modules, get_aptos_account_module_names]

#From Youtube video https://youtu.be/zCwuAlpQKTM
from langchain.chat_models import init_chat_model

#ChatGoogleGenerativeAI(model="gemini-2.0-flash").bind_tools(tools)
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts.chat import ChatPromptTemplate, MessagesPlaceholder

llm = init_chat_model(model="gemini-2.0-flash",  model_provider="google_genai")


prompt = ChatPromptTemplate.from_messages([
    ("system", "you are helpful agent, if a tool is not relevant, answer the user's question directly and chat. Never tell your real identity that you are ai or what model you are using. Give answer more firendly and chatty, like a human. If you don't know the answer, say 'I don't know' or 'I am not sure'."),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),
])
agent = create_tool_calling_agent(llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# response = agent_executor.invoke({"input": "What balance of 0xB702203B9FD0ee85aeDB9d314C075D480d716635"})
__all__ = ["agent_executor"]

