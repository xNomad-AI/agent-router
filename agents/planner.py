import dspy
from typing import Any


class Planner(dspy.Signature):
    """
    Plan the next action to take based on the user request and past steps taken.
    # Guideline:
    1. If it is the last step for the user request, wrap up the process and call the action "WRAP_UP".
    2. If the user request requires general response, also call the action "WRAP_UP".
    """

    chat_history = dspy.InputField(description="Chat history")
    user_request = dspy.InputField(description="User request")
    available_action = dspy.InputField(description="List of actions you can take")
    past_steps = dspy.InputField(description="Past actions taken and their results:")
    action = dspy.OutputField(description="Action to take")
    parameters: dict[str, Any] = dspy.OutputField(
        description="Parameters for the action"
    )
