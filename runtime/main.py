from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Dict, Any, List
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .executor import AIONRuntime
from . import database as db
from . import auth
from .config import config

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="AION Runtime", version="0.1.0")

# Add rate limit exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

runtime = AIONRuntime()

class FlowCreateRequest(BaseModel):
    dsl: Dict[str, Any]

class UserCreate(BaseModel):
    username: str
    password: str

@app.on_event("startup")
def startup_event():
    db.init_db()

@app.get("/")
def health_check():
    return {"status": "ok", "service": "AION Runtime"}

@app.get("/health")
def health_check_alias():
    """Compatibility healthcheck endpoint used by proxies and the Studio API client."""
    return {"status": "ok", "service": "AION Runtime"}

# --- Auth APIs ---

@app.post("/auth/register")
@limiter.limit("5/minute")  # Rate limit registration
def register(request: Request, user: UserCreate):
    hashed_pw = auth.get_password_hash(user.password)
    user_id = db.create_user(user.username, hashed_pw)
    if not user_id:
        raise HTTPException(status_code=400, detail="Username already registered")
    return {"message": "User created successfully"}

@app.post("/auth/token", response_model=auth.Token)
@limiter.limit("10/minute")  # Rate limit login attempts
def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = db.get_user_by_username(form_data.username)
    if not user_dict or not auth.verify_password(form_data.password, user_dict["hashed_password"]):
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = auth.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user_dict["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- Flow APIs (Protected) ---

@app.post("/flows")
def register_flow(request: FlowCreateRequest, current_user: auth.User = Depends(auth.get_current_user)):
    flow_id = db.create_flow(request.dsl, user_id=current_user.id)
    return {"id": flow_id, "message": "Flow registered successfully"}

@app.get("/flows")
def list_flows(current_user: auth.User = Depends(auth.get_current_user)):
    return db.list_flows(user_id=current_user.id)

@app.get("/flows/{flow_id}")
def get_flow(flow_id: str, current_user: auth.User = Depends(auth.get_current_user)):
    flow = db.get_flow(flow_id, user_id=current_user.id)
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")
    return flow

@app.patch("/flows/{flow_id}")
def update_flow(flow_id: str, request: FlowCreateRequest, current_user: auth.User = Depends(auth.get_current_user)):
    """Update an existing flow"""
    # Check if flow exists and user owns it
    existing = db.get_flow(flow_id, user_id=current_user.id)
    if not existing:
        raise HTTPException(status_code=404, detail="Flow not found or access denied")
    
    # Update the flow (we'll need to add update_flow function to database.py)
    updated = db.update_flow(flow_id, request.dsl, user_id=current_user.id)
    if not updated:
        raise HTTPException(status_code=400, detail="Failed to update flow")
    return {"message": "Flow updated successfully"}

@app.delete("/flows/{flow_id}")
def delete_flow(flow_id: str, current_user: auth.User = Depends(auth.get_current_user)):
    """Delete a flow"""
    deleted = db.delete_flow(flow_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Flow not found or access denied")
    return {"message": "Flow deleted successfully"}

# --- Execution APIs (Protected) ---

@app.post("/flows/{flow_id}/execute")
async def execute_saved_flow(flow_id: str, background_tasks: BackgroundTasks, current_user: auth.User = Depends(auth.get_current_user)):
    # 1. Get Flow (enforcing ownership)
    flow_data = db.get_flow(flow_id, user_id=current_user.id)
    if not flow_data:
        raise HTTPException(status_code=404, detail="Flow not found or access denied")
    
    from compiler.compiler import AIONCompiler
    compiler = AIONCompiler()
    try:
        plan = compiler.compile(flow_data["dsl"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Compilation Failed: {str(e)}")

    # 3. Create Execution Record
    exec_id = db.create_execution(flow_id, user_id=current_user.id)
    
    # 4. Trigger Execution (Background)
    background_tasks.add_task(run_and_track_execution, exec_id, plan)
    
    return {"execution_id": exec_id, "status": "pending"}

@app.get("/executions/{exec_id}")
def get_execution_status(exec_id: str, current_user: auth.User = Depends(auth.get_current_user)):
    execution = db.get_execution(exec_id, user_id=current_user.id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution

async def run_and_track_execution(exec_id: str, plan: Dict[str, Any]):
    # Update status to running
    db.update_execution(exec_id, "running")
    
    try:
        result = await runtime.execute_plan(plan)
        # Update status to completed
        db.update_execution(exec_id, "completed", result)
    except Exception as e:
        # Update status to failed
        db.update_execution(exec_id, "failed", {"error": str(e)})

# --- Secrets APIs (Protected) ---
from . import secrets_db
from . import encryption

class SecretCreateRequest(BaseModel):
    key: str
    value: str

@app.post("/secrets")
def create_secret(request: SecretCreateRequest, current_user: auth.User = Depends(auth.get_current_user)):
    """Create a new encrypted secret"""
    encrypted_value = encryption.encrypt_value(request.value)
    secret_id = secrets_db.create_secret(current_user.id, request.key, encrypted_value)
    return {"id": secret_id, "message": "Secret created successfully"}

@app.get("/secrets")
def list_secrets(current_user: auth.User = Depends(auth.get_current_user)):
    """List all secrets for the current user (values masked)"""
    return secrets_db.list_secrets(current_user.id)

@app.delete("/secrets/{secret_id}")
def delete_secret(secret_id: str, current_user: auth.User = Depends(auth.get_current_user)):
    """Delete a secret"""
    deleted = secrets_db.delete_secret(secret_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Secret not found")
    return {"message": "Secret deleted successfully"}

# --- Copilot APIs (Protected) ---
from .copilot import AIONCopilot

copilot = AIONCopilot()

class CopilotPromptRequest(BaseModel):
    prompt: str

@app.post("/copilot/generate")
async def copilot_generate(request: CopilotPromptRequest, current_user: auth.User = Depends(auth.get_current_user)):
    dsl = await copilot.generate_flow_from_prompt(request.prompt)
    return {"dsl": dsl}

@app.post("/copilot/validate")
async def copilot_validate(request: FlowCreateRequest, current_user: auth.User = Depends(auth.get_current_user)):
    result = await copilot.validate_flow(request.dsl)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
