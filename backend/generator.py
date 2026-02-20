"""
Core AI code generation engine for Zero-Code App Builder.

Uses template-based generation with AI customization for stability.
"""
import os
import json
import httpx
import uuid
import re
from typing import Dict, Optional
from dotenv import load_dotenv
from models import AppSpecification, FieldSpec, GeneratedApp, CodeBlocks

load_dotenv()


class AppGenerator:
    """AI-powered code generation with template injection"""

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.api_base = "https://api.anthropic.com/v1/messages"
        self.model = "claude-sonnet-4-5-20250929"
        self.templates_dir = os.path.join(os.path.dirname(__file__), "templates")

    async def generate_app(self, description: str) -> GeneratedApp:
        """
        Main entry point: user description → complete app code

        Args:
            description: User's app description

        Returns:
            GeneratedApp with all files ready for download
        """
        try:
            # Step 1: Extract app specification from description
            spec = await self.extract_app_specification(description)

            # Step 2: Load appropriate template
            template_files = self.load_template(spec.app_type)

            # Step 3: Generate code blocks with AI
            code_blocks = await self.generate_code_blocks(spec)

            # Step 4: Inject code blocks into template
            files = self.inject_into_template(template_files, spec, code_blocks)

            # Step 5: Create app ID and package
            app_id = f"{spec.entity_name_lower}_manager_{uuid.uuid4().hex[:8]}"

            # Step 6: Generate instructions
            instructions = self._generate_instructions(spec)

            return GeneratedApp(
                app_id=app_id,
                files=files,
                instructions=instructions,
                metadata={
                    "entity_name": spec.entity_name,
                    "app_type": spec.app_type,
                    "field_count": len(spec.fields),
                    "description": spec.description
                }
            )

        except Exception as e:
            print(f"⚠️ Generation failed: {e}. Using fallback template.")
            # Fallback to generic template
            return await self.get_fallback_app(description)

    async def extract_app_specification(self, description: str) -> AppSpecification:
        """
        Uses AI to extract structured parameters from user description.

        Args:
            description: User's app description

        Returns:
            AppSpecification with entity name, fields, app type
        """
        prompt = f"""You are analyzing an app description to extract structured parameters.

Description: "{description}"

Extract and output ONLY valid JSON (no other text):
{{
  "entity_name": "Recipe",
  "entity_name_lower": "recipe",
  "app_type": "crud_list_manager",
  "description": "Recipe manager app",
  "fields": [
    {{"name": "name", "type": "str", "required": true, "placeholder": "Recipe name"}},
    {{"name": "ingredients", "type": "List[str]", "required": true, "placeholder": "One per line"}},
    {{"name": "steps", "type": "List[str]", "required": true, "placeholder": "Cooking steps"}}
  ]
}}

Rules:
- entity_name: Capitalized singular noun (e.g., "Recipe", "Todo", "Contact")
- entity_name_lower: Lowercase version for variables
- app_type: Must be "crud_list_manager" (only supported type for now)
- fields: 2-6 fields maximum
- field types: "str", "int", "float", "bool", "List[str]"
- If unclear, use generic "Item" as entity_name

Output ONLY the JSON, nothing else."""

        try:
            response = await self._call_claude_api(prompt)
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                spec_data = json.loads(json_match.group())
                # Convert to AppSpecification
                fields = [FieldSpec(**f) for f in spec_data.get('fields', [])]
                spec = AppSpecification(
                    entity_name=spec_data['entity_name'],
                    entity_name_lower=spec_data['entity_name_lower'],
                    app_type=spec_data.get('app_type', 'crud_list_manager'),
                    description=spec_data.get('description', description),
                    fields=fields
                )
                return spec
            else:
                raise ValueError("No JSON found in AI response")

        except Exception as e:
            print(f"⚠️ Failed to extract spec: {e}. Using generic spec.")
            # Fallback to generic item manager
            return self._get_generic_spec(description)

    async def generate_code_blocks(self, spec: AppSpecification) -> CodeBlocks:
        """
        Uses AI to generate specific code blocks for the app.

        Args:
            spec: App specification

        Returns:
            CodeBlocks with Pydantic model, endpoints, React components
        """
        # Build field descriptions for prompt
        fields_desc = "\n".join([
            f"- {f.name}: {f.type} ({'required' if f.required else 'optional'})"
            for f in spec.fields
        ])

        prompt = f"""Generate Python and React code blocks for a {spec.entity_name} manager app.

Entity: {spec.entity_name}
Fields:
{fields_desc}

Generate ONLY valid JSON:
{{
  "pydantic_model": "class {spec.entity_name}(BaseModel):\\n    id: Optional[int] = None\\n    ...",
  "api_endpoints": "# CRUD endpoints code here",
  "react_form_fields": "{{/* JSX form fields */}}",
  "react_list_item": "{{/* JSX for displaying one item */}}"
}}

Requirements for pydantic_model:
- Include all fields from spec
- id field is Optional[int] = None
- Use proper Python types (str, int, List[str], etc.)
- No TODO or placeholder comments

Requirements for api_endpoints:
- GET /{spec.entity_name_lower} - return {spec.entity_name_lower}_store
- POST /{spec.entity_name_lower} - add to store with next_id
- GET /{spec.entity_name_lower}/{{id}} - return single item
- DELETE /{spec.entity_name_lower}/{{id}} - remove from store
- Include try-except with HTTPException
- Use global next_id variable

Requirements for react_form_fields:
- One input/textarea per field (except id)
- Use formData state and handleInputChange
- Include labels and placeholders
- Wrap in div.form-group

Requirements for react_list_item:
- Display all fields of the item
- Use proper JSX syntax
- Include item.id as key

Output ONLY the JSON."""

        try:
            response = await self._call_claude_api(prompt)
            # Extract JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                blocks_data = json.loads(json_match.group())
                return CodeBlocks(**blocks_data)
            else:
                raise ValueError("No JSON in response")

        except Exception as e:
            print(f"⚠️ Failed to generate code blocks: {e}. Using template defaults.")
            return self._get_default_code_blocks(spec)

    def load_template(self, app_type: str) -> Dict[str, str]:
        """
        Loads pre-tested template files for the specified app type.

        Args:
            app_type: Type of app (crud_list_manager, etc.)

        Returns:
            Dict mapping file paths to template content
        """
        template_dir = os.path.join(self.templates_dir, app_type)

        templates = {}
        template_files = {
            'backend_template.py': 'backend/main.py',
            'frontend_template.jsx': 'frontend/src/App.jsx',
            'package_template.json': 'frontend/package.json',
            'readme_template.md': 'README.md',
            'app_css_template.css': 'frontend/src/App.css'
        }

        for template_file, target_path in template_files.items():
            file_path = os.path.join(template_dir, template_file)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    templates[target_path] = f.read()

        # Add additional required files
        templates['frontend/index.html'] = self._get_index_html_template()
        templates['frontend/src/main.jsx'] = self._get_main_jsx_template()
        templates['frontend/vite.config.js'] = self._get_vite_config_template()
        templates['backend/requirements.txt'] = self._get_requirements_txt()

        return templates

    def inject_into_template(
        self,
        template_files: Dict[str, str],
        spec: AppSpecification,
        code_blocks: CodeBlocks
    ) -> Dict[str, str]:
        """
        Replaces template variables with actual code.

        Args:
            template_files: Template file contents
            spec: App specification
            code_blocks: AI-generated code blocks

        Returns:
            Complete files ready for delivery
        """
        files = {}

        # Build initial form state for React
        form_state = self._build_form_state(spec.fields)

        # Replacement mapping
        replacements = {
            '{ENTITY_NAME}': spec.entity_name,
            '{ENTITY_NAME_LOWER}': spec.entity_name_lower,
            '{DESCRIPTION}': spec.description,
            '{PYDANTIC_MODEL_CODE}': code_blocks.pydantic_model,
            '{API_ENDPOINTS_CODE}': code_blocks.api_endpoints,
            '{FORM_FIELDS}': code_blocks.react_form_fields,
            '{LIST_ITEM_CONTENT}': code_blocks.react_list_item,
            '{INITIAL_FORM_STATE}': form_state
        }

        # Apply replacements to each file
        for file_path, content in template_files.items():
            modified_content = content
            for placeholder, value in replacements.items():
                modified_content = modified_content.replace(placeholder, value)
            files[file_path] = modified_content

        return files

    async def get_fallback_app(self, description: str = "") -> GeneratedApp:
        """
        Returns a pre-tested, guaranteed-working generic Item Manager app.

        Used when AI generation fails or validation fails.

        Returns:
            GeneratedApp with generic item manager
        """
        generic_spec = self._get_generic_spec(description or "Generic item manager")
        template_files = self.load_template("crud_list_manager")
        code_blocks = self._get_default_code_blocks(generic_spec)
        files = self.inject_into_template(template_files, generic_spec, code_blocks)

        app_id = f"item_manager_{uuid.uuid4().hex[:8]}"

        return GeneratedApp(
            app_id=app_id,
            files=files,
            instructions=self._generate_instructions(generic_spec),
            metadata={
                "entity_name": "Item",
                "app_type": "crud_list_manager",
                "field_count": 3,
                "description": "Generic item manager (fallback)",
                "fallback": True
            }
        )

    def _get_generic_spec(self, description: str) -> AppSpecification:
        """Returns a generic Item specification"""
        return AppSpecification(
            entity_name="Item",
            entity_name_lower="item",
            app_type="crud_list_manager",
            description=description or "Generic item manager",
            fields=[
                FieldSpec(name="name", type="str", required=True, placeholder="Item name"),
                FieldSpec(name="description", type="str", required=True, placeholder="Description"),
                FieldSpec(name="category", type="str", required=False, placeholder="Category")
            ]
        )

    def _get_default_code_blocks(self, spec: AppSpecification) -> CodeBlocks:
        """Generates default code blocks without AI"""
        # Build Pydantic model
        model_fields = ["    id: Optional[int] = None"]
        for field in spec.fields:
            if field.required:
                model_fields.append(f"    {field.name}: {field.type}")
            else:
                model_fields.append(f"    {field.name}: Optional[{field.type}] = None")

        pydantic_model = f"class {spec.entity_name}(BaseModel):\n" + "\n".join(model_fields)

        # Build API endpoints
        api_endpoints = f"""
@app.get("/{spec.entity_name_lower}")
async def get_all_{spec.entity_name_lower}s():
    \"\"\"Get all {spec.entity_name_lower}s\"\"\"
    return {spec.entity_name_lower}_store

@app.post("/{spec.entity_name_lower}")
async def create_{spec.entity_name_lower}(item: {spec.entity_name}):
    \"\"\"Create a new {spec.entity_name_lower}\"\"\"
    global next_id
    try:
        item.id = next_id
        next_id += 1
        {spec.entity_name_lower}_store.append(item)
        return item
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/{spec.entity_name_lower}/{{item_id}}")
async def get_{spec.entity_name_lower}(item_id: int):
    \"\"\"Get a single {spec.entity_name_lower}\"\"\"
    for item in {spec.entity_name_lower}_store:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="{spec.entity_name} not found")

@app.delete("/{spec.entity_name_lower}/{{item_id}}")
async def delete_{spec.entity_name_lower}(item_id: int):
    \"\"\"Delete a {spec.entity_name_lower}\"\"\"
    global {spec.entity_name_lower}_store
    {spec.entity_name_lower}_store = [item for item in {spec.entity_name_lower}_store if item.id != item_id]
    return {{"message": "{spec.entity_name} deleted successfully"}}
"""

        # Build React form fields
        form_fields = []
        for field in spec.fields:
            if field.type == "str":
                form_fields.append(f"""            <div className="form-group">
              <label htmlFor="{field.name}">{field.name.replace('_', ' ').title()}</label>
              <input
                type="text"
                id="{field.name}"
                name="{field.name}"
                value={{formData.{field.name}}}
                onChange={{handleInputChange}}
                placeholder="{field.placeholder or field.name}"
                required={{{str(field.required).lower()}}}
              />
            </div>""")
            elif field.type in ["List[str]", "list"]:
                form_fields.append(f"""            <div className="form-group">
              <label htmlFor="{field.name}">{field.name.replace('_', ' ').title()}</label>
              <textarea
                id="{field.name}"
                name="{field.name}"
                value={{formData.{field.name}}}
                onChange={{handleInputChange}}
                placeholder="{field.placeholder or field.name + ' (one per line)'}"
                required={{{str(field.required).lower()}}}
              />
            </div>""")

        react_form_fields = "\n".join(form_fields)

        # Build React list item display
        list_item_content = [f"<h3>{{item.name || 'Item #' + item.id}}</h3>"]
        for field in spec.fields:
            if field.name != "name":
                if field.type in ["List[str]", "list"]:
                    list_item_content.append(f"""                <div>
                  <strong>{field.name.replace('_', ' ').title()}:</strong>
                  <ul>
                    {{item.{field.name} && item.{field.name}.split('\\n').map((line, i) => (
                      <li key={{i}}>{{line}}</li>
                    ))}}
                  </ul>
                </div>""")
                else:
                    list_item_content.append(f"<p><strong>{field.name.replace('_', ' ').title()}:</strong> {{item.{field.name}}}</p>")

        react_list_item = "\n".join(list_item_content)

        return CodeBlocks(
            pydantic_model=pydantic_model,
            api_endpoints=api_endpoints,
            react_form_fields=react_form_fields,
            react_list_item=react_list_item
        )

    def _build_form_state(self, fields: list) -> str:
        """Builds initial form state object for React"""
        state_fields = [f"{field.name}: ''" for field in fields]
        return "{ " + ", ".join(state_fields) + " }"

    def _generate_instructions(self, spec: AppSpecification) -> str:
        """Generates run instructions for the generated app"""
        return f"""🚀 Quick Start Instructions:

1. Extract the ZIP file
2. Open TWO terminal windows

Terminal 1 (Backend):
  cd backend
  pip install -r requirements.txt
  python main.py

Terminal 2 (Frontend):
  cd frontend
  npm install
  npm run dev

3. Open http://localhost:5173 in your browser
4. Start adding {spec.entity_name_lower}s!

Your {spec.entity_name} Manager is ready to use! 🎉"""

    def _get_index_html_template(self) -> str:
        """Returns index.html template"""
        return """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>App Manager</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>"""

    def _get_main_jsx_template(self) -> str:
        """Returns main.jsx template"""
        return """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)"""

    def _get_vite_config_template(self) -> str:
        """Returns vite.config.js template"""
        return """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
})"""

    def _get_requirements_txt(self) -> str:
        """Returns requirements.txt"""
        return """fastapi==0.115.0
uvicorn[standard]==0.30.6
pydantic==2.6.4"""

    async def _call_claude_api(self, prompt: str) -> str:
        """
        Calls Claude API with the given prompt.

        Args:
            prompt: The prompt to send

        Returns:
            AI response text
        """
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in environment")

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.api_base,
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": self.model,
                    "max_tokens": 4096,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
            )
            response.raise_for_status()
            result = response.json()
            return result['content'][0]['text']


# Singleton instance
generator = AppGenerator()
