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

from agents.planner import PlannerForFirstStep, PlannerWithSwitchTask, PlannerForLoop, SOL_BACKGROUND_PROMPT, BSC_BACKGROUND_PROMPT
from agents.action import ACTION_LIST

# Load environment variables
load_dotenv()

# Configure logger
log_dir = "log"
pathlib.Path(log_dir).mkdir(exist_ok=True)
log_file = f"{log_dir}/{{time:YYYY-MM-DD_HH}}.log"  # Use loguru's time formatting
logger.remove()  # Remove default logger
logger.add(sys.stderr, level="INFO")  # Add stderr logger
logger.add(log_file, rotation="1h", level="INFO")  # Use "1h" for hourly rotation

# Initialize FastAPI app
app = FastAPI(
    title="Action Planner API",
    description="API that accepts chat history and returns an action",
)

# Initialize language model
model = "openai/gpt-4o"
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
    chain: str = "solana"


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

def convert_scientific_to_decimal(obj):
    if isinstance(obj, dict):
        return {key: convert_scientific_to_decimal(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_scientific_to_decimal(item) for item in obj]
    elif isinstance(obj, float):
        # Convert scientific notation to decimal format
        return format(obj, 'f').rstrip('0').rstrip('.')
    return obj

def modify_dspy_signature(chain):
    dspy_signature_list = [PlannerForFirstStep, PlannerWithSwitchTask, PlannerForLoop]
    
    if chain == "solana":
        BACKGROUND_PROMPT = SOL_BACKGROUND_PROMPT
    elif chain == "bsc":
        BACKGROUND_PROMPT = BSC_BACKGROUND_PROMPT
    else:
        BACKGROUND_PROMPT = SOL_BACKGROUND_PROMPT        
        logger.warning(f"Invalid chain: {chain}, using Solana background prompt")

    for dspy_signature in dspy_signature_list:
        # Store original doc if not already stored
        if not hasattr(dspy_signature, '_original_doc'):
            dspy_signature._original_doc = dspy_signature.__doc__ or ""
        
        # Reset doc to original + background prompt
        dspy_signature.__doc__ = f"{BACKGROUND_PROMPT}{dspy_signature._original_doc}"

    return dspy_signature_list

@app.post("/plan", response_model=PlanResponse)
async def plan(request: PlanRequest):
    CUSTOM_PLANNER_FOR_FIRST_STEP, CUSTOM_PLANNER_WITH_SWITCH_TASK, CUSTOM_PLANNER_FOR_LOOP = modify_dspy_signature(request.chain)
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
        last_step = request.past_steps[-1] if request.past_steps else None
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
            if new_message:
                actions.append(SWITCH_TASK_ACTION)
                plan_action = dspy.Predict(CUSTOM_PLANNER_WITH_SWITCH_TASK)
                response = plan_action(
                    chat_history=chat_history_str,
                    new_message=new_message,
                    past_steps=past_steps,
                    last_step=last_step,
                    task_definition=task_definition,
                    available_action=actions,
                    
                )
            else:
                plan_action = dspy.Predict(CUSTOM_PLANNER_FOR_LOOP)
                response = plan_action(
                    chat_history=chat_history_str,
                    task_definition=task_definition,
                    past_steps=past_steps,
                    available_action=actions,  
                )
        else:
            plan_action = dspy.Predict(CUSTOM_PLANNER_FOR_FIRST_STEP)
            response = plan_action(     
                chat_history=chat_history_str,
                new_message=new_message,
                task_definition=task_definition,
                available_action=actions,
            )
        
        
        
        # for LAUNCH_TOKEN, change the action name to CREATE_TOKEN
        if response.action == "LAUNCH_TOKEN":
            response.action = "CREATE_TOKEN"
        
        # Complex situation where we have to determine if the task is the same as the user's latest message, and if the last step is pending
        if switched_task == False and new_message:
            logger.info(f"is_same_task: {response.is_same_task}")
            logger.info(f"should_repeat_last_step: {response.should_repeat_last_step}")
            logger.info(f"summary_of_past_steps: {response.summary_of_past_steps}")
        
        logger.info(f"action: {response.action}\n parameters: {response.parameters}\n action_description: {response.action_description}")
        
        # Convert parameters from scientific notation to decimal
        formatted_parameters = convert_scientific_to_decimal(response.parameters)
        
        return PlanResponse(
            action=response.action.strip('"'),
            parameters=formatted_parameters,
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
