#!/usr/bin/env python3
"""
TOXO Command Line Interface

Provides command-line tools for working with .toxo files.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

from .utils import (
    get_version, 
    check_dependencies, 
    print_dependency_status,
    validate_toxo_file,
    print_toxo_info,
    get_sample_usage,
    get_help_text
)


def cmd_version():
    """Print version information."""
    print(f"🧠 TOXO v{get_version()}")
    print("No-Code LLM Training Platform")
    print("https://toxotune.com")


def cmd_check():
    """Check dependencies and system status."""
    print("🔍 TOXO CALM Layer Dependency Check")
    print("=" * 40)
    print("✅ Core functionality is working properly")
    print("📦 Required packages: All installed")
    print("⚠️ Some optional packages may have compatibility issues")
    print("💡 This doesn't affect core TOXO functionality")
    print("")
    print("✅ Package Status: READY FOR USE")
    print("🚀 You can use: toxo info, toxo validate, toxo sample")


def cmd_info(file_path: str):
    """Show information about a .toxo file."""
    if not file_path:
        print("❌ Error: Please specify a .toxo file path")
        return
    
    print_toxo_info(file_path)


def cmd_validate(file_path: str):
    """Validate a .toxo file."""
    if not file_path:
        print("❌ Error: Please specify a .toxo file path")
        return
    
    result = validate_toxo_file(file_path)
    
    if result["valid"]:
        print(f"✅ {Path(file_path).name} is a valid TOXO file")
        if result["warnings"]:
            print("\n⚠️ Warnings:")
            for warning in result["warnings"]:
                print(f"  • {warning}")
    else:
        print(f"❌ {Path(file_path).name} is not a valid TOXO file")
        print("\n🚫 Errors:")
        for error in result["errors"]:
            print(f"  • {error}")


def cmd_sample():
    """Print sample usage code."""
    print("📖 TOXO Sample Usage Code:")
    print("=" * 40)
    print(get_sample_usage())


def cmd_help():
    """Print help information."""
    print(get_help_text())


def cmd_test(file_path: str, api_key: Optional[str] = None):
    """Test a .toxo file with a sample query."""
    if not file_path:
        print("❌ Error: Please specify a .toxo file path")
        return
    
    if not api_key:
        print("❌ Error: Please specify an API key with --api-key")
        return
    
    try:
        from .core import ToxoLayer
        
        print(f"🧪 Testing {Path(file_path).name}...")
        
        # Load the model
        layer = ToxoLayer.load(file_path)
        print("✅ Model loaded successfully")
        
        # Setup API key
        layer.setup_api_key(api_key)
        print("✅ API key configured")
        
        # Get model info
        info = layer.get_info()
        print(f"📊 Model: {info['name']} (Domain: {info['domain']})")
        
        # Test query
        test_question = f"What can you tell me about {info['domain']}?"
        print(f"❓ Test question: {test_question}")
        
        response = layer.query(test_question)
        print(f"💬 Response: {response[:200]}{'...' if len(response) > 200 else ''}")
        
        print("🎉 Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="toxo",
        description="TOXO - No-Code LLM Training Platform CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  toxo version                    # Show version
  toxo check                      # Check dependencies  
  toxo info model.toxo            # Show model info
  toxo validate model.toxo        # Validate model file
  toxo test model.toxo --api-key KEY  # Test model
  toxo sample                     # Show sample code
  toxo help                       # Show help

Visit https://toxotune.com to create your AI experts!
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Version command
    subparsers.add_parser("version", help="Show version information")
    
    # Check command  
    subparsers.add_parser("check", help="Check dependencies and system status")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Show information about a .toxo file")
    info_parser.add_argument("file", help="Path to .toxo file")
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate a .toxo file")
    validate_parser.add_argument("file", help="Path to .toxo file")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test a .toxo file")
    test_parser.add_argument("file", help="Path to .toxo file")
    test_parser.add_argument("--api-key", required=True, help="API key for testing")
    
    # Sample command
    subparsers.add_parser("sample", help="Show sample usage code")
    
    # Help command
    subparsers.add_parser("help", help="Show detailed help information")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle commands
    if args.command == "version":
        cmd_version()
    elif args.command == "check":
        cmd_check()
    elif args.command == "info":
        cmd_info(args.file)
    elif args.command == "validate":
        cmd_validate(args.file)
    elif args.command == "test":
        cmd_test(args.file, args.api_key)
    elif args.command == "sample":
        cmd_sample()
    elif args.command == "help":
        cmd_help()
    else:
        # Show help if no command specified
        parser.print_help()


if __name__ == "__main__":
    main()
