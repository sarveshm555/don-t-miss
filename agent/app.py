import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from agent.models.reminder_schema import AgentRequest, AgentResponse
from agent.reminder_agent import ReminderAgent

app = FastAPI(
    title="Don't Miss AI Agent Backend",
    description="AWS Strands Agents SDK powered backend connected to local Ollama for reminder extraction with human confirmation",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = ReminderAgent()

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "sdk": "strands-agents",
        "model_provider": "ollama",
        "model": agent.model_id,
        "host": agent.host,
    }

@app.post("/agent/reminder", response_model=AgentResponse)
async def create_reminder_proposal(request: AgentRequest):
    if not request.prompt or not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
    
    response = await agent.process_prompt_async(
        prompt=request.prompt,
        current_date=request.current_date,
        current_time=request.current_time,
    )
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, timeout_keep_alive=180)
