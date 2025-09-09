# model_availability.py
# Path: apicrusher/model_availability.py
# Checks model availability and provides fallbacks

import time
import json
import requests
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

class ModelAvailabilityChecker:
    """
    Caches model availability and provides intelligent fallbacks
    when models are deprecated or unavailable.
    """
    
    def __init__(self):
        self.availability_cache = {}  # {provider:model: (available, timestamp)}
        self.cache_duration = 3600  # 1 hour cache
        
        # Fallback mapping for deprecated models
        self.fallback_map = {
            # OpenAI fallbacks
            'openai:gpt-4-32k': 'gpt-4-turbo-preview',
            'openai:gpt-3.5-turbo-16k': 'gpt-3.5-turbo',
            'openai:text-davinci-003': 'gpt-3.5-turbo',
            'openai:code-davinci-002': 'gpt-4',
            
            # Anthropic fallbacks
            'anthropic:claude-2': 'claude-3-sonnet-20240229',
            'anthropic:claude-instant-1': 'claude-3-haiku-20240307',
            
            # Google fallbacks
            'google:palm-2': 'gemini-1.5-flash',
            'google:gemini-pro': 'gemini-1.5-pro',
            
            # Generic fallbacks by capability
            'expensive': ['gpt-4', 'claude-3-opus-20240229', 'gemini-1.5-pro'],
            'cheap': ['gpt-3.5-turbo', 'claude-3-haiku-20240307', 'gemini-1.5-flash'],
            'fast': ['gpt-3.5-turbo', 'claude-3-haiku-20240307', 'groq/llama3-8b-8192']
        }
        
        # Known deprecated models
        self.deprecated_models = {
            'text-davinci-003': '2024-01-04',
            'code-davinci-002': '2024-01-04',
            'gpt-4-32k-0314': '2024-06-06',
            'gpt-3.5-turbo-0301': '2024-06-13'
        }
    
    def is_model_available(self, provider: str, model: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a model is available, with caching.
        Returns (is_available, fallback_model_if_not)
        """
        cache_key = f"{provider}:{model}"
        
        # Check if model is known deprecated
        if model in self.deprecated_models:
            fallback = self.get_fallback(provider, model)
            return False, fallback
        
        # Check cache
        if cache_key in self.availability_cache:
            cached_result, timestamp = self.availability_cache[cache_key]
            if time.time() - timestamp < self.cache_duration:
                if not cached_result:
                    return False, self.get_fallback(provider, model)
                return cached_result, None
        
        # Test model availability
        is_available = self._test_model_availability(provider, model)
        
        # Cache result
        self.availability_cache[cache_key] = (is_available, time.time())
        
        if not is_available:
            fallback = self.get_fallback(provider, model)
            return False, fallback
        
        return True, None
    
    def _test_model_availability(self, provider: str, model: str) -> bool:
        """
        Test if a model is actually available by making a minimal API call.
        """
        try:
            if provider == 'openai':
                # Test with OpenAI API
                import openai
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=[{"role": "user", "content": "Hi"}],
                    max_tokens=1
                )
                return True
            elif provider == 'anthropic':
                # Test with Anthropic API
                headers = {"anthropic-version": "2023-06-01"}
                response = requests.post(
                    "https://api.anthropic.com/v1/messages",
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": "Hi"}],
                        "max_tokens": 1
                    },
                    headers=headers
                )
                return response.status_code == 200
            elif provider == 'google':
                # Test with Google API
                response = requests.post(
                    f"https://generativelanguage.googleapis.com/v1/models/{model}:generateContent",
                    json={"contents": [{"parts": [{"text": "Hi"}]}]}
                )
                return response.status_code == 200
        except Exception as e:
            # Model not available or API error
            print(f"Model {provider}:{model} not available: {e}")
            return False
        
        return False
    
    def get_fallback(self, provider: str, model: str) -> Optional[str]:
        """
        Get fallback model for a deprecated/unavailable model.
        """
        # Check specific fallback
        specific_key = f"{provider}:{model}"
        if specific_key in self.fallback_map:
            return self.fallback_map[specific_key]
        
        # Determine capability level and find alternative
        if 'gpt-4' in model or 'opus' in model or 'large' in model:
            fallbacks = self.fallback_map['expensive']
        elif 'mini' in model or 'haiku' in model or 'small' in model:
            fallbacks = self.fallback_map['cheap']
        else:
            fallbacks = self.fallback_map['cheap']
        
        # Try to stay within same provider if possible
        for fallback in fallbacks:
            if provider in fallback or provider == 'openai' and 'gpt' in fallback:
                return fallback
        
        # Return first available fallback
        return fallbacks[0] if fallbacks else 'gpt-3.5-turbo'
    
    def update_deprecated_list(self):
        """
        Fetch latest deprecated models list from APICrusher server.
        """
        try:
            response = requests.get(
                "https://apicrusher.com/api/deprecated-models",
                timeout=5
            )
            if response.status_code == 200:
                self.deprecated_models = response.json()
        except:
            # Use local list if can't fetch updates
            pass

# Integration with existing SDK
def integrate_with_sdk():
    """
    Add this to your apicrusher/core.py OpenAI class __init__:
    """
    # In __init__ method:
    # self.model_checker = ModelAvailabilityChecker()
    
    # In chat.completions.create method:
    """
    # Check model availability
    is_available, fallback = self.model_checker.is_model_available(provider, model)
    if not is_available and fallback:
        print(f"⚠️ Model {model} deprecated/unavailable. Using {fallback} instead.")
        model = fallback
    """
