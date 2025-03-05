from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class ToolBase(BaseModel):
    """Base model for tool"""


def convert_to_schema(model: ToolBase) -> Dict[str, Any]:
    json_schema = model.model_json_schema()
    function_calling_json = {
        "type": "function",
        "function": {
            "name": model.__name__,
            "description": model.__doc__,
            "parameters": json_schema,
        },
    }
    return function_calling_json


class CLAIM_AIRDROP(ToolBase):
    """Claim an airdrop for the user agent account"""

    programName: Optional[str] = Field(
        None, description="The name of the airdrop program to claim"
    )


class ANALYZE_TOKEN(ToolBase):
    """Analyze the token trade info, twitter binding and news about the token by given symbol or contract address"""

    tokenSymbol: Optional[str] = Field(
        None,
        description="The token symbol to analyze, at least one of tokenSymbol or tokenAddress should be provided",
    )
    tokenAddress: Optional[str] = Field(
        None,
        description="The token contract address to analyze, should be a 44 character string, at least one of tokenSymbol or tokenAddress should be provided",
    )
    analyze: Optional[List[str]] = Field(
        None,
        description="The types of analysis to perform, should be an array, items can be 'info', 'news', 'twitter', default to ['info', 'twitter', 'news']",
    )


class AUTO_TASK(ToolBase):
    """Perform auto token swap. Enables the agent to automatically execute trades when specified conditions are met, such as limit orders, scheduled transactions, or other custom triggers, optimizing trading strategies without manual intervention."""

    inputTokenSymbol: Optional[str] = Field(
        None,
        description="Symbol of the token to sell, at least one of inputTokenSymbol or inputTokenCA is required",
    )
    inputTokenCA: Optional[str] = Field(
        None,
        description="Contract address of the token to sell, at least one of inputTokenSymbol or inputTokenCA is required",
    )
    outputTokenSymbol: Optional[str] = Field(
        None,
        description="Symbol of the token to buy, at least one of outputTokenSymbol or outputTokenCA is required",
    )
    outputTokenCA: Optional[str] = Field(
        None,
        description="Contract address of the token to buy, at least one of outputTokenSymbol or outputTokenCA is required",
    )
    inputTokenAmount: Optional[float] = Field(
        None,
        description="Amount of inputToken to swap, at least one of inputTokenAmount or inputTokenPercentage is required",
    )
    inputTokenPercentage: Optional[float] = Field(
        None,
        description="Percentage of inputToken balance to swap, at least one of inputTokenAmount or inputTokenPercentage is required",
    )
    outputTokenAmount: Optional[float] = Field(
        None, description="Amount of outputToken to swap"
    )
    priceCondition: Optional[str] = Field(
        None,
        description='Price condition for the swap, enum "below" or "above", at lease one of delay or priceTarget is provided',
    )
    priceTarget: Optional[float] = Field(None, description="Price target for the swap")
    tokenTarget: Optional[str] = Field(
        None, description="Token address or symbol of the trigger and price targets to"
    )
    delay: Optional[str] = Field(
        None,
        description='Delay for the swap, e.g., "after 5 minutes" or "below 0.00169", at lease one of delay or priceTarget is provided',
    )


class SWAP_TOKEN(ToolBase):
    """Swap tokens on Solana blockchain, set default token symbol to SOL when user want to buy or sell tokens"""

    inputTokenSymbol: Optional[str] = Field(
        None,
        description="Symbol of the token to sell, at least one of inputTokenSymbol or inputTokenCA is required",
    )
    inputTokenCA: Optional[str] = Field(
        None,
        description="Contract address of the token to sell, at least one of inputTokenSymbol or inputTokenCA is required",
    )
    outputTokenSymbol: Optional[str] = Field(
        None,
        description="Symbol of the token to buy, at least one of outputTokenSymbol or outputTokenCA is required",
    )
    outputTokenCA: Optional[str] = Field(
        None,
        description="Contract address of the token to buy, at least one of outputTokenSymbol or outputTokenCA is required",
    )
    inputTokenAmount: Optional[float] = Field(
        None,
        description="Amount of inputToken to swap, at least one of inputTokenAmount or inputTokenPercentage is required",
    )
    inputTokenPercentage: Optional[float] = Field(
        None,
        description="Percentage of inputToken balance to swap, at least one of inputTokenAmount or inputTokenPercentage is required",
    )
    outputTokenAmount: Optional[float] = Field(
        None, description="Amount of outputToken to swap"
    )


class WALLET_PORTFOLIO(ToolBase):
    """Get the wallet total balance or specific token balance in agent wallet"""

    queryType: Optional[str] = Field(
        None,
        description='The type of query, should be "walletBalance" or "tokenBalance", default is walletBalance',
    )
    tokenSymbol: Optional[str] = Field(
        None,
        description='The token symbol to query, at lease one of tokenSymbol or tokenAddress should be provided when queryType is "tokenBalance"',
    )
    tokenAddress: Optional[str] = Field(
        None,
        description='The token contract address to query, at lease one of tokenSymbol or tokenAddress should be provided when queryType is "tokenBalance"',
    )


class SEND_TOKEN(ToolBase):
    """Transfer SPL tokens or SOL from agent wallet to another address"""

    tokenSymbol: Optional[str] = Field(None, description="The token symbol to transfer")
    tokenAddress: Optional[str] = Field(
        None, description="The token contract address to transfer"
    )
    recipient: Optional[str] = Field(None, description="The recipient wallet address")
    amount: Optional[float] = Field(
        None, description="The amount of tokens to transfer"
    )


class CREATE_TOKEN(ToolBase):
    """Create a new token on pumpfun and buy a specified amount using SOL. Requires the token name, symbol and image url, buy amount after create in SOL."""

    name: str = Field(..., description="Name of the token to create")
    symbol: str = Field(..., description="Symbol of the token to create")
    imageUrl: Optional[str] = Field(
        None, description="Image URL or attachment file of the token to create"
    )
    description: Optional[str] = Field(
        None, description="Description of the token to create"
    )
    twitter: Optional[str] = Field(
        None, description="Twitter URL of the token to create"
    )
    website: Optional[str] = Field(
        None, description="Website URL of the token to create"
    )
    telegram: Optional[str] = Field(
        None, description="Telegram URL of the token to create"
    )
    buyAmountSol: Optional[float] = Field(
        None, description="Amount of SOL to buy after token creation"
    )


class WRAP_UP(ToolBase):
    """Wrap up the process for previous steps when the user's request is completed or it is unable to be completed"""

    message: str = Field(..., description="The message to wrap up the process")


class GENERAL_CHAT(ToolBase):
    """Reply to the user's message. This action is triggered when the user's message is not related to the crypto market."""

    message: str = Field(..., description="The message to reply to the user")


ACTION_LIST = [
    convert_to_schema(tool)
    for tool in [
        CLAIM_AIRDROP,
        ANALYZE_TOKEN,
        AUTO_TASK,
        SWAP_TOKEN,
        WALLET_PORTFOLIO,
        SEND_TOKEN,
        CREATE_TOKEN,
        GENERAL_CHAT,
        WRAP_UP,
    ]
]
