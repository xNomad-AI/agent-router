import dspy
from typing import Any


class Planner(dspy.Signature):
    """
    Plan the next step to take based on the user request and past steps taken.
    # Guideline:
    1. Each step involves at most one action.
    2. If it is the last step, wrap up the process and call the action "WRAP_UP"
    """

    chat_history = dspy.InputField(description="Chat history")
    user_request = dspy.InputField(description="User request")
    available_action = dspy.InputField(description="List of actions you can take")
    past_steps = dspy.InputField(description="Past steps taken:")
    next_step = dspy.OutputField(description="Next atomic step to take")
    action = dspy.OutputField(description="Action to take")
    parameters: dict[str, Any] = dspy.OutputField(
        description="Parameters for the action"
    )
