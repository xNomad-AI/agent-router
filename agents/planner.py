import dspy
from typing import Any


class Planner(dspy.Signature):
    """
    Break the task into smaller steps and plan the next action to take based on the task definition and past steps taken.
    # Guideline:
    1. If the task is completely finished or unable to proceed based on the past steps, wrap up the process and call the action "WRAP_UP".
    2. If the task requires only general response, also call the action "WRAP_UP".
    3. If the last action is pending user's input, and user responded, retry the last action.
    """

    chat_history = dspy.InputField(description="Chat history")
    task_definition = dspy.InputField(description="Task definition")
    available_action = dspy.InputField(description="List of actions you can take")
    past_steps = dspy.InputField(description="Past actions taken and their results:")
    action = dspy.OutputField(description="Action to take")
    parameters: dict[str, Any] = dspy.OutputField(
        description="Parameters for the action"
    )
    explanation = dspy.OutputField(description="Explanation to action and parameters in natural language")
