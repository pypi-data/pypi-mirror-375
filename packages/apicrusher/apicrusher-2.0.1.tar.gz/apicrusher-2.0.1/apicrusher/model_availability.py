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
        
        # Current available models as of September 2025
        self.available_models = {
            'openai': [
                # GPT-5 family (Released August 7, 2025)
                'gpt-5', 'gpt-5-turbo', 'gpt-5-mini', 'gpt-5-nano',
                'gpt-5-pro',  # Extended reasoning variant
                
                # GPT-4 family (still available)
                'gpt-4', 'gpt-4-turbo', 'gpt-4-turbo-preview',
                'gpt-4o', 'gpt-4o-mini', 'gpt-4o-2024-08-06',
                'gpt-4-0613', 'gpt-4-32k',
                
                # GPT-3.5 family
                'gpt-3.5-turbo', 'gpt-3.5-turbo-16k',
                
                # O-series reasoning models
                'o1', 'o1-preview', 'o1-mini',
                'o3', 'o3-mini', 'o3-pro',
                'o4', 'o4-mini',  # Latest reasoning models
                
                # Realtime models
                'gpt-realtime', 'gpt-realtime-mini',
                
                # Open models (Released August 5, 2025)
                'gpt-oss-20b', 'gpt-oss-120b',
                
                # Legacy compatibility
                'gpt-4.5', 'gpt-4.5-turbo',  # Orion/transitional models
            ],
            
            'anthropic': [
                # Claude 4 family (Current generation - May/August 2025)
                'claude-opus-4-20250805', 
                'claude-opus-4.1-20250805',  # Released August 5, 2025
                'claude-opus-4-1-20250805',  # Alternative naming
                'claude-sonnet-4-20250805',
                'claude-sonnet-4-20250522',
                
                # Claude 3.5 family (still available)
                'claude-3.5-sonnet-20241022',
                'claude-3-5-sonnet-20241022',
                
                # Claude 3 family
                'claude-3-opus-20240229',
                'claude-3-sonnet-20240229',
                'claude-3-haiku-20240307',
                
                # Simplified names (aliases)
                'claude-opus-4', 'claude-opus-4.1',
                'claude-sonnet-4', 'claude-haiku',
                
                # Legacy
                'claude-instant-1.2',
            ],
            
            'google': [
                # Gemini 2.0 family (Latest)
                'gemini-2.0-pro', 'gemini-2.0-flash', 'gemini-2.0-ultra',
                'gemini-exp-2025-01-01',  # Experimental versions
                
                # Gemini 1.5 family
                'gemini-1.5-pro', 'gemini-1.5-pro-latest',
                'gemini-1.5-flash', 'gemini-1.5-flash-latest',
                'gemini-1.5-ultra',
                
                # Gemini 1.0 family
                'gemini-pro', 'gemini-pro-vision',
                
                # Legacy Palm models (being phased out)
                'text-bison-001', 'chat-bison-001',
            ],
            
            'meta': [
                # Llama 3.3 family (Latest - December 2024)
                'llama-3.3-70b', 'llama-3.3-70b-instruct',
                
                # Llama 3.2 family
                'llama-3.2-405b', 'llama-3.2-70b', 'llama-3.2-7b',
                'llama-3.2-405b-instruct', 'llama-3.2-70b-instruct',
                
                # Llama 3.1 family
                'llama-3.1-405b', 'llama-3.1-70b', 'llama-3.1-8b',
                
                # Llama 3 family
                'llama-3-70b', 'llama-3-8b',
                
                # Code Llama
                'codellama-70b', 'codellama-34b', 'codellama-13b',
            ],
            
            'mistral': [
                # Latest models
                'mistral-large-2', 'mistral-large-latest',
                'mistral-medium', 'mistral-small',
                
                # Mixtral models
                'mixtral-8x22b', 'mixtral-8x7b',
                
                # Specialized
                'codestral-22b', 'codestral-mamba',
                
                # Open models
                'mistral-7b', 'mistral-7b-instruct',
            ],
            
            'cohere': [
                # Command R family (Latest)
                'command-r-plus', 'command-r',
                
                # Command family
                'command', 'command-light', 'command-nightly',
                
                # Specialized
                'embed-english-v3.0', 'embed-multilingual-v3.0',
                'rerank-english-v2.0',
            ],
            
            'groq': [
                # Groq-hosted models (Fast inference)
                'llama3-70b-8192', 'llama3-8b-8192',
                'mixtral-8x7b-32768',
                'gemma-7b-it',
            ],
            
            'perplexity': [
                # Perplexity models
                'pplx-sonar-large', 'pplx-sonar-medium', 'pplx-sonar-small',
                'pplx-7b-online', 'pplx-70b-online',
            ],
            
            'xai': [
                # Grok models (X.AI)
                'grok-2', 'grok-2-mini',
                'grok-1', 'grok-1.5',
            ],
            
            'deepseek': [
                # DeepSeek models (Chinese, cost-effective)
                'deepseek-r1', 'deepseek-r1-distill',
                'deepseek-v3', 'deepseek-v2.5',
                'deepseek-coder-v2', 'deepseek-math',
            ],
            
            'alibaba': [
                # Qwen models
                'qwen2.5-72b', 'qwen2.5-32b', 'qwen2.5-7b',
                'qwen2-vl-72b',  # Vision-language model
            ],
            
            'together': [
                # Together AI hosted models
                'meta-llama/Llama-3.3-70B-Instruct',
                'mistralai/Mixtral-8x22B-Instruct',
                'NousResearch/Nous-Hermes-2-Mixtral-8x7B',
            ],
            
            'replicate': [
                # Replicate hosted models
                'meta/llama-3.3-70b-instruct',
                'mistralai/mixtral-8x7b-instruct',
            ],
        }
        
        # Fallback mapping for deprecated models
        self.fallback_map = {
            # OpenAI deprecated models
            'openai:text-davinci-003': 'gpt-3.5-turbo',
            'openai:code-davinci-002': 'gpt-4',
            'openai:gpt-4-32k-0314': 'gpt-4-turbo',
            'openai:gpt-3.5-turbo-0301': 'gpt-3.5-turbo',
            'openai:gpt-4-0314': 'gpt-4',
            
            # Anthropic deprecated models
            'anthropic:claude-2': 'claude-3-sonnet-20240229',
            'anthropic:claude-instant-1': 'claude-3-haiku-20240307',
            'anthropic:claude-2.1': 'claude-3-sonnet-20240229',
            
            # Google deprecated models
            'google:palm-2': 'gemini-1.5-flash',
            'google:gemini-pro': 'gemini-1.5-pro',
            'google:bard': 'gemini-1.5-pro',
            
            # Generic fallbacks by capability tier
            'expensive': [
                'gpt-5', 'claude-opus-4.1-20250805', 'gemini-2.0-pro',
                'gpt-4', 'claude-3-opus-20240229', 'gemini-1.5-pro'
            ],
            'balanced': [
                'gpt-4o', 'claude-sonnet-4-20250805', 'gemini-1.5-pro',
                'gpt-3.5-turbo', 'claude-3-sonnet-20240229'
            ],
            'cheap': [
                'gpt-4o-mini', 'claude-3-haiku-20240307', 'gemini-1.5-flash',
                'gpt-3.5-turbo', 'llama-3.3-70b', 'mistral-7b'
            ],
            'fast': [
                'gpt-4o-mini', 'claude-3-haiku-20240307', 'gemini-1.5-flash',
                'groq/llama3-8b-8192', 'deepseek-v3'
            ]
        }
        
        # Known deprecated models with deprecation dates
        self.deprecated_models = {
            # OpenAI deprecations
            'text-davinci-003': '2024-01-04',
            'code-davinci-002': '2024-01-04',
            'text-davinci-002': '2024-01-04',
            'gpt-4-32k-0314': '2024-06-06',
            'gpt-3.5-turbo-0301': '2024-06-13',
            'gpt-4-0314': '2024-06-13',
            'gpt-4': '2025-04-30',  # Replaced by gpt-4o
            
            # Anthropic deprecations
            'claude-2': '2024-03-01',
            'claude-2.1': '2024-03-01',
            'claude-instant-1': '2024-05-01',
            
            # Google deprecations
            'palm-2': '2024-12-31',
            'text-bison-001': '2025-06-01',
            'chat-bison-001': '2025-06-01',
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
        
        # Test model availability (using static list)
        is_available = self._test_model_availability(provider, model)
        
        # Cache result
        self.availability_cache[cache_key] = (is_available, time.time())
        
        if not is_available:
            fallback = self.get_fallback(provider, model)
            return False, fallback
        
        return True, None
    
    def _test_model_availability(self, provider: str, model: str) -> bool:
        """
        Check model availability using static list (no API calls to save money)
        """
        if provider in self.available_models:
            # Check exact match
            if model in self.available_models[provider]:
                return True
            
            # Check partial match for versioned models
            model_base = model.split('-')[0]
            for available_model in self.available_models[provider]:
                if available_model.startswith(model_base):
                    return True
        
        # For unknown providers or models, assume available
        # (Better to try and fail than to block unnecessarily)
        return True
    
    def get_fallback(self, provider: str, model: str) -> Optional[str]:
        """
        Get fallback model for a deprecated/unavailable model.
        """
        # Check specific fallback
        specific_key = f"{provider}:{model}"
        if specific_key in self.fallback_map:
            return self.fallback_map[specific_key]
        
        # Determine capability level and find alternative
        model_lower = model.lower()
        
        # Ultra-high tier (most expensive, most capable)
        if any(term in model_lower for term in ['gpt-5', 'opus-4', 'ultra', 'pro-max']):
            fallbacks = self.fallback_map.get('expensive', [])
        # High tier
        elif any(term in model_lower for term in ['gpt-4', 'opus', 'sonnet-4', 'large', 'pro']):
            fallbacks = self.fallback_map.get('expensive', [])
        # Mid tier
        elif any(term in model_lower for term in ['sonnet', 'medium', 'turbo']):
            fallbacks = self.fallback_map.get('balanced', [])
        # Low tier
        elif any(term in model_lower for term in ['mini', 'haiku', 'flash', 'small', 'nano']):
            fallbacks = self.fallback_map.get('cheap', [])
        else:
            fallbacks = self.fallback_map.get('balanced', [])
        
        # Try to stay within same provider if possible
        for fallback in fallbacks:
            if provider in fallback or (provider == 'openai' and 'gpt' in fallback):
                return fallback
            if provider == 'anthropic' and 'claude' in fallback:
                return fallback
            if provider == 'google' and 'gemini' in fallback:
                return fallback
        
        # Return first available fallback
        return fallbacks[0] if fallbacks else 'gpt-4o-mini'
    
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
                data = response.json()
                # Update deprecated models from all providers
                if 'openai' in data:
                    self.deprecated_models.update(data['openai'])
                if 'anthropic' in data:
                    self.deprecated_models.update(data['anthropic'])
                if 'google' in data:
                    self.deprecated_models.update(data['google'])
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
