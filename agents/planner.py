import dspy
from typing import Any


class PlannerWithSwitchTask(dspy.Signature):
    """
    You are a crypto expert agent, you can help user to analyze crypto tokens and manage their crypto assets.
    
    # Terms
    1. Buy / sell {tokenSymbol} ({tokenAddress}): Swapping tokens using "EXECUTE_SWAP", default to buying with SOL or selling for SOL
    2. Automatic Task: Limit order which is triggered by price or time using "AUTO_TASK"
    
    
    # Objective
    1. Figure out the best action to take based on the user's latest message and the past steps taken.
    2. If the task definition does not match the user's latest message, generate a new task using "SWITCH_TASK". Otherwise, break the task into smaller steps and plan the next action to take based on the task definition and past steps taken.
    
    # Guideline:
    1. If the task is completely finished or unable to proceed based on the past steps, wrap up the process and call the action "WRAP_UP".
    2. Retry last action if it was pending user's input
    3. Never repeat the last action if it is completed
    4. If the task requires only general response, call the action "GENERAL_CHAT".
    """

    chat_history = dspy.InputField(description="Chat history")
    new_message = dspy.InputField(description="Latest message from the user")
    task_definition = dspy.InputField(description="Task definition")
    available_action = dspy.InputField(description="List of actions you can take")
    past_steps = dspy.InputField(description="Past actions taken and their results:")
    is_same_task = dspy.OutputField(description="Reasoning if the current task definition matches the user's latest message")
    summary_of_past_steps = dspy.OutputField(description="Summary of the past steps and whether you should wrap up the process")
    action = dspy.OutputField(description="Action to take")
    parameters: dict[str, Any] = dspy.OutputField(
        description="Parameters for the action"
    )
    explanation = dspy.OutputField(description="Explanation to action and parameters in natural language")
    
class Planner(dspy.Signature):
    """
    You are a crypto expert agent, you can help user to analyze crypto tokens and manage their crypto assets.
    
    # Terms
    1. Buy / sell {tokenSymbol} ({tokenAddress}): Swapping tokens using "EXECUTE_SWAP", default to buying with SOL or selling for SOL
    2. Automatic Task: Limit order which is triggered by price or time using "AUTO_TASK"
    
    # Objective
    1. Figure out the best action to take based on the user's latest message and the past steps taken.
    2. Break the task into smaller steps and plan the next action to take based on the task definition and past steps taken.
    
    # Guideline:
    1. If the task is completely finished or unable to proceed based on the past steps, wrap up the process and call the action "WRAP_UP".
    2. Retry last action if it was pending user's input
    3. Never repeat the last action if it is completed
    4. If the task requires only general response, call the action "GENERAL_CHAT".
    5. When "AUTO_TASK" is successfully created, the action is completed, no further execution is needed.
    """
    available_action = dspy.InputField(description="List of actions you can take")
    chat_history = dspy.InputField(description="Chat history")
    new_message = dspy.InputField(description="Latest message from the user")
    task_definition = dspy.InputField(description="Task definition")
    past_steps = dspy.InputField(description="Past actions taken and their results:")
    is_same_task = dspy.OutputField(description="Reasoning if the current task definition matches the user's latest message")
    summary_of_past_steps = dspy.OutputField(description="Summary of the past steps and whether you should wrap up the process")
    action = dspy.OutputField(description="Action to take")
    parameters: dict[str, Any] = dspy.OutputField(
        description="Parameters for the action"
    )
    explanation = dspy.OutputField(description="Explanation to action and parameters in natural language")