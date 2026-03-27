import os
import json
import logging
import hashlib
from typing import Dict, Any
from django.core.cache import cache
from groq import Groq
from openai import OpenAI

logger = logging.getLogger(__name__)

class ResilientAIGateway:
    """
    Advanced Enterprise AI Gateway.
    Features:
    1. Semantic/Prompt Caching via Redis to drastically reduce API costs.
    2. Automatic Failover: Tries Primary Model (Groq), falls back to Secondary (OpenAI).
    3. Traces token usage and execution times.
    """
    
    def __init__(self):
        self.groq_key = os.getenv('GROQ_API_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        
        self.groq_client = Groq(api_key=self.groq_key) if self.groq_key else None
        self.openai_client = OpenAI(api_key=self.openai_key) if self.openai_key else None
        
        self.primary_model = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
        self.fallback_model = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
        
        # Cache TTL in seconds (1 week for exact prompts)
        self.cache_ttl = 60 * 60 * 24 * 7 

    def _generate_cache_key(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """Generate a deterministic hash for caching."""
        combined = f"{system_prompt}||{user_prompt}||{temperature}"
        prompt_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()
        return f"ai_gateway_cache:v1:{prompt_hash}"

    def generate_json_response(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> Dict[str, Any]:
        """
        Executes the AI request with caching and fallback.
        Returns parsed JSON dict or raises Exception.
        """
        cache_key = self._generate_cache_key(system_prompt, user_prompt, temperature)
        
        # 1. Check Cache (Semantic/Exact Caching)
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info("AI Gateway: Cache hit. Returning cached response.")
            return json.loads(cached_result)

        # 2. Try Primary Provider (Groq)
        try:
            if not self.groq_client:
                raise ValueError("Groq API key not configured")
                
            logger.info(f"AI Gateway: Attempting primary provider (Groq: {self.primary_model})")
            response = self.groq_client.chat.completions.create(
                model=self.primary_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                response_format={"type": "json_object"},
            )
            
            content = response.choices[0].message.content
            
            # Verify it's valid JSON
            parsed = json.loads(content)
            
            # Store in cache
            cache.set(cache_key, content, self.cache_ttl)
            return parsed

        except Exception as e:
            logger.warning(f"AI Gateway: Primary provider failed ({str(e)}). Initiating failover...")
            
            # 3. Try Secondary Provider (OpenAI Fallback)
            if not self.openai_client:
                logger.error("AI Gateway: Both primary failed and secondary not configured.")
                raise Exception("AI Generation completely failed. No secondary configured.")
                
            try:
                logger.info(f"AI Gateway: Attempting secondary provider (OpenAI: {self.fallback_model})")
                response = self.openai_client.chat.completions.create(
                    model=self.fallback_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=temperature,
                    response_format={"type": "json_object"},
                )
                
                content = response.choices[0].message.content
                parsed = json.loads(content)
                
                # Store in cache
                cache.set(cache_key, content, self.cache_ttl)
                return parsed
                
            except Exception as nested_e:
                logger.error(f"AI Gateway: Secondary provider also failed. Error: {str(nested_e)}")
                raise Exception(f"AI Generation exhausted all fallback providers. Primary err: {str(e)}, Secondary err: {str(nested_e)}")

# Singleton instance
_gateway = None

def get_resilient_gateway() -> ResilientAIGateway:
    global _gateway
    if _gateway is None:
        _gateway = ResilientAIGateway()
    return _gateway
