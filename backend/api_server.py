import sys
import os
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from jose import JWTError, jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Add parent directory to path so we can import digital_self
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from digital_self import DigitalSelf
from brain import db # Import DB module directly

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

# Must match Spring Boot's secret
JWT_SECRET = "secure_secret_key_for_digital_self_ai_project_2026"
ALGORITHM = "HS256"

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[ALGORITHM])
        return payload # Contains userId
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

class ChatRequest(BaseModel):
    message: str
    model: str = "llama3.2:1b"
    session_id: str = None # Optional session ID

@app.get("/health")
def health_check():
    return {"status": "ok", "bot_initialized": bot is not None}

@app.post("/chat")
async def chat(request: ChatRequest, fast_req: Request, token_data: dict = Depends(verify_token)):
    if not bot:
        raise HTTPException(status_code=503, detail="Digital Self not initialized")
    
    user_input = request.message
    request_model = request.model
    session_id = request.session_id
    uid = token_data.get("userId")
    
    print(f"[API] Chat: {user_input[:50]}... | UserID: {uid} | Session: {session_id}")
    
    import time
    start_time = time.time()
    
    # 1. Save User Message if session exists
    if session_id:
        db.add_chat_message(session_id, "user", user_input)
    
    # bot.chat returns a generator
    print(f"[API] Preparing generator... ({time.time() - start_time:.3f}s)")
    response_generator = bot.chat(user_input, model=request_model, user_id=uid)
    print(f"[API] Generator ready. ({time.time() - start_time:.3f}s)")
    
    async def stream_wrapper():
        full_response = ""
        try:
            for chunk in response_generator:
                text_chunk = ""
                if isinstance(chunk, dict) and "message" in chunk:
                    text_chunk = chunk["message"]["content"]
                else:
                    text_chunk = str(chunk)
                
                if not full_response:
                    print(f"[API] First chunk yielded. ({time.time() - start_time:.3f}s)")
                
                full_response += text_chunk
                yield text_chunk
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"[API ERROR] {e}")
            yield f"[Chat Error: {e}]"
        finally:
            # 2. Save Assistant Message if session exists
            if session_id and full_response:
                db.add_chat_message(session_id, "assistant", full_response)

    return StreamingResponse(stream_wrapper(), media_type="text/plain")

@app.get("/memories")
def get_memories(token_data: dict = Depends(verify_token)):
    if not bot:
         raise HTTPException(status_code=503, detail="Digital Self not initialized")
    uid = token_data.get("userId")
    return bot.memory_controller.get_all_memories(user_id=uid)

@app.get("/users")
def get_users(token_data: dict = Depends(verify_token)):
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

# --- Chat History Endpoints ---

@app.get("/chats")
def list_chats(token_data: dict = Depends(verify_token)):
    if not bot: raise HTTPException(status_code=503)
    uid = token_data.get("userId")
    return db.get_user_chat_sessions(uid)

@app.post("/chats")
def create_chat(title: str = "New Chat", token_data: dict = Depends(verify_token)):
    if not bot: raise HTTPException(status_code=503)
    uid = token_data.get("userId")
    import uuid
    session_id = str(uuid.uuid4())
    db.create_chat_session(session_id, uid, title)
    return {"id": session_id, "title": title}

@app.get("/chats/{session_id}/messages")
def get_messages(session_id: str, token_data: dict = Depends(verify_token)):
    if not bot: raise HTTPException(status_code=503)
    # Check ownership ideally, but for now just fetch
    return db.get_chat_messages(session_id)

@app.delete("/chats/{session_id}")
def delete_chat(session_id: str, token_data: dict = Depends(verify_token)):
    if not bot: raise HTTPException(status_code=503)
    db.delete_chat_session(session_id)
    return {"status": "deleted"}

@app.put("/chats/{session_id}")
def rename_chat(session_id: str, req: dict, token_data: dict = Depends(verify_token)):
    if not bot: raise HTTPException(status_code=503)
    title = req.get('title')
    if title:
        db.rename_chat_session(session_id, title)
    return {"status": "updated"}

if __name__ == "__main__":
    import uvicorn
    print("Starting server on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
