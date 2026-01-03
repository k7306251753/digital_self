import sys
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

# Add parent directory to path so we can import digital_self
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from digital_self import DigitalSelf

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Digital Self
try:
    bot = DigitalSelf()
    print("Digital Self initialized.")
except Exception as e:
    print(f"Failed to initialize Digital Self: {e}")
    bot = None

class ChatRequest(BaseModel):
    message: str
    model: str = "llama3.2:1b"

@app.get("/health")
def health_check():
    return {"status": "ok", "bot_initialized": bot is not None}

@app.post("/chat")
async def chat(request: ChatRequest, fast_req: Request):
    if not bot:
        raise HTTPException(status_code=503, detail="Digital Self not initialized")
    
    user_input = request.message
    request_model = request.model
    uid = fast_req.headers.get("X-User-Id")
    
    print(f"[API] Chat: {user_input[:50]}... | User: {uid}")
    
    # bot.chat returns a generator (either LLM stream or single-yield intent response)
    response_generator = bot.chat(user_input, model=request_model, user_id=uid)
    
    async def stream_wrapper():
        try:
            for chunk in response_generator:
                yield str(chunk)
        except Exception as e:
            print(f"[API ERROR] {e}")
            yield f"[Chat Error: {e}]"

    return StreamingResponse(stream_wrapper(), media_type="text/plain")

@app.get("/memories")
def get_memories():
    if not bot:
         raise HTTPException(status_code=503, detail="Digital Self not initialized")
    return bot.memory_controller.get_all_memories()

@app.get("/users")
def get_users():
    if not bot:
         raise HTTPException(status_code=503, detail="Digital Self not initialized")
    return bot.list_users()

@app.get("/models")
def get_models():
    import ollama
    try:
        return ollama.list()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("Starting server on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
