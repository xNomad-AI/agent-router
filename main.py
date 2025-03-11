import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Any
import dspy
from dotenv import load_dotenv
import json

from agents.planner import Planner
from agents.action import ACTION_LIST

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


class Step(BaseModel):
    action: str
    detail: str
    result: str    


class PlanRequest(BaseModel):
    chat_history: List[ChatMessage]
    task_definition: str
    past_steps: list[Step]


class PlanResponse(BaseModel):
    action: str
    parameters: dict[str, Any]
    explanation: str


@app.post("/plan", response_model=PlanResponse)
async def plan(request: PlanRequest):
    try:
        task_definition = request.task_definition
        chat_history = request.chat_history
        past_steps = request.past_steps

        chat_history_str = ""
        for msg in chat_history:
            chat_history_str += f"{msg.role}: {msg.content}\n"

        plan_action = dspy.Predict(Planner)
        response = plan_action(
            available_action=ACTION_LIST,
            chat_history=chat_history_str,
            task_definition=task_definition,
            past_steps=past_steps,
        )

        return PlanResponse(
            action=response.action,
            parameters=response.parameters,
            explanation=response.explanation,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
