"""
Pydantic models for Zero-Code AI App Builder API
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any


class GenerateRequest(BaseModel):
    """Request model for app generation"""
    description: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="User's app description"
    )


class FieldSpec(BaseModel):
    """Specification for a single field in the generated model"""
    name: str
    type: str  # str, int, float, bool, List[str], etc.
    required: bool = True
    placeholder: str = ""


class AppSpecification(BaseModel):
    """Extracted app specification from user description"""
    entity_name: str  # "Recipe", "Todo", "Contact"
    entity_name_lower: str  # "recipe", "todo", "contact"
    app_type: str  # crud_list_manager, calculator, dashboard
    description: str
    fields: List[FieldSpec]


class CodeBlocks(BaseModel):
    """AI-generated code blocks to inject into templates"""
    pydantic_model: str
    api_endpoints: str
    react_form_fields: str
    react_list_item: str


class ValidationResult(BaseModel):
    """Result of code validation checks"""
    passed: bool
    checks: Dict[str, bool]
    errors: List[str] = []


class GeneratedApp(BaseModel):
    """Complete generated application"""
    app_id: str
    files: Dict[str, str]  # file_path: content
    instructions: str
    metadata: Dict[str, Any]


class GenerateResponse(BaseModel):
    """Response from generate endpoint"""
    app_id: str
    files: Dict[str, str]
    instructions: str
    metadata: Dict[str, Any]


class TemplateInfo(BaseModel):
    """Information about an available template"""
    type: str
    name: str
    examples: List[str]
    description: str
