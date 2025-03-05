import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Any
import dspy
from dotenv import load_dotenv
from ast import literal_eval
import json

from planner import ActionExecutor, ACTION_LIST, InstructionPlanner
from action import TOOLS

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Action Planner API",
    description="API that accepts chat history and returns an action",
)

# Initialize language model
model = "openai/gpt-4o"
lm = dspy.LM(model=model, api_key=os.getenv("OPENAI_API_KEY"))

dspy.configure(lm=lm)


# Define request and response models
class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str


class ActionRequest(BaseModel):
    chat_history: List[ChatMessage]
    plan: list[str]
    current_step: str


class ActionResponse(BaseModel):
    action: str
    parameters: dict[str, Any]


class InstructionRequest(BaseModel):
    chat_history: List[ChatMessage]


class InstructionResponse(BaseModel):
    instruction_list: list[str]


@app.post("/execute-action", response_model=ActionResponse)
async def execute_action(request: ActionRequest):
    try:
        # Format chat history as a string
        user_prompt = request.chat_history[-1].content

        chat_history_str = ""
        for msg in request.chat_history[:-1]:
            chat_history_str += f"{msg.role}: {msg.content}\n"

        # Use the ActionPlanner to predict the action
        plan_action = dspy.Predict(ActionExecutor)
        response = plan_action(
            user_prompt=user_prompt,
            chat_history=chat_history_str,
            plan=request.plan,
            current_step=request.current_step,
            action_list=TOOLS,
        )

        return ActionResponse(
            action=response.action, parameters=json.loads(response.parameters)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error planning action: {str(e)}")


@app.post("/plan-instruction", response_model=InstructionResponse)
async def plan_instruction(request: InstructionRequest):
    try:
        # Format chat history as a string
        user_prompt = request.chat_history[-1].content

        chat_history_str = ""
        for msg in request.chat_history[:-1]:
            chat_history_str += f"{msg.role}: {msg.content}\n"

        # Use the ActionPlanner to predict the action
        plan_instruction = dspy.Predict(InstructionPlanner, tools=[])
        response = plan_instruction(
            user_prompt=user_prompt,
            chat_history=chat_history_str,
            action_list=ACTION_LIST,
        )

        return InstructionResponse(instruction_list=response.instruction_list)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error planning action: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
