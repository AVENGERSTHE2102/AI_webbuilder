"""
Zero-Code AI App Builder - FastAPI Backend Server

Main API server that orchestrates the generation pipeline.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from datetime import datetime
import io
import zipfile
import os
from typing import Dict
from pathlib import Path

from models import GenerateRequest, GenerateResponse, TemplateInfo
from generator import generator
from validator import validator

# Initialize FastAPI app
app = FastAPI(
    title="Zero-Code AI App Builder",
    description="Generate complete full-stack apps from text descriptions",
    version="1.0.0"
)

# CORS Configuration
# Allow Vercel frontend and all origins for flexibility
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
if cors_origins == ["*"]:
    # Allow all origins (includes Vercel, local dev, etc.)
    allowed_origins = ["*"]
else:
    allowed_origins = cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Log CORS configuration
print(f"✅ CORS enabled for origins: {allowed_origins}")

# In-memory storage for generated apps (temporary)
app_storage: Dict[str, bytes] = {}


@app.get("/api")
async def api_root():
    """API health check endpoint"""
    return {
        "status": "online",
        "service": "Zero-Code AI App Builder",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "message": "Send POST to /api/generate with your app description"
    }


@app.post("/api/generate", response_model=GenerateResponse)
async def generate_app(request: GenerateRequest):
    """
    Main endpoint: generates complete app from description.

    Request body:
        {
            "description": "A recipe manager with ingredients and cooking steps"
        }

    Response:
        {
            "app_id": "recipe_manager_abc123",
            "files": {
                "backend/main.py": "...",
                "frontend/src/App.jsx": "...",
                ...
            },
            "instructions": "Quick start guide",
            "metadata": {...}
        }
    """
    try:
        # Validate input
        description = request.description.strip()

        if len(description) < 10:
            raise HTTPException(
                status_code=400,
                detail="Description too short. Please provide at least 10 characters describing your app."
            )

        if len(description) > 500:
            raise HTTPException(
                status_code=400,
                detail="Description too long. Please keep it under 500 characters."
            )

        print(f"📝 Generating app from description: {description[:50]}...")

        # Generate app using AI + templates
        app = await generator.generate_app(description)

        print(f"✅ Generated app: {app.app_id}")
        print(f"   Files: {len(app.files)}")
        print(f"   Entity: {app.metadata.get('entity_name', 'Unknown')}")

        # Validate generated code
        validation_result = validator.validate_generated_app(app.files)

        if not validation_result.passed:
            print(f"⚠️ Validation failed. Issues found:")
            for error in validation_result.errors:
                print(f"   - {error}")

            # Attempt auto-fix
            print("🔧 Attempting auto-fix...")
            fixed_files = validator.attempt_auto_fix(app.files, validation_result)

            # Re-validate
            revalidation = validator.validate_generated_app(fixed_files)

            if revalidation.passed:
                print("✅ Auto-fix successful!")
                app.files = fixed_files
            else:
                print("⚠️ Auto-fix failed. Using fallback template.")
                # Use fallback
                app = await generator.get_fallback_app(description)

        # Create ZIP file for download
        zip_bytes = create_zip_package(app.files, app.app_id)
        app_storage[app.app_id] = zip_bytes

        print(f"📦 ZIP package created: {len(zip_bytes)} bytes")
        print(f"✨ App generation complete!\n")

        return GenerateResponse(
            app_id=app.app_id,
            files=app.files,
            instructions=app.instructions,
            metadata=app.metadata
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Generation error: {e}")
        # Last resort: return fallback
        try:
            fallback_app = await generator.get_fallback_app(request.description)
            zip_bytes = create_zip_package(fallback_app.files, fallback_app.app_id)
            app_storage[fallback_app.app_id] = zip_bytes

            return GenerateResponse(
                app_id=fallback_app.app_id,
                files=fallback_app.files,
                instructions=fallback_app.instructions,
                metadata=fallback_app.metadata
            )
        except Exception as fallback_error:
            raise HTTPException(
                status_code=500,
                detail=f"Generation failed: {str(e)}. Fallback also failed: {str(fallback_error)}"
            )


@app.get("/api/download/{app_id}")
async def download_app(app_id: str):
    """
    Downloads the generated app as a ZIP file.

    Args:
        app_id: The app identifier from /api/generate

    Returns:
        ZIP file download
    """
    try:
        if app_id not in app_storage:
            raise HTTPException(
                status_code=404,
                detail=f"App '{app_id}' not found. It may have expired or the ID is incorrect."
            )

        zip_bytes = app_storage[app_id]

        return Response(
            content=zip_bytes,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={app_id}.zip"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Download failed: {str(e)}"
        )


@app.get("/api/templates")
async def list_templates():
    """
    Returns available template types with examples.

    Returns:
        List of template information
    """
    return {
        "templates": [
            TemplateInfo(
                type="crud_list_manager",
                name="List Manager",
                examples=[
                    "A todo list app with tasks and due dates",
                    "A recipe manager with ingredients and cooking steps",
                    "A contact manager with names, emails, and phone numbers",
                    "A book tracker with title, author, and reading status",
                    "A workout log with exercises, sets, and reps"
                ],
                description="Apps that manage lists of items with create, read, and delete functionality"
            ).dict()
        ],
        "coming_soon": [
            "calculator",
            "dashboard",
            "form_builder"
        ]
    }


@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "stored_apps": len(app_storage),
        "service": "Zero-Code AI App Builder"
    }


def create_zip_package(files: Dict[str, str], app_id: str) -> bytes:
    """
    Creates a ZIP file from the generated app files.

    Args:
        files: Dict mapping file paths to contents
        app_id: App identifier (used as root folder name)

    Returns:
        ZIP file as bytes
    """
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_path, content in files.items():
            # Add files with app_id as root folder
            full_path = f"{app_id}/{file_path}"
            zip_file.writestr(full_path, content)

    zip_buffer.seek(0)
    return zip_buffer.read()


# Mount frontend static files (for production)
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists() and (frontend_dist / "index.html").exists():
    print(f"✅ Serving frontend from: {frontend_dist}")

    # Mount assets directory
    if (frontend_dist / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")

    # Serve index.html for root and all non-API routes
    @app.get("/", response_class=FileResponse)
    async def serve_frontend_root():
        """Serve the frontend index.html at root"""
        return FileResponse(str(frontend_dist / "index.html"))

    @app.get("/{full_path:path}", response_class=FileResponse)
    async def serve_spa_routes(full_path: str):
        """Serve SPA - all non-API routes go to index.html"""
        # Don't intercept API routes
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")

        # Try to serve the file if it exists
        file_path = frontend_dist / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))

        # Otherwise serve index.html for SPA routing
        return FileResponse(str(frontend_dist / "index.html"))
else:
    print(f"⚠️ Frontend dist not found at: {frontend_dist}")
    print("   API-only mode - frontend not available")

    @app.get("/")
    async def root():
        """Health check when frontend is not available"""
        return {
            "status": "online",
            "service": "Zero-Code AI App Builder API",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "message": "Frontend not built. Run: cd frontend && npm install && npm run build",
            "api_docs": "/docs"
        }

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Zero-Code AI App Builder - Backend Server")
    print("=" * 60)
    print()
    print("📝 Description: Generate full-stack apps from text descriptions")
    print("🌐 Server: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print()
    print("💡 Example usage:")
    print('   POST /api/generate {"description": "A todo list app"}')
    print()
    print("⚠️  Make sure to set OPENROUTER_API_KEY or ANTHROPIC_API_KEY in .env file")
    print()
    print("=" * 60)
    print()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
