# setup.py
# Path: setup.py
# Comprehensive setup for APICrusher with intelligent dependencies

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="apicrusher",
    version="2.0.1",
    author="APICrusher",
    author_email="hello@apicrusher.com",
    description="Cut AI API costs by 63-99% with intelligent routing across all AI providers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://apicrusher.com",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.7",
    
    # Core dependencies - always installed
    install_requires=[
        "requests>=2.28.0",  # For API calls and telemetry
    ],
    
    # Optional dependencies for different use cases
    extras_require={
        # Individual provider support
        "openai": ["openai>=1.0.0"],
        "anthropic": ["anthropic>=0.25.0"],
        "google": ["google-generativeai>=0.3.0"],
        "cohere": ["cohere>=4.0.0"],
        
        # Caching support
        "redis": ["redis>=4.5.0"],
        
        # Most common use case - OpenAI with caching
        "standard": [
            "openai>=1.0.0",
            "redis>=4.5.0",
        ],
        
        # Everything - all providers and features
        "all": [
            "openai>=1.0.0",
            "anthropic>=0.25.0",
            "google-generativeai>=0.3.0",
            "cohere>=4.0.0",
            "redis>=4.5.0",
        ],
        
        # Development dependencies
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "twine>=4.0.0",
            "wheel>=0.37.0",
        ],
    },
    
    keywords=[
        "openai", "anthropic", "google", "ai", "api", 
        "optimization", "cost-reduction", "llm", "gpt", 
        "claude", "gemini", "gpt-5", "gpt-4", "claude-4",
        "api-optimization", "ai-cost-reduction", "universal-ai",
        "groq", "mistral", "cohere", "deepseek", "llama"
    ],
    
    project_urls={
        "Website": "https://apicrusher.com",
        "Documentation": "https://apicrusher.com/docs",
        "Source": "https://github.com/apicrusher/apicrusher",
        "Bug Reports": "https://github.com/apicrusher/apicrusher/issues",
        "Changelog": "https://apicrusher.com/changelog",
    },
    
    # Entry points if you want to provide CLI tools
    entry_points={
        "console_scripts": [
            # Future: apicrusher-cli=apicrusher.cli:main
        ],
    },
    
    # Package data
    package_data={
        "apicrusher": ["*.json", "*.yaml", "*.yml"],
    },
    
    # Metadata
    license="MIT",
    platforms=["any"],
    zip_safe=False,  # Don't install as zip for better debugging
)
