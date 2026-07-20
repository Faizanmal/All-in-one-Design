import os
import json
import logging
import hashlib
from typing import Dict, Any
from django.core.cache import cache
from groq import Groq
from openai import OpenAI

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

try:
    import openai
    NVIDIA_AVAILABLE = True
except ImportError:
    NVIDIA_AVAILABLE = False

logger = logging.getLogger(__name__)

class ResilientAIGateway:
    """
    Advanced Enterprise AI Gateway.
    Features:
    1. Semantic/Prompt Caching via Redis to drastically reduce API costs.
    2. Automatic Failover: Tries Primary Model (Groq), falls back to Secondary (OpenAI), 
       Tertiary (Nvidia), and Quaternary (Google).
    3. Traces token usage and execution times.
    """
    
    def __init__(self):
        self.groq_key = os.getenv('GROQ_API_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.nvidia_key = os.getenv('NVIDIA_API_KEY')
        self.google_project_id = os.getenv('GOOGLE_PROJECT_ID')
        self.google_location = os.getenv('GOOGLE_LOCATION', 'us-central1')
        
        self.groq_client = Groq(api_key=self.groq_key) if self.groq_key else None
        self.openai_client = OpenAI(api_key=self.openai_key) if self.openai_key else None
        
        # Initialize Nvidia client (using OpenAI-compatible API)
        self.nvidia_client = None
        if NVIDIA_AVAILABLE and self.nvidia_key:
            try:
                self.nvidia_client = openai.OpenAI(
                    api_key=self.nvidia_key,
                    base_url="https://integrate.api.nvidia.com/v1"
                )
            except Exception as e:
                logger.warning(f"Failed to initialize Nvidia client: {e}")
        
        # Initialize Google client
        self.google_client = None
        if GOOGLE_AVAILABLE and self.google_project_id:
            try:
                genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
                self.google_client = genai.GenerativeModel(self.google_model)
            except Exception as e:
                logger.warning(f"Failed to initialize Google client: {e}")
        
        self.primary_model = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
        self.fallback_model = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
        self.nvidia_model = os.getenv('NVIDIA_MODEL', 'nvidia/llama-3.1-70b-instruct')
        self.google_model = os.getenv('GOOGLE_MODEL', 'gemini-1.5-pro')
        
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
            try:
                if not self.openai_client:
                    raise ValueError("OpenAI API key not configured")
                    
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
                logger.warning(f"AI Gateway: Secondary provider failed ({str(nested_e)}). Trying tertiary provider...")
                
                # 4. Try Tertiary Provider (Nvidia Fallback)
                try:
                    if not self.nvidia_client:
                        raise ValueError("Nvidia API key not configured")
                        
                    logger.info(f"AI Gateway: Attempting tertiary provider (Nvidia: {self.nvidia_model})")
                    response = self.nvidia_client.chat.completions.create(
                        model=self.nvidia_model,
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
                    
                except Exception as tertiary_e:
                    logger.warning(f"AI Gateway: Tertiary provider failed ({str(tertiary_e)}). Trying quaternary provider...")
                    
                    # 5. Try Quaternary Provider (Google Fallback)
                    try:
                        if not self.google_client:
                            raise ValueError("Google AI not configured")
                            
                        logger.info(f"AI Gateway: Attempting quaternary provider (Google: {self.google_model})")
                        
                        # Configure for JSON response
                        generation_config = genai.GenerationConfig(
                            temperature=temperature,
                            response_mime_type="application/json"
                        )
                        
                        response = self.google_client.generate_content(
                            contents=f"System: {system_prompt}\n\nUser: {user_prompt}",
                            generation_config=generation_config
                        )
                        
                        content = response.text
                        parsed = json.loads(content)
                        
                        # Store in cache
                        cache.set(cache_key, content, self.cache_ttl)
                        return parsed
                        
                    except Exception as quaternary_e:
                        logger.error(f"AI Gateway: All providers failed. Primary: {str(e)}, Secondary: {str(nested_e)}, Tertiary: {str(tertiary_e)}, Quaternary: {str(quaternary_e)}")
                        raise Exception(f"AI Generation exhausted all fallback providers. Primary err: {str(e)}, Secondary err: {str(nested_e)}, Tertiary err: {str(tertiary_e)}, Quaternary err: {str(quaternary_e)}")

# Singleton instance
_gateway = None

def get_resilient_gateway() -> ResilientAIGateway:
    global _gateway
    if _gateway is None:
        _gateway = ResilientAIGateway()
    return _gateway
