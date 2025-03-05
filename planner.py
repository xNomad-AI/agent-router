import dspy

ACTION_LIST = {
    "SWAP_TOKEN": "Perform a token swap. buy or sell tokens, supports SOL and SPL tokens swaps.",
    "SEND_TOKEN": "Transfer SPL tokens or SOL from agent's wallet to another address, aka [send |withdraw|transfer] [amount] [tokenSymbol] [tokenCA] to [address] ",
    "ANALYZE_TOKEN": "Analyze the token trade info, twitter binding and news about the token by given symbol or contract address,",
    "CREATE_TOKEN": "Create a new token on pumpfun and buy a specified amount using SOL. Requires the token name, symbol and image url, buy amount after create in SOL.",
    "AUTO_TASK": "Perform auto token swap. Enables the agent to automatically execute trades when specified conditions are met, such as limit orders, scheduled transactions, or other custom triggers, optimizing trading strategies without manual intervention.",
    "WALLET_PORTFOLIO": "Get the wallet total balance or specific token balance in agent wallet",
    "CLAIM_AIRDROP": "Perform claim airdrop for the user agent account",
    "CHAT": "Chat with the user without actually performing any action",
}


class InstructionPlanner(dspy.Signature):
    """ "Given a user prompt, chat history, and a list of actions you can take, return the instructions to take
    # Guideline:
    1. Return high-level instruction step by step in natural langauge.
    2. The instruction should be based on the user prompt and the action list we have.
    3. Be direct and specific.
    """

    action_list = dspy.InputField(description="The list of actions you can take")
    chat_history = dspy.InputField(description="The chat history")
    user_prompt = dspy.InputField(description="The user prompt")
    instruction_list: list[str] = dspy.OutputField(
        description="A list of instructions to take"
    )


class ActionExecutor(dspy.Signature):
    """Given a user prompt, chat history, and a list of actions, return the action to take
    # Guideline:
    1. Only return the action name in the action list, not the action description
    """

    chat_history = dspy.InputField(description="The chat history")
    user_prompt = dspy.InputField(description="The user prompt")
    plan = dspy.InputField(description="The plan to take")
    current_step = dspy.InputField(description="The current step in the plan")
    action_list = dspy.InputField(description="The list of actions")
    action = dspy.OutputField(description="The action to take")
    parameters = dspy.OutputField(description="The parameters for the action")