"""
TOXO Utilities Module

Utility functions for the TOXO package.
"""

import sys
from typing import Dict, Any, List
from pathlib import Path


def get_version() -> str:
    """Get the current version of TOXO package."""
    return "1.0.0"


def check_dependencies() -> Dict[str, Any]:
    """
    Check if all required dependencies are available.
    
    Returns:
        Dictionary with dependency status
    """
    dependencies = {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "python_compatible": sys.version_info >= (3, 8),
        "required_packages": {},
        "optional_packages": {},
        "status": "unknown"
    }
    
    # Check required packages
    required = [
        ("google.generativeai", "google-generativeai"),
        ("numpy", "numpy"),
        ("requests", "requests"),
        ("tqdm", "tqdm"),
        ("pydantic", "pydantic"),
    ]
    
    for module_name, package_name in required:
        try:
            __import__(module_name)
            dependencies["required_packages"][package_name] = "✅ Available"
        except ImportError:
            dependencies["required_packages"][package_name] = "❌ Missing"
    
    # Check optional packages
    optional = [
        ("chromadb", "chromadb"),
        ("sentence_transformers", "sentence-transformers"),
        ("sklearn", "scikit-learn"),
        ("pandas", "pandas"),
    ]
    
    for module_name, package_name in optional:
        try:
            __import__(module_name)
            dependencies["optional_packages"][package_name] = "✅ Available"
        except ImportError:
            dependencies["optional_packages"][package_name] = "⚪ Optional"
    
    # Determine overall status
    missing_required = [pkg for pkg, status in dependencies["required_packages"].items() 
                       if "Missing" in status]
    
    if not dependencies["python_compatible"]:
        dependencies["status"] = "❌ Python version incompatible (requires 3.8+)"
    elif missing_required:
        dependencies["status"] = f"❌ Missing required packages: {', '.join(missing_required)}"
    else:
        dependencies["status"] = "✅ All requirements satisfied"
    
    return dependencies


def print_dependency_status() -> None:
    """Print a formatted dependency status report."""
    deps = check_dependencies()
    
    print("🔍 TOXO Dependency Check")
    print("=" * 40)
    print(f"Python Version: {deps['python_version']}")
    print(f"Status: {deps['status']}")
    print()
    
    print("📦 Required Packages:")
    for package, status in deps["required_packages"].items():
        print(f"  {package}: {status}")
    
    print()
    print("🔧 Optional Packages:")
    for package, status in deps["optional_packages"].items():
        print(f"  {package}: {status}")


def validate_toxo_file(file_path: str) -> Dict[str, Any]:
    """
    Validate if a file is a proper .toxo file.
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        Dictionary with validation results
    """
    result = {
        "valid": False,
        "errors": [],
        "warnings": [],
        "info": {}
    }
    
    file_path = Path(file_path)
    
    # Check if file exists
    if not file_path.exists():
        result["errors"].append("File does not exist")
        return result
    
    # Check file extension
    if file_path.suffix.lower() != '.toxo':
        result["errors"].append("File must have .toxo extension")
        return result
    
    # Check if it's a valid ZIP file
    try:
        import zipfile
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            
            # Check for required files
            required_files = ["manifest.json"]
            for req_file in required_files:
                if req_file not in file_list:
                    result["errors"].append(f"Missing required file: {req_file}")
            
            # Check for recommended files
            recommended_files = [
                "config/layer_config.json",
                "training/training_data.json",
                "toxo.py"
            ]
            for rec_file in recommended_files:
                if rec_file not in file_list:
                    result["warnings"].append(f"Missing recommended file: {rec_file}")
            
            # Extract basic info
            try:
                manifest_data = zip_ref.read("manifest.json").decode('utf-8')
                import json
                manifest = json.loads(manifest_data)
                
                result["info"] = {
                    "name": manifest.get("package_info", {}).get("name", "Unknown"),
                    "domain": manifest.get("package_info", {}).get("domain", "Unknown"),
                    "version": manifest.get("package_info", {}).get("version", "Unknown"),
                    "created_at": manifest.get("package_info", {}).get("created_at", "Unknown"),
                    "file_count": len(file_list),
                    "file_size": f"{file_path.stat().st_size / 1024:.1f} KB"
                }
            except:
                result["warnings"].append("Could not read manifest information")
            
    except zipfile.BadZipFile:
        result["errors"].append("File is not a valid ZIP archive")
        return result
    except Exception as e:
        result["errors"].append(f"Error reading file: {str(e)}")
        return result
    
    # If no errors, mark as valid
    if not result["errors"]:
        result["valid"] = True
    
    return result


def print_toxo_info(file_path: str) -> None:
    """Print information about a .toxo file."""
    validation = validate_toxo_file(file_path)
    
    print(f"📋 TOXO File Information: {Path(file_path).name}")
    print("=" * 50)
    
    if validation["valid"]:
        print("✅ Valid TOXO file")
        
        info = validation["info"]
        print(f"📛 Name: {info.get('name', 'Unknown')}")
        print(f"🎯 Domain: {info.get('domain', 'Unknown')}")
        print(f"📊 Version: {info.get('version', 'Unknown')}")
        print(f"📅 Created: {info.get('created_at', 'Unknown')}")
        print(f"📁 Files: {info.get('file_count', 0)}")
        print(f"💾 Size: {info.get('file_size', 'Unknown')}")
        
        if validation["warnings"]:
            print("\n⚠️ Warnings:")
            for warning in validation["warnings"]:
                print(f"  • {warning}")
    else:
        print("❌ Invalid TOXO file")
        print("\n🚫 Errors:")
        for error in validation["errors"]:
            print(f"  • {error}")


def get_sample_usage() -> str:
    """Get sample usage code for TOXO."""
    return '''
# TOXO Sample Usage

from toxo import ToxoLayer

# Load your trained model
layer = ToxoLayer.load("your_expert_model.toxo")

# Set your API key
layer.setup_api_key("your_gemini_api_key_here")

# Query your AI expert
response = layer.query("Your question here")
print(response)

# Get model information
info = layer.get_info()
print(f"Domain: {info['domain']}")
print(f"Capabilities: {info['capabilities']}")

# Async usage
import asyncio

async def main():
    response = await layer.query_async("Your async question")
    print(response)

asyncio.run(main())
'''


def get_help_text() -> str:
    """Get help text for TOXO usage."""
    return '''
🧠 TOXO - No-Code LLM Training Platform

Quick Start:
1. Visit https://toxotune.com to create your AI expert
2. Download your .toxo file
3. Install: pip install toxo
4. Use: ToxoLayer.load("your_model.toxo")

Need help?
• Documentation: https://docs.toxotune.com
• Support: support@toxotune.com
• Community: https://community.toxotune.com

Common Commands:
• toxo.check_dependencies() - Check your setup
• toxo.validate_toxo_file("file.toxo") - Validate a .toxo file
• ToxoLayer.load("file.toxo") - Load and use your model
'''
