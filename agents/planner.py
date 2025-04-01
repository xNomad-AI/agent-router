import dspy
from typing import Any

SOL_BACKGROUND_PROMPT = """
You are a crypto expert agent in Solana chain, you can help user to analyze crypto tokens and manage their crypto assets.

# Terms
1. Buy / sell {tokenSymbol} ({tokenAddress}): Swapping tokens using "EXECUTE_SWAP", default to buying with SOL (as inputToken) or selling for SOL (as outputToken)
2. Automatic Task: Limit order which is triggered by price or time using "AUTO_TASK"
3. Native token: The native token of the chain, for solana, it's SOL (So11111111111111111111111111111111111111112)
"""

BSC_BACKGROUND_PROMPT = """
You are a crypto expert agent in BSC chain, you can help user to analyze crypto tokens and manage their crypto assets. Remember, the default token to buy and sell is BNB. BNB is the native token of BSC chain.

# Terms
1. Buy / sell {tokenSymbol} ({tokenAddress}): Swapping tokens using "EXECUTE_SWAP", default to buying with BNB (as inputToken) or selling for BNB (as outputToken)
2. Automatic task to buy / sell {tokenSymbol} ({tokenAddress}): Automatically buying / selling tokens using "AUTO_TASK", default to buying with BNB (as inputToken) or selling for BNB (as outputToken)
3. Native token: The native token of the chain, for BSC chain, it's BNB. When the user specifies 'buy <token>' without specifying inputTokenSymbol, the default inputTokenSymbol is \"BNB\". When the user specifies 'sell <token>' without specifying outputTokenSymbol, the default outputTokenSymbol is \"BNB\".
"""

# Standard Intention Recognition
class PlannerWithSwitchTask(dspy.Signature):
    """
    # Objective
    1. Figure out the best action to take based on the user's latest message and the past steps taken.
    2. If the task definition does not match the user's latest message, generate a new task using "SWITCH_TASK". Otherwise, break the task into smaller steps and plan the next action to take based on the task definition and past steps taken.
    3. User might repeat the same task multiple times, even if the task is completed, if the user's latest message is to run it again, you should obey the user's instruction.
    
    # Guideline:
    1. If the task is completely finished or unable to proceed based on the past steps, wrap up the process and call the action "WRAP_UP".
    2. Repeat last step if it was pending user's input
    3. If the task requires only general response, call the action "GENERAL_CHAT".
    """

    chat_history = dspy.InputField(description="Chat history")
    new_message = dspy.InputField(description="Latest message from the user")
    task_definition = dspy.InputField(description="Task definition")
    available_action = dspy.InputField(description="List of actions you can take")
    past_steps = dspy.InputField(description="Past actions taken and their results")
    last_step = dspy.InputField(description="The most recent step taken and its result")
    is_same_task = dspy.OutputField(description="Repeat the user's latest message and current task definition, and reasoning if the current task definition matches the user's latest message. If the task definition is not the same, output: 'The task definition is not the same, switch to new task with the action \"SWITCH_TASK\"'")
    should_repeat_last_step = dspy.OutputField(description="Repeat the most recent step (last step), the step result, and user's latest message. If last step is not pending, output: 'Last step is not pending, no need to repeat'; If last step is pending and user confirmed, output: 'User confirmed the pending step, repeat the last step'; if last step is pending and user rejected, output: 'User rejected the pending step, skip the last step'")
    summary_of_past_steps = dspy.OutputField(description="Repeat the task definition and summarize the past steps. Reason if the task is fully completed or not. Output 'You should wrap up the process with \"WRAP_UP\"' if the task is fully satisfied by the past steps, otherwise output 'You should continue the process'")
    action = dspy.OutputField(description="Action to take")
    parameters: dict[str, Any] = dspy.OutputField(
        description="Parameters for the action"
    )
    action_description = dspy.OutputField(description="Action and parameters in short natural language")

class PlannerForLoop(dspy.Signature):
    """
    # Objective
    1. Figure out the best action to take based on the past steps taken.
    2. Break the task into smaller steps and plan the next action to take based on the task definition and past steps taken.
    
    # Guideline:
    1. If the task is completely finished or unable to proceed based on the past steps, wrap up the process and call the action "WRAP_UP".
    2. If the task requires only general response, call the action "GENERAL_CHAT".
    """

    chat_history = dspy.InputField(description="Chat history")
    task_definition = dspy.InputField(description="Task definition")
    available_action = dspy.InputField(description="List of actions you can take")
    past_steps = dspy.InputField(description="Past actions taken and their results")
    summary_of_past_steps = dspy.OutputField(description="Repeat the task definition and summarize the past steps. Reason if the task is fully completed or not. Output 'You should wrap up the process with \"WRAP_UP\"' if the task is fully satisfied by the past steps, otherwise output 'You should continue the process'")
    action = dspy.OutputField(description="Action to take")
    parameters: dict[str, Any] = dspy.OutputField(
        description="Parameters for the action"
    )
    action_description = dspy.OutputField(description="Action and parameters in short natural language")
    


# Simplify because the task has been switched, so this step is guaranteed to be the first step
class PlannerForFirstStep(dspy.Signature):
    """
    # Objective
    1. Figure out the best action to take based on the user's latest message and the past steps taken.
    2. Break the task into smaller steps and plan the next action to take based on the task definition and past steps taken.
    
    # Guideline:
    1. If the task is completely finished or unable to proceed based on the past steps, wrap up the process and call the action "WRAP_UP".
    2. If the task requires only general response, call the action "GENERAL_CHAT".
    3. When "AUTO_TASK" is successfully created, the action is completed, no further execution is needed.
    """
    available_action = dspy.InputField(description="List of actions you can take")
    chat_history = dspy.InputField(description="Chat history")
    new_message = dspy.InputField(description="Latest message from the user")
    task_definition = dspy.InputField(description="Task definition")
    action = dspy.OutputField(description="Action to take")
    parameters: dict[str, Any] = dspy.OutputField(
        description="Parameters for the action"
    )
    action_description = dspy.OutputField(description="Action and parameters in short natural language")