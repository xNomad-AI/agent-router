import dspy
from typing import Any


class PlannerWithSwitchTask(dspy.Signature):
    """
    If the task definition does not match the user's latest message, generate a new task using "SWITCH_TASK". Otherwise, break the task into smaller steps and plan the next action to take based on the task definition and past steps taken.
    # Guideline:
    1. If the task is completely finished or unable to proceed based on the past steps, wrap up the process and call the action "WRAP_UP".
    2. If the last action is pending user's input, and user responded, retry the last action.
    3. Do not repeat the same action in the past steps unless pending.
    4. If the task requires only general response, call the action "GENERAL_CHAT".
    5. If the user's latest message does not match the current task definition, call the action "SWITCH_TASK".
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
    Break the task into smaller steps and plan the next action to take based on the task definition and past steps taken.
    # Guideline:
    1. If the task is completely finished or unable to proceed based on the past steps, wrap up the process and call the action "WRAP_UP".
    2. If the last action is pending user's input, and user responded, retry the last action.
    3. Do not repeat the same action in the past steps unless pending.
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