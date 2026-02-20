#!/usr/bin/env python3
"""
Setup Verification Script for Zero-Code AI App Builder

Checks that all files are present and basic setup is correct.
"""
import os
import sys
from pathlib import Path


def check_file(path, description):
    """Check if a file exists"""
    if os.path.exists(path):
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ MISSING: {description} ({path})")
        return False


def check_directory(path, description):
    """Check if a directory exists"""
    if os.path.isdir(path):
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ MISSING: {description} ({path})")
        return False


def main():
    print("=" * 60)
    print("🔍 Zero-Code AI App Builder - Setup Verification")
    print("=" * 60)
    print()

    all_checks = []

    # Check project root files
    print("📁 Checking project root files...")
    all_checks.append(check_file("README.md", "Main README"))
    all_checks.append(check_file(".gitignore", "Git ignore file"))
    all_checks.append(check_file("SETUP_CHECKLIST.md", "Setup checklist"))
    print()

    # Check backend structure
    print("🐍 Checking backend files...")
    all_checks.append(check_directory("backend", "Backend directory"))
    all_checks.append(check_file("backend/main.py", "Backend server"))
    all_checks.append(check_file("backend/generator.py", "Code generator"))
    all_checks.append(check_file("backend/validator.py", "Code validator"))
    all_checks.append(check_file("backend/models.py", "Pydantic models"))
    all_checks.append(check_file("backend/requirements.txt", "Python dependencies"))
    all_checks.append(check_file("backend/.env.example", "Environment template"))
    print()

    # Check backend templates
    print("📄 Checking backend templates...")
    all_checks.append(check_directory("backend/templates/crud_list_manager", "CRUD template directory"))
    all_checks.append(check_file("backend/templates/crud_list_manager/backend_template.py", "Backend template"))
    all_checks.append(check_file("backend/templates/crud_list_manager/frontend_template.jsx", "Frontend template"))
    all_checks.append(check_file("backend/templates/crud_list_manager/package_template.json", "Package template"))
    all_checks.append(check_file("backend/templates/crud_list_manager/readme_template.md", "README template"))
    all_checks.append(check_file("backend/templates/crud_list_manager/app_css_template.css", "CSS template"))
    print()

    # Check frontend structure
    print("⚛️  Checking frontend files...")
    all_checks.append(check_directory("frontend", "Frontend directory"))
    all_checks.append(check_file("frontend/package.json", "Package.json"))
    all_checks.append(check_file("frontend/vite.config.js", "Vite config"))
    all_checks.append(check_file("frontend/index.html", "Index HTML"))
    all_checks.append(check_directory("frontend/src", "Frontend src directory"))
    all_checks.append(check_file("frontend/src/main.jsx", "Main entry point"))
    all_checks.append(check_file("frontend/src/App.jsx", "Main App component"))
    all_checks.append(check_file("frontend/src/index.css", "Global styles"))
    all_checks.append(check_file("frontend/src/App.css", "App styles"))
    print()

    # Check frontend pages
    print("📄 Checking frontend pages...")
    all_checks.append(check_directory("frontend/src/pages", "Pages directory"))
    all_checks.append(check_file("frontend/src/pages/Builder.jsx", "Builder page"))
    all_checks.append(check_file("frontend/src/pages/Builder.css", "Builder styles"))
    print()

    # Check frontend components
    print("🧩 Checking frontend components...")
    all_checks.append(check_directory("frontend/src/components", "Components directory"))
    all_checks.append(check_file("frontend/src/components/CodeViewer.jsx", "CodeViewer component"))
    all_checks.append(check_file("frontend/src/components/CodeViewer.css", "CodeViewer styles"))
    all_checks.append(check_file("frontend/src/components/DownloadButton.jsx", "DownloadButton component"))
    all_checks.append(check_file("frontend/src/components/DownloadButton.css", "DownloadButton styles"))
    all_checks.append(check_file("frontend/src/components/LoadingSpinner.jsx", "LoadingSpinner component"))
    all_checks.append(check_file("frontend/src/components/LoadingSpinner.css", "LoadingSpinner styles"))
    print()

    # Check .env file
    print("🔐 Checking environment configuration...")
    if os.path.exists("backend/.env"):
        print("✅ .env file exists")
        # Check if API key is set
        with open("backend/.env", "r") as f:
            content = f.read()
            if "ANTHROPIC_API_KEY=" in content and "your_api_key_here" not in content:
                print("✅ API key appears to be set")
                all_checks.append(True)
            else:
                print("⚠️  WARNING: API key not configured in .env")
                print("   Please add your ANTHROPIC_API_KEY to backend/.env")
                all_checks.append(False)
    else:
        print("⚠️  WARNING: .env file not found")
        print("   Copy backend/.env.example to backend/.env and add your API key")
        all_checks.append(False)
    print()

    # Summary
    print("=" * 60)
    passed = sum(all_checks)
    total = len(all_checks)
    percentage = (passed / total) * 100

    print(f"📊 Results: {passed}/{total} checks passed ({percentage:.1f}%)")
    print("=" * 60)
    print()

    if all(all_checks):
        print("🎉 SUCCESS! All files are in place.")
        print()
        print("Next steps:")
        print("1. Ensure ANTHROPIC_API_KEY is set in backend/.env")
        print("2. Start backend: cd backend && python main.py")
        print("3. Start frontend: cd frontend && npm run dev")
        print("4. Visit http://localhost:5173")
        print()
        return 0
    else:
        print("❌ FAILED: Some files are missing.")
        print()
        print("Please ensure all files are created correctly.")
        print("Check the implementation plan and create missing files.")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
