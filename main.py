import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Any
import dspy
from dotenv import load_dotenv
import json
from loguru import logger

from agents.planner import Planner, PlannerWithSwitchTask
from agents.action import ACTION_LIST

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Action Planner API",
    description="API that accepts chat history and returns an action",
)

# Initialize language model
model = "openai/gpt-4o-mini"
lm = dspy.LM(model=model, api_key=os.getenv("OPENAI_API_KEY"))

dspy.configure(lm=lm)


# Define request and response models
class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str


class Step(BaseModel):
    action: str
    detail: str
    result: str    


class PlanRequest(BaseModel):
    chat_history: List[ChatMessage]
    task_definition: str
    actions: list[dict | None]
    past_steps: list[Step]
    switched_task: bool


class PlanResponse(BaseModel):
    action: str
    parameters: dict[str, Any]
    explanation: str

WRAP_UP_ACTION = {"name": "WRAP_UP",
            "strict": True,
            "additionalProperties": False,
            "description": """Wrap up the process for previous steps when the user's request is completely executed or it is unable to be completed.
# Guideline
1. Generate a message to the user utilizing the information from previous steps.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The message to wrap up the process or to reply to the user's message"
                    }}}}

GENERAL_CHAT_ACTION = {"name": "GENERAL_CHAT",
            "strict": True,
            "additionalProperties": False,
            "description": """Reply to the user's message. This action is triggered when the user's message is not related to the crypto market.""",
            "parameters": {
                "type": "object",
                "properties": {"message": {"type": "string", "description": "The message to reply to the user"}}}}

SWITCH_TASK_ACTION = {"name": "SWITCH_TASK",
            "strict": True,
            "additionalProperties": False,
            "description": """Generate a new task definition. This action is triggered when the current task definition does not match the user's latest message.""",
            "parameters": {
                "type": "object",
                "properties": {"newTaskDefinition": {"type": "string", "description": "new task definition"}}}}

@app.post("/plan", response_model=PlanResponse)
async def plan(request: PlanRequest):
    try:
        task_definition = request.task_definition
        chat_history = request.chat_history[:-1]
        last_message = request.chat_history[-1]
        if last_message.role == "user":
            new_message = last_message.content
        else:
            new_message = ""
        past_steps = request.past_steps
        switched_task = request.switched_task

        chat_history_str = ""
        for msg in chat_history:
            chat_history_str += f"{msg.role}: {msg.content}\n"
            
        actions = [action for action in request.actions if action is not None] + [WRAP_UP_ACTION, GENERAL_CHAT_ACTION]
        if switched_task == False:
            actions.append(SWITCH_TASK_ACTION)
            plan_action = dspy.Predict(PlannerWithSwitchTask)
        else:
            plan_action = dspy.Predict(Planner)
            
        response = plan_action(
            available_action=actions,
            chat_history=chat_history_str,
            task_definition=task_definition,
            new_message=new_message,
            past_steps=past_steps,
        )

        logger.info(f"is_same_task: {response.is_same_task}")
        logger.info(f"summary_of_past_steps: {response.summary_of_past_steps}")
        logger.info(f"action: {response.action}\n parameters: {response.parameters}\n explanation: {response.explanation}")
        return PlanResponse(
            action=response.action.strip('"'),
            parameters=response.parameters,
            explanation=response.explanation.strip('"'),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
