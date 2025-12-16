import sys
import os
from fastapi import FastAPI, HTTPException
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
    allow_origins=["*"], # In production, replace with specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Digital Self
# We do this at module level so it persists
try:
    bot = DigitalSelf()
    print("Digital Self initialized.")
except Exception as e:
    print(f"Failed to initialize Digital Self: {e}")
    bot = None

class ChatRequest(BaseModel):
    message: str
    model: str = "llama3" # Default

@app.get("/health")
def health_check():
    return {"status": "ok", "bot_initialized": bot is not None}

@app.post("/chat")
async def chat(request: ChatRequest):
    request_model = request.model
    print(f"[API] Incoming Chat Request. Model: {request_model} | Length: {len(request.message)}")
    
    if not bot:
        raise HTTPException(status_code=500, detail="Digital Self not initialized")
    
    user_input = request.message
    
    # The DigitalSelf.chat method returns a generator for streaming or a strong/generator depending on implementation.
    # We need to adapt it for StreamingResponse.
    
    response_generator = bot.chat(user_input, model=request.model)
    
    async def stream_wrapper():
        # digital_self.chat returns a generator.
        # It yields chunks of text.
        try:
            for chunk in response_generator:
                if isinstance(chunk, dict) and 'message' in chunk: # Ollama raw response
                     yield chunk['message']['content']
                elif isinstance(chunk, str):
                     yield chunk
                # If it's the error generator or simple string generator
                # Attempt to access attribute if it is an object (Ollama Client v0.1.6+)
                elif hasattr(chunk, 'message') and hasattr(chunk.message, 'content'):
                     yield chunk.message.content
                else: 
                     yield str(chunk)
        except Exception as e:
            yield f"[Error: {e}]"

    return StreamingResponse(stream_wrapper(), media_type="text/plain")

@app.get("/memories")
def get_memories():
    if not bot:
         raise HTTPException(status_code=503, detail="Digital Self not initialized")
    return bot.memory_controller.get_all_memories()

@app.get("/models")
def get_models():
    import ollama
    try:
        # ollama.list() returns {'models': [...]}
        return ollama.list()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
