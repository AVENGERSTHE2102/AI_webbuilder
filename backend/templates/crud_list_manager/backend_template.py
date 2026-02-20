"""
Pre-tested CRUD List Manager Backend Template
This template is GUARANTEED to work - it's the foundation for all generated apps.

Template Variables (replaced by AI):
- {ENTITY_NAME} → "Recipe", "Todo", "Contact"
- {ENTITY_NAME_LOWER} → "recipe", "todo", "contact"
- {PYDANTIC_MODEL_CODE} → AI-generated Pydantic model
- {API_ENDPOINTS_CODE} → AI-generated CRUD endpoints
- {DESCRIPTION} → User's app description
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from datetime import datetime

# App metadata
APP_TITLE = "{ENTITY_NAME} Manager"
APP_DESCRIPTION = "{DESCRIPTION}"
APP_VERSION = "1.0.0"

# Initialize FastAPI app
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION
)

# CORS Configuration - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# PYDANTIC MODELS (AI-GENERATED)
# ============================================================================

{PYDANTIC_MODEL_CODE}

# ============================================================================
# IN-MEMORY STORAGE (No database setup needed)
# ============================================================================

{ENTITY_NAME_LOWER}_store: List[{ENTITY_NAME}] = []
next_id = 1

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": APP_TITLE,
        "version": APP_VERSION,
        "timestamp": datetime.now().isoformat()
    }

{API_ENDPOINTS_CODE}

# ============================================================================
# SERVER STARTUP
# ============================================================================

if __name__ == "__main__":
    print(f"🚀 Starting {APP_TITLE}...")
    print(f"📝 {APP_DESCRIPTION}")
    print(f"🌐 Server running at: http://localhost:8000")
    print(f"📚 API docs at: http://localhost:8000/docs")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
