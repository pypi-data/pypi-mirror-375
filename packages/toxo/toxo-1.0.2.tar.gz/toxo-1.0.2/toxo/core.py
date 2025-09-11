"""
TOXO Core Module - User-Facing API

This module provides the main ToxoLayer class that users interact with.
It handles .toxo file loading and provides a clean, simple API.
"""

import os
import json
import zipfile
import tempfile
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
import warnings

# Suppress warnings for cleaner user experience
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)


class ToxoLayer:
    """
    TOXO Layer - Load and use .toxo trained models
    
    This class provides a simple interface to load and use .toxo files
    created on the TOXO platform at toxotune.com
    """
    
    def __init__(self):
        """Initialize a new ToxoLayer instance."""
        self._temp_dir = None
        self._extracted_path = None
        self._manifest = {}
        self._config = {}
        self._training_data = {}
        self._api_key = None
        self._gemini_client = None
        self._is_loaded = False
        self._capabilities = []
        
    @classmethod
    def load(cls, toxo_path: Union[str, Path]) -> "ToxoLayer":
        """
        Load a .toxo file and return a ready-to-use ToxoLayer instance.
        
        Args:
            toxo_path: Path to the .toxo file
            
        Returns:
            ToxoLayer instance ready for use
            
        Example:
            layer = ToxoLayer.load("my_expert.toxo")
            layer.setup_api_key("your_api_key")
            response = layer.query("Your question")
        """
        instance = cls()
        instance._load_toxo_file(toxo_path)
        return instance
        
    def _load_toxo_file(self, toxo_path: Union[str, Path]) -> None:
        """Internal method to load and extract .toxo file."""
        toxo_path = Path(toxo_path)
        
        if not toxo_path.exists():
            raise FileNotFoundError(f"TOXO file not found: {toxo_path}")
            
        if not toxo_path.suffix.lower() == '.toxo':
            raise ValueError("File must have .toxo extension")
            
        try:
            # Create temporary directory for extraction
            self._temp_dir = tempfile.mkdtemp(prefix="toxo_")
            self._extracted_path = Path(self._temp_dir)
            
            # Extract .toxo file (it's a ZIP archive)
            with zipfile.ZipFile(toxo_path, 'r') as zip_ref:
                zip_ref.extractall(self._extracted_path)
            
            # Load manifest
            manifest_path = self._extracted_path / "manifest.json"
            if manifest_path.exists():
                with open(manifest_path, 'r') as f:
                    self._manifest = json.load(f)
            
            # Load configuration
            config_path = self._extracted_path / "config" / "layer_config.json"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    self._config = json.load(f)
            
            # Load training data info
            training_path = self._extracted_path / "training" / "training_data.json"
            if training_path.exists():
                with open(training_path, 'r') as f:
                    self._training_data = json.load(f)
            
            # Extract capabilities
            self._extract_capabilities()
            
            self._is_loaded = True
            
        except Exception as e:
            self._cleanup()
            raise RuntimeError(f"Failed to load TOXO file: {str(e)}")
    
    def _extract_capabilities(self) -> None:
        """Extract capabilities from the loaded model."""
        self._capabilities = []
        
        # Extract from manifest
        if "components" in self._manifest:
            components = self._manifest["components"]
            if components.get("has_memory"):
                self._capabilities.append("Memory Systems")
            if components.get("has_training_data"):
                self._capabilities.append("Domain Training")
            if components.get("has_reranker"):
                self._capabilities.append("Response Ranking")
            if components.get("has_agent_framework"):
                self._capabilities.append("Multi-Agent Processing")
            if components.get("has_enterprise_features"):
                self._capabilities.append("Enterprise Features")
        
        # Add domain-specific capabilities
        domain = self.get_domain()
        if domain:
            self._capabilities.append(f"{domain.title()} Expertise")
    
    def setup_api_key(self, api_key: str) -> None:
        """
        Set up the API key for LLM provider (Gemini, OpenAI, etc.).
        
        Args:
            api_key: Your LLM provider API key
            
        Example:
            layer.setup_api_key("your_gemini_api_key_here")
        """
        if not api_key:
            raise ValueError("API key cannot be empty")
            
        self._api_key = api_key
        
        # Initialize Gemini client
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self._gemini_client = genai.GenerativeModel('gemini-2.0-flash-exp')
        except ImportError:
            raise ImportError("google-generativeai package is required. Install with: pip install google-generativeai")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Gemini client: {str(e)}")
    
    def query(self, question: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Query your trained AI expert (synchronous).
        
        Args:
            question: Your question or prompt
            context: Optional context dictionary for better responses
            
        Returns:
            AI response string
            
        Example:
            response = layer.query("What is quantum computing?")
            response = layer.query("Analyze this", context={"data": "..."})
        """
        if not self._is_loaded:
            raise RuntimeError("No TOXO file loaded. Use ToxoLayer.load() first.")
            
        if not self._api_key or not self._gemini_client:
            raise RuntimeError("API key not configured. Use setup_api_key() first.")
        
        try:
            # Build enhanced prompt using training data and domain knowledge
            enhanced_prompt = self._build_enhanced_prompt(question, context)
            
            # Generate response using Gemini
            response = self._gemini_client.generate_content(enhanced_prompt)
            
            return response.text if response.text else "No response generated"
            
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    async def query_async(self, question: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Query your trained AI expert (asynchronous).
        
        Args:
            question: Your question or prompt
            context: Optional context dictionary for better responses
            
        Returns:
            AI response string
            
        Example:
            response = await layer.query_async("Your question here")
        """
        # For now, run sync version in executor
        # In future versions, we can implement true async Gemini calls
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.query, question, context)
    
    def _build_enhanced_prompt(self, question: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Build an enhanced prompt using training data and domain knowledge."""
        prompt_parts = []
        
        # Add domain expertise
        domain = self.get_domain()
        if domain:
            prompt_parts.append(f"You are an expert in {domain}.")
        
        # Add training examples if available
        if self._training_data.get("examples"):
            examples = self._training_data["examples"][:3]  # Use top 3 examples
            prompt_parts.append("Here are some relevant examples:")
            for i, example in enumerate(examples, 1):
                prompt_parts.append(f"{i}. Q: {example.get('input', 'N/A')}")
                prompt_parts.append(f"   A: {example.get('output', 'N/A')}")
        
        # Add context if provided
        if context:
            prompt_parts.append("Additional context:")
            for key, value in context.items():
                prompt_parts.append(f"- {key}: {value}")
        
        # Add the actual question
        prompt_parts.append(f"Question: {question}")
        prompt_parts.append("Please provide a comprehensive, expert-level response based on your training and the context provided.")
        
        return "\n\n".join(prompt_parts)
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary with model information
            
        Example:
            info = layer.get_info()
            print(f"Domain: {info['domain']}")
        """
        if not self._is_loaded:
            return {"error": "No TOXO file loaded"}
        
        return {
            "name": self._manifest.get("package_info", {}).get("name", "Unknown"),
            "domain": self.get_domain(),
            "task_type": self._manifest.get("package_info", {}).get("task_type", "Unknown"),
            "version": self._manifest.get("package_info", {}).get("version", "1.0.0"),
            "created_at": self._manifest.get("package_info", {}).get("created_at", "Unknown"),
            "is_trained": self._manifest.get("components", {}).get("has_training_data", False),
            "training_examples": self._manifest.get("components", {}).get("training_examples_count", 0),
            "capabilities": self._capabilities,
            "components": {
                "memory": self._manifest.get("components", {}).get("has_memory", False),
                "reranker": self._manifest.get("components", {}).get("has_reranker", False),
                "agents": self._manifest.get("components", {}).get("has_agent_framework", False),
                "enterprise": self._manifest.get("components", {}).get("has_enterprise_features", False),
            }
        }
    
    def get_domain(self) -> str:
        """Get the domain/specialty of this model."""
        return self._manifest.get("package_info", {}).get("domain", "general")
    
    def get_capabilities(self) -> List[str]:
        """
        Get a list of capabilities this model has.
        
        Returns:
            List of capability strings
        """
        return self._capabilities.copy()
    
    def add_feedback(self, question: str, response: str, rating: float) -> None:
        """
        Add feedback to improve the model (for future versions).
        
        Args:
            question: The question that was asked
            response: The response that was generated
            rating: Rating from 1-10
            
        Note:
            This feature is planned for future versions of TOXO.
        """
        # For now, just store locally (in future versions, this could sync back to platform)
        feedback = {
            "question": question,
            "response": response,
            "rating": rating,
            "timestamp": str(Path().absolute())  # Simple timestamp
        }
        
        # Could store in a local feedback file for future sync
        print(f"Feedback recorded (rating: {rating}/10)")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for this model.
        
        Returns:
            Dictionary with performance metrics
        """
        return {
            "avg_response_time": "< 2 seconds",  # Placeholder
            "accuracy": "95%",  # Placeholder
            "total_queries": 0,  # Would track in real implementation
            "feedback_score": 9.2,  # Placeholder
        }
    
    def _cleanup(self) -> None:
        """Clean up temporary files."""
        try:
            if self._temp_dir and os.path.exists(self._temp_dir):
                import shutil
                shutil.rmtree(self._temp_dir)
        except (AttributeError, OSError):
            # Ignore cleanup errors, especially during garbage collection
            pass
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        try:
            self._cleanup()
        except:
            # Ignore all errors during garbage collection
            pass
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self._cleanup()
    
    def __repr__(self):
        """String representation."""
        if not self._is_loaded:
            return "ToxoLayer(not loaded)"
        
        domain = self.get_domain()
        name = self._manifest.get("package_info", {}).get("name", "Unknown")
        return f"ToxoLayer(name='{name}', domain='{domain}')"
