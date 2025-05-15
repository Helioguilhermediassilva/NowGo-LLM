from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

# Core and Orchestration imports
from .core.openai_client import test_openai_connection # get_chat_completion is now used by BaseAgent
from .orchestration.orchestrator import handle_user_request

app = FastAPI(
    title="NowGo-LLM Backend",
    description="API for the NowGo-LLM project, providing intelligent contextual AI solutions.",
    version="0.1.0",
    # You can add more metadata like contact, license, etc.
)

# --- Pydantic Models for Request/Response --- #
class InteractiveChatRequest(BaseModel):
    user_id: str
    company_id: str
    prompt: str
    module_accessed: Optional[str] = None
    current_interaction_data: Optional[Dict[str, Any]] = None

class InteractiveChatResponse(BaseModel):
    user_prompt: str
    assistant_response: str
    # We can add more fields like persona_used, context_summary, etc.

# --- Event Handlers --- #
@app.on_event("startup")
async def startup_event():
    print("Starting up NowGo-LLM API...")
    # Initialize any necessary resources, e.g., DB connections, ML models.
    # Test OpenAI connection on startup (optional, ensure .env is configured)
    # print("Performing startup OpenAI connection test...")
    # await test_openai_connection()

@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down NowGo-LLM API...")
    # Clean up resources here if necessary

# --- API Endpoints --- #
@app.get("/health", tags=["Health Check"])
async def health_check():
    """Check the health of the API. Returns a simple status message."""
    return {"status": "ok", "message": "NowGo-LLM API is healthy"}

@app.post("/v1/chat/interactive", response_model=InteractiveChatResponse, tags=["Interactive Chat"])
async def interactive_chat_endpoint(request: InteractiveChatRequest):
    """
    Main endpoint for interactive chat with context-aware, persona-driven LLM.
    Requires user_id, company_id, and a prompt.
    """
    if not request.prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    if not request.user_id or not request.company_id:
        raise HTTPException(status_code=400, detail="user_id and company_id are required")

    try:
        assistant_response = await handle_user_request(
            user_id=request.user_id,
            company_id=request.company_id,
            user_prompt=request.prompt,
            module_accessed=request.module_accessed,
            current_interaction_data=request.current_interaction_data
        )

        if assistant_response is None:
            raise HTTPException(status_code=500, detail="Failed to get a response from the assistant. The LLM or orchestrator might have encountered an issue.")
        
        return InteractiveChatResponse(user_prompt=request.prompt, assistant_response=assistant_response)
    
    except Exception as e:
        # Log the exception for debugging
        print(f"Error during interactive chat: {e}")
        # You might want to have more specific error handling here
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.get("/test_openai/", tags=["Testing"])
async def test_openai_direct_endpoint():
    """A simple endpoint to test the OpenAI connection directly with a predefined prompt."""
    success = await test_openai_connection()
    if success:
        return {"status": "ok", "message": "OpenAI connection test successful. Check logs for response."}
    else:
        # This endpoint should ideally return a 500 if the test fails, 
        # or provide more details on why it failed.
        raise HTTPException(status_code=503, detail="OpenAI connection test failed. Check API key and logs.")

# To run this application (from the /home/ubuntu/NowGo-LLM/backend directory):
# 1. Ensure your OPENAI_API_KEY is set in /home/ubuntu/NowGo-LLM/.env
# 2. Activate the virtual environment: source venv/bin/activate
# 3. Run uvicorn: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# Then access http://localhost:8000/docs for the Swagger UI.

