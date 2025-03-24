import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Any
import dspy
from dotenv import load_dotenv
import json
from loguru import logger
import sys
from datetime import datetime
import pathlib

from agents.planner import Planner, PlannerWithSwitchTask
from agents.action import ACTION_LIST

# Load environment variables
load_dotenv()

# Configure logger
log_dir = "log"
pathlib.Path(log_dir).mkdir(exist_ok=True)
log_file = f"{log_dir}/{datetime.now().strftime('%Y-%m-%d')}.log"
logger.remove()  # Remove default logger
logger.add(sys.stderr, level="INFO")  # Add stderr logger
logger.add(log_file, rotation="00:00", level="INFO")  # Add file logger with daily rotation

# Initialize FastAPI app
app = FastAPI(
    title="Action Planner API",
    description="API that accepts chat history and returns an action",
)

# Initialize language model
model = "openai/gpt-4o-mini"
lm = dspy.LM(model=model, api_key=os.getenv("OPENAI_API_KEY"))

dspy.configure(lm=lm)

class Media(BaseModel):
    id: str
    url: str
    title: str
    source: str
    description: str
    text: str
    contentType: str | None = None

# Define request and response models
class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    attachments: list[Media] | None = None  # attachments, explicitly optional with default None


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
        logger.info(f"request: {json.dumps(request.dict(), default=str)}")
        task_definition = request.task_definition
        chat_history = request.chat_history[:-1]
        last_message = request.chat_history[-1]
        if last_message.role == "user":
            new_message = last_message.content
            if last_message.attachments:
                new_message += f" (Attachment: {last_message.attachments[0].url})"
        else:
            new_message = ""
        past_steps = request.past_steps
        switched_task = request.switched_task

        chat_history_str = ""
        for msg in chat_history:
            chat_history_str += f"{msg.role}: {msg.content}"
            if msg.attachments:
                chat_history_str += f" (Attachment: {msg.attachments[0].url})"
            chat_history_str += "\n"
            
        actions = [action for action in request.actions if action is not None] + [WRAP_UP_ACTION, GENERAL_CHAT_ACTION]
        
        # for CREATE_TOKEN, change the action name to LAUNCH_TOKEN
        for action in actions:
            if action["name"] == "CREATE_TOKEN":
                action["name"] = "LAUNCH_TOKEN"

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

        # for LAUNCH_TOKEN, change the action name to CREATE_TOKEN
        if response.action == "LAUNCH_TOKEN":
            response.action = "CREATE_TOKEN"
        logger.info(f"is_same_task: {response.is_same_task}")
        
        if switched_task == False:
            logger.info(f"should_repeat_last_step: {response.should_repeat_last_step}")
        logger.info(f"summary_of_past_steps: {response.summary_of_past_steps}")
        logger.info(f"action: {response.action}\n parameters: {response.parameters}\n action_description: {response.action_description}")
        return PlanResponse(
            action=response.action.strip('"'),
            parameters=response.parameters,
            explanation=response.action_description.strip('"'),
        )

    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()
    
    if args.debug:
        uvicorn.run(app, host="0.0.0.0", port=8081, log_level="info")
    else:
        uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
