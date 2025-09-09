# apicrusher/__init__.py
# Path: apicrusher/__init__.py
# Version: 2.2.1 - 2025 Model Updates

"""
APICrusher - Universal AI API Cost Optimizer
Reduce AI API costs by 63-99% across all providers
Supports: OpenAI, Anthropic, Google, xAI, Groq, Cohere, Mistral, and more
"""

__version__ = "2.2.1"
__author__ = "APICrusher"
__email__ = "hello@apicrusher.com"
__url__ = "https://apicrusher.com"

# Import main classes
from .core import (
    OpenAI,
    APIOptimizer,
    UniversalModelRouter,
    UniversalAPIClient,
    ContextCompressor,
    ModelConfig
)

# Export public API
__all__ = [
    "OpenAI",
    "APIOptimizer", 
    "UniversalModelRouter",
    "UniversalAPIClient",
    "ContextCompressor",
    "ModelConfig",
    "__version__"
]

# Package metadata
def get_version():
    """Return the current version of APICrusher"""
    return __version__

def print_version():
    """Print APICrusher version and capabilities"""
    print(f"APICrusher v{__version__}")
    print("✅ 2025 Model Support:")
    print("  - GPT-5 models ($1.25/$10 per M)")
    print("  - Claude Opus 4.1 ($15/$75 per M)")
    print("  - Gemini 2.5 Flash-Lite ($0.10/$0.40 per M)")
    print("  - xAI Grok models")
    print("  - 15+ providers supported")
    print("💰 Proven savings: 63-99% cost reduction")
    print("🌐 Learn more: https://apicrusher.com")
