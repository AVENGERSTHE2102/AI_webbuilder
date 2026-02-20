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
        # OpenRouter API only
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.api_base = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "anthropic/claude-sonnet-4-20250514"
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
            # Check API key first
            if not self.api_key:
                print("❌ ERROR: OPENROUTER_API_KEY not configured!")
                print("   Set it in Render Dashboard: https://dashboard.render.com")
                print("   Get free $5 credits at: https://openrouter.ai/")
                raise ValueError("OPENROUTER_API_KEY not set - cannot generate custom code")

            print(f"✅ API Key found: {self.api_key[:8]}...")

            # Step 1: Extract app specification from description
            print("📋 Step 1: Extracting app specification...")
            spec = await self.extract_app_specification(description)
            print(f"   Entity: {spec.entity_name}, Fields: {len(spec.fields)}")

            # Step 2: Load appropriate template
            print("📁 Step 2: Loading template...")
            template_files = self.load_template(spec.app_type)

            # Step 3: Generate code blocks with AI
            print("🤖 Step 3: Generating custom code blocks...")
            code_blocks = await self.generate_code_blocks(spec)

            # Step 4: Inject code blocks into template
            print("💉 Step 4: Injecting code into template...")
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
        prompt = f"""You are an expert at analyzing app descriptions and extracting detailed specifications.

User wants to build: "{description}"

Analyze this description and extract the core entity, fields, and requirements. Be specific and thoughtful about what fields make sense for this app.

Output ONLY valid JSON (no markdown, no explanation):
{{
  "entity_name": "Recipe",
  "entity_name_lower": "recipe",
  "app_type": "crud_list_manager",
  "description": "Recipe manager with ingredients and cooking steps",
  "fields": [
    {{"name": "title", "type": "str", "required": true, "placeholder": "Recipe name"}},
    {{"name": "description", "type": "str", "required": false, "placeholder": "Brief description"}},
    {{"name": "ingredients", "type": "List[str]", "required": true, "placeholder": "Ingredients (one per line)"}},
    {{"name": "instructions", "type": "List[str]", "required": true, "placeholder": "Cooking steps"}},
    {{"name": "prepTime", "type": "str", "required": false, "placeholder": "Prep time"}},
    {{"name": "cookTime", "type": "str", "required": false, "placeholder": "Cook time"}}
  ]
}}

Requirements:
- entity_name: Singular noun from the description (Recipe, Todo, Contact, Book, etc.)
- fields: Extract 3-8 relevant fields based on what makes sense for this type of app
- field types: str, int, float, bool, List[str]
- Think about what fields are essential vs optional for this app type
- Make placeholders helpful and specific
- app_type: "crud_list_manager"

Output ONLY the JSON."""

        try:
            response = await self._call_claude_api(prompt)
            print(f"   AI Response: {response[:200]}...")
            # Extract JSON from response
            pattern = r'\{.*\}'
            json_match = re.search(pattern, response, re.DOTALL)
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
                print(f"   ✅ Extracted spec for: {spec.entity_name}")
                return spec
            else:
                raise ValueError("No JSON found in AI response")

        except Exception as e:
            print(f"❌ Failed to extract spec: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            print("⚠️ Using generic fallback spec.")
            # Fallback to generic item manager
            return self._get_generic_spec(description)

    async def generate_code_blocks(self, spec: AppSpecification) -> CodeBlocks:
        """
        Uses AI to generate complete, customized code for the app.

        Args:
            spec: App specification

        Returns:
            CodeBlocks with Pydantic model, endpoints, React components
        """
        # Build detailed field descriptions
        fields_desc = "\n".join([
            f"- {f.name}: {f.type} ({'required' if f.required else 'optional'}) - placeholder: '{f.placeholder}'"
            for f in spec.fields
        ])

        prompt = f"""You are an expert full-stack developer. Generate production-ready code for a {spec.entity_name} management application.

App Description: {spec.description}

Entity: {spec.entity_name}
Fields:
{fields_desc}

Generate complete, customized code. Output ONLY valid JSON (no markdown):
{{
  "pydantic_model": "complete Pydantic model code",
  "api_endpoints": "complete FastAPI endpoint code",
  "react_form_fields": "complete JSX form code",
  "react_list_item": "complete JSX display code"
}}

PYDANTIC MODEL - Generate this EXACT structure:
```python
class {spec.entity_name}(BaseModel):
    id: Optional[int] = None
    # Add all fields with proper types
    # Include Field() validators where appropriate
```

API ENDPOINTS - Generate COMPLETE working endpoints:
```python
@app.get("/{spec.entity_name_lower}")
async def get_all_{spec.entity_name_lower}s():
    return {spec.entity_name_lower}_store

@app.post("/{spec.entity_name_lower}")
async def create_{spec.entity_name_lower}(item: {spec.entity_name}):
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
    for item in {spec.entity_name_lower}_store:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="{spec.entity_name} not found")

@app.delete("/{spec.entity_name_lower}/{{item_id}}")
async def delete_{spec.entity_name_lower}(item_id: int):
    global {spec.entity_name_lower}_store
    {spec.entity_name_lower}_store = [item for item in {spec.entity_name_lower}_store if item.id != item_id]
    return {{"message": "{spec.entity_name} deleted successfully"}}
```

REACT FORM FIELDS - Generate beautiful, functional form inputs:
- Use proper input types (text, number, textarea, etc.)
- Include all fields with their specific placeholders
- Proper labels with capitalized names
- Use formData state and handleInputChange
- Make List[str] fields use textarea with instructions

REACT LIST ITEM - Generate attractive card display:
- Show all important fields
- Use proper formatting for different data types
- List[str] fields should map to <ul><li> elements
- Include visual hierarchy (title bigger, metadata smaller)
- Add icons or emojis where appropriate

IMPORTANT:
- NO placeholder comments like "// Add fields here"
- Generate COMPLETE working code
- Make it specific to {spec.entity_name}, not generic
- All fields should be properly implemented
- Code should be production-ready

Output ONLY the JSON with these 4 code blocks.
"""

        try:
            response = await self._call_claude_api(prompt)
            # Extract JSON
            pattern = r'\{.*\}'
            json_match = re.search(pattern, response, re.DOTALL)
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
        """Generates custom code blocks based on specification"""
        # Build Pydantic model with proper field definitions
        model_fields = ["    id: Optional[int] = None"]
        for field in spec.fields:
            # Add field descriptions for better API docs
            field_desc = f' description="{field.placeholder}"' if field.placeholder else ''
            if field.required:
                if field.type.startswith("List"):
                    model_fields.append(f"    {field.name}: {field.type} = Field(default_factory=list,{field_desc})")
                else:
                    model_fields.append(f"    {field.name}: {field.type} = Field(...,{field_desc})")
            else:
                if field.type.startswith("List"):
                    model_fields.append(f"    {field.name}: Optional[{field.type}] = Field(default_factory=list,{field_desc})")
                else:
                    model_fields.append(f"    {field.name}: Optional[{field.type}] = Field(None,{field_desc})")

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

        # Build React form fields with proper input types
        form_fields = []
        for field in spec.fields:
            label = field.name.replace('_', ' ').replace('Time', ' Time').replace('Date', ' Date').title()

            if field.type == "int":
                form_fields.append(f"""            <div className="form-group">
              <label htmlFor="{field.name}">{label}</label>
              <input
                type="number"
                id="{field.name}"
                name="{field.name}"
                value={{formData.{field.name}}}
                onChange={{handleInputChange}}
                placeholder="{field.placeholder or label}"
                required={{{str(field.required).lower()}}}
              />
            </div>""")
            elif field.type == "float":
                form_fields.append(f"""            <div className="form-group">
              <label htmlFor="{field.name}">{label}</label>
              <input
                type="number"
                step="0.01"
                id="{field.name}"
                name="{field.name}"
                value={{formData.{field.name}}}
                onChange={{handleInputChange}}
                placeholder="{field.placeholder or label}"
                required={{{str(field.required).lower()}}}
              />
            </div>""")
            elif field.type == "bool":
                form_fields.append(f"""            <div className="form-group">
              <label htmlFor="{field.name}">
                <input
                  type="checkbox"
                  id="{field.name}"
                  name="{field.name}"
                  checked={{formData.{field.name}}}
                  onChange={{handleInputChange}}
                />
                {label}
              </label>
            </div>""")
            elif field.type in ["List[str]", "list"]:
                form_fields.append(f"""            <div className="form-group">
              <label htmlFor="{field.name}">{label}</label>
              <textarea
                id="{field.name}"
                name="{field.name}"
                value={{formData.{field.name}}}
                onChange={{handleInputChange}}
                placeholder="{field.placeholder or 'Enter ' + label.lower() + ' (one per line)'}"
                rows="4"
                required={{{str(field.required).lower()}}}
              />
              <small>Enter each item on a new line</small>
            </div>""")
            elif 'name' in field.name.lower() or 'title' in field.name.lower():
                # Make name/title fields larger
                form_fields.append(f"""            <div className="form-group">
              <label htmlFor="{field.name}">{label}</label>
              <input
                type="text"
                id="{field.name}"
                name="{field.name}"
                value={{formData.{field.name}}}
                onChange={{handleInputChange}}
                placeholder="{field.placeholder or label}"
                required={{{str(field.required).lower()}}}
                className="input-large"
              />
            </div>""")
            elif 'description' in field.name.lower() or 'notes' in field.name.lower():
                # Make description fields textarea
                form_fields.append(f"""            <div className="form-group">
              <label htmlFor="{field.name}">{label}</label>
              <textarea
                id="{field.name}"
                name="{field.name}"
                value={{formData.{field.name}}}
                onChange={{handleInputChange}}
                placeholder="{field.placeholder or label}"
                rows="3"
                required={{{str(field.required).lower()}}}
              />
            </div>""")
            else:
                # Default text input
                form_fields.append(f"""            <div className="form-group">
              <label htmlFor="{field.name}">{label}</label>
              <input
                type="text"
                id="{field.name}"
                name="{field.name}"
                value={{formData.{field.name}}}
                onChange={{handleInputChange}}
                placeholder="{field.placeholder or label}"
                required={{{str(field.required).lower()}}}
              />
            </div>""")

        react_form_fields = "\n".join(form_fields)

        # Build React list item display with smart formatting
        # Find the title field (name, title, or first string field)
        title_field = next((f for f in spec.fields if 'name' in f.name.lower() or 'title' in f.name.lower()), spec.fields[0] if spec.fields else None)

        list_item_content = []
        if title_field:
            list_item_content.append(f"<h3>{{item.{title_field.name} || '{spec.entity_name} #' + item.id}}</h3>")

        for field in spec.fields:
            if field == title_field:
                continue  # Already used as title

            label = field.name.replace('_', ' ').replace('Time', ' Time').replace('Date', ' Date').title()

            if field.type in ["List[str]", "list"]:
                # Build this without f-string to avoid backslash issues
                field_code = """                <div className="field-section">
                  <strong>{label}:</strong>
                  <ul className="field-list">
                    {{{{item.{field_name} && item.{field_name}.split('\\n').filter(line => line.trim()).map((line, i) => (
                      <li key={{{{i}}}}>{{{{line}}}}</li>
                    ))}}}}
                  </ul>
                </div>""".format(label=label, field_name=field.name)
                list_item_content.append(field_code)
            elif field.type == "bool":
                list_item_content.append(f"""                <div className="field-section">
                  <strong>{label}:</strong> {{item.{field.name} ? '✅ Yes' : '❌ No'}}
                </div>""")
            elif 'description' in field.name.lower() or 'notes' in field.name.lower():
                list_item_content.append(f"""                <div className="field-section">
                  <strong>{label}:</strong>
                  <p className="description-text">{{item.{field.name}}}</p>
                </div>""")
            elif field.type in ["int", "float"]:
                list_item_content.append(f"""                <div className="field-section">
                  <span className="field-label">{label}:</span>
                  <span className="field-value">{{item.{field.name}}}</span>
                </div>""")
            else:
                list_item_content.append(f"""                <div className="field-section">
                  <span className="field-label">{label}:</span>
                  <span className="field-value">{{item.{field.name}}}</span>
                </div>""")

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
        Calls Claude API via OpenRouter.

        Args:
            prompt: The prompt to send

        Returns:
            AI response text
        """
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not set in environment. Get free $5 credits at https://openrouter.ai/")

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # OpenRouter API (OpenAI-compatible format)
                response = await client.post(
                    self.api_base,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "HTTP-Referer": "https://github.com/AVENGERSTHE2102/AI_webbuilder",
                        "X-Title": "Zero-Code AI App Builder",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 4096,
                        "temperature": 0.7
                    }
                )

                # Check for errors
                if response.status_code != 200:
                    error_text = response.text
                    print(f"❌ OpenRouter API Error ({response.status_code}): {error_text}")
                    raise ValueError(f"API returned {response.status_code}: {error_text}")

                result = response.json()

                # Check for error in response
                if 'error' in result:
                    print(f"❌ OpenRouter API Error: {result['error']}")
                    raise ValueError(f"API Error: {result['error']}")

                return result['choices'][0]['message']['content']

        except httpx.HTTPError as e:
            print(f"❌ HTTP Error calling OpenRouter: {type(e).__name__}: {str(e)}")
            raise
        except Exception as e:
            print(f"❌ Error calling OpenRouter API: {type(e).__name__}: {str(e)}")
            raise


# Singleton instance
generator = AppGenerator()
