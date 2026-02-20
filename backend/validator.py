"""
Multi-layer validation system to ensure ZERO broken code delivery.

This is critical for bounty-thon compliance - all checks must pass before delivery.
"""
import ast
import re
from typing import Dict, List, Tuple
from models import ValidationResult


class CodeValidator:
    """Validates generated code to ensure it's production-ready"""

    FORBIDDEN_KEYWORDS = [
        "TODO", "FIXME", "PLACEHOLDER", "XXX", "HACK",
        "TEMP", "INCOMPLETE", "WIP"
    ]

    REQUIRED_BACKEND_IMPORTS = [
        "from fastapi import",
        "from fastapi.middleware.cors import",
        "from pydantic import",
        "import uvicorn"
    ]

    def validate_generated_app(self, files: Dict[str, str]) -> ValidationResult:
        """
        Runs all validation checks on generated app files.

        Returns:
            ValidationResult with passed status and detailed check results
        """
        checks = {}
        errors = []

        # Check 1: Python syntax validation
        if 'backend/main.py' in files:
            syntax_valid, syntax_error = self._validate_python_syntax(files['backend/main.py'])
            checks['python_syntax'] = syntax_valid
            if not syntax_valid:
                errors.append(f"Python syntax error: {syntax_error}")
        else:
            checks['python_syntax'] = False
            errors.append("Missing backend/main.py")

        # Check 2: React syntax validation
        if 'frontend/src/App.jsx' in files:
            react_valid, react_error = self._validate_react_syntax(files['frontend/src/App.jsx'])
            checks['react_syntax'] = react_valid
            if not react_valid:
                errors.append(f"React syntax error: {react_error}")
        else:
            checks['react_syntax'] = False
            errors.append("Missing frontend/src/App.jsx")

        # Check 3: No placeholder text
        placeholder_check = self._check_no_placeholders(files)
        checks['no_placeholders'] = placeholder_check
        if not placeholder_check:
            errors.append("Found placeholder text (TODO, FIXME, etc.)")

        # Check 4: Required imports present
        if 'backend/main.py' in files:
            imports_valid = self._check_required_imports(files['backend/main.py'])
            checks['required_imports'] = imports_valid
            if not imports_valid:
                errors.append("Missing required backend imports")
        else:
            checks['required_imports'] = False

        # Check 5: Error handling present
        if 'backend/main.py' in files:
            error_handling = self._check_error_handling(files['backend/main.py'])
            checks['error_handling'] = error_handling
            if not error_handling:
                errors.append("Missing error handling (try/except)")
        else:
            checks['error_handling'] = False

        # Check 6: README completeness
        if 'README.md' in files:
            readme_valid = self._validate_readme(files['README.md'])
            checks['readme_complete'] = readme_valid
            if not readme_valid:
                errors.append("README missing required sections")
        else:
            checks['readme_complete'] = False
            errors.append("Missing README.md")

        # Check 7: React component exports
        if 'frontend/src/App.jsx' in files:
            export_valid = self._check_react_export(files['frontend/src/App.jsx'])
            checks['react_export'] = export_valid
            if not export_valid:
                errors.append("React component missing default export")
        else:
            checks['react_export'] = False

        # Overall result
        passed = all(checks.values())

        return ValidationResult(
            passed=passed,
            checks=checks,
            errors=errors
        )

    def _validate_python_syntax(self, code: str) -> Tuple[bool, str]:
        """
        Validates Python code syntax using AST parsing.

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            ast.parse(code)
            return True, ""
        except SyntaxError as e:
            return False, f"Line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, str(e)

    def _validate_react_syntax(self, code: str) -> Tuple[bool, str]:
        """
        Basic React/JSX validation.

        Checks for:
        - Proper import statements
        - Function component structure
        - Return statement
        """
        try:
            # Check for React import
            if 'import React' not in code and "import {" not in code:
                return False, "Missing React import"

            # Check for function component
            if 'function App' not in code and 'const App' not in code:
                return False, "No App component found"

            # Check for return statement
            if 'return (' not in code and 'return(' not in code:
                return False, "No JSX return statement found"

            # Check for balanced JSX tags (basic check)
            open_tags = code.count('<div')
            close_tags = code.count('</div>')
            if abs(open_tags - close_tags) > 2:  # Allow some tolerance
                return False, "Unbalanced JSX tags detected"

            return True, ""
        except Exception as e:
            return False, str(e)

    def _check_no_placeholders(self, files: Dict[str, str]) -> bool:
        """
        Checks that no placeholder text exists in any file.

        Returns:
            True if no placeholders found, False otherwise
        """
        for file_content in files.values():
            for keyword in self.FORBIDDEN_KEYWORDS:
                if keyword in file_content.upper():
                    return False
        return True

    def _check_required_imports(self, backend_code: str) -> bool:
        """
        Verifies all required imports are present in backend code.

        Returns:
            True if all required imports found, False otherwise
        """
        for required_import in self.REQUIRED_BACKEND_IMPORTS:
            if required_import not in backend_code:
                return False
        return True

    def _check_error_handling(self, backend_code: str) -> bool:
        """
        Checks that error handling is present (try/except blocks).

        Returns:
            True if error handling found, False otherwise
        """
        # For templates, error handling might be in the API endpoints
        # At minimum, check for HTTPException usage
        has_http_exception = 'HTTPException' in backend_code
        has_try_except = 'try:' in backend_code and 'except' in backend_code

        return has_http_exception or has_try_except

    def _validate_readme(self, readme_content: str) -> bool:
        """
        Validates README has required sections.

        Returns:
            True if README is complete, False otherwise
        """
        required_sections = [
            'Prerequisites',
            'Backend Setup',
            'Frontend Setup',
            'npm install',
            'python main.py'
        ]

        for section in required_sections:
            if section not in readme_content:
                return False

        return True

    def _check_react_export(self, react_code: str) -> bool:
        """
        Checks that React component has default export.

        Returns:
            True if export found, False otherwise
        """
        return 'export default' in react_code

    def attempt_auto_fix(self, files: Dict[str, str], validation_result: ValidationResult) -> Dict[str, str]:
        """
        Attempts to automatically fix common issues.

        Args:
            files: Original files
            validation_result: Result from validation

        Returns:
            Fixed files (or original if auto-fix not possible)
        """
        fixed_files = files.copy()

        # Auto-fix 1: Add missing React export
        if not validation_result.checks.get('react_export', True):
            if 'frontend/src/App.jsx' in fixed_files:
                react_code = fixed_files['frontend/src/App.jsx']
                if 'export default App' not in react_code:
                    # Add export at the end
                    react_code = react_code.rstrip() + '\n\nexport default App;\n'
                    fixed_files['frontend/src/App.jsx'] = react_code

        # Auto-fix 2: Add missing imports (if template structure intact)
        if not validation_result.checks.get('required_imports', True):
            if 'backend/main.py' in fixed_files:
                backend_code = fixed_files['backend/main.py']
                # Add missing FastAPI imports if not present
                if 'from fastapi import' not in backend_code:
                    backend_code = 'from fastapi import FastAPI, HTTPException\n' + backend_code
                    fixed_files['backend/main.py'] = backend_code

        return fixed_files


# Singleton instance
validator = CodeValidator()
