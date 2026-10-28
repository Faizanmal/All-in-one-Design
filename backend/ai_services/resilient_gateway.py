"""
Resilient multi-provider AI gateway with ordered failover.

Fallback order:
  1. Groq
  2. Nvidia
  3. Gemini (Google)
  4. OpenAI
  5. Anthropic
"""
import os
import json
import logging
import hashlib
from typing import Dict, Any, Callable, List, Optional, Tuple

logger = logging.getLogger(__name__)

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class ResilientAIGateway:
    """
    Enterprise AI Gateway with caching and multi-provider failover.

    Order: Groq → Nvidia → Gemini → OpenAI → Anthropic
    """

    def __init__(self):
        self.groq_key = os.getenv('GROQ_API_KEY')
        self.google_key = os.getenv('GOOGLE_API_KEY')
        self.nvidia_key = os.getenv('NVIDIA_API_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')

        self.primary_model = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
        self.google_model = os.getenv('GOOGLE_MODEL', 'gemini-1.5-pro')
        self.nvidia_model = os.getenv('NVIDIA_MODEL', 'nvidia/llama-3.1-70b-instruct')
        self.fallback_model = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
        self.anthropic_model = os.getenv('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')

        self.groq_client = None
        if GROQ_AVAILABLE and self.groq_key:
            try:
                self.groq_client = Groq(api_key=self.groq_key)
            except Exception as e:
                logger.warning(f"Failed to initialize Groq client: {e}")

        self.google_client = None
        if GOOGLE_AVAILABLE and self.google_key:
            try:
                genai.configure(api_key=self.google_key)
                self.google_client = genai.GenerativeModel(self.google_model)
            except Exception as e:
                logger.warning(f"Failed to initialize Google/Gemini client: {e}")

        self.nvidia_client = None
        if OPENAI_AVAILABLE and self.nvidia_key:
            try:
                self.nvidia_client = OpenAI(
                    api_key=self.nvidia_key,
                    base_url='https://integrate.api.nvidia.com/v1',
                )
            except Exception as e:
                logger.warning(f"Failed to initialize Nvidia client: {e}")

        self.openai_client = None
        if OPENAI_AVAILABLE and self.openai_key:
            try:
                self.openai_client = OpenAI(api_key=self.openai_key)
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")

        self.anthropic_client = None
        if ANTHROPIC_AVAILABLE and self.anthropic_key:
            try:
                self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_key)
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic client: {e}")

        # Exact-prompt cache TTL (1 week)
        self.cache_ttl = 60 * 60 * 24 * 7

    def _generate_cache_key(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        combined = f"{system_prompt}||{user_prompt}||{temperature}"
        prompt_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()
        return f"ai_gateway_cache:v1:{prompt_hash}"

    def _parse_json_content(self, content: str) -> Dict[str, Any]:
        if not content or not content.strip():
            raise ValueError('Empty model response')
        text = content.strip()
        if text.startswith('```'):
            # Strip markdown fences if a provider wraps JSON
            lines = text.split('\n')
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            text = '\n'.join(lines).strip()
        return json.loads(text)

    def _call_groq(self, system_prompt: str, user_prompt: str, temperature: float) -> Dict[str, Any]:
        if not self.groq_client:
            raise ValueError('Groq API key not configured')
        response = self.groq_client.chat.completions.create(
            model=self.primary_model,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
            temperature=temperature,
            response_format={'type': 'json_object'},
        )
        return self._parse_json_content(response.choices[0].message.content)

    def _call_gemini(self, system_prompt: str, user_prompt: str, temperature: float) -> Dict[str, Any]:
        if not self.google_client:
            raise ValueError('Google/Gemini API key not configured')
        generation_config = genai.GenerationConfig(
            temperature=temperature,
            response_mime_type='application/json',
        )
        response = self.google_client.generate_content(
            contents=f'System: {system_prompt}\n\nUser: {user_prompt}',
            generation_config=generation_config,
        )
        return self._parse_json_content(response.text)

    def _call_nvidia(self, system_prompt: str, user_prompt: str, temperature: float) -> Dict[str, Any]:
        if not self.nvidia_client:
            raise ValueError('Nvidia API key not configured')
        # Nvidia may not always honor response_format; still request JSON in prompt.
        response = self.nvidia_client.chat.completions.create(
            model=self.nvidia_model,
            messages=[
                {
                    'role': 'system',
                    'content': system_prompt + '\n\nRespond with valid JSON only.',
                },
                {'role': 'user', 'content': user_prompt},
            ],
            temperature=temperature,
        )
        return self._parse_json_content(response.choices[0].message.content)

    def _call_openai(self, system_prompt: str, user_prompt: str, temperature: float) -> Dict[str, Any]:
        if not self.openai_client:
            raise ValueError('OpenAI API key not configured')
        response = self.openai_client.chat.completions.create(
            model=self.fallback_model,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
            temperature=temperature,
            response_format={'type': 'json_object'},
        )
        return self._parse_json_content(response.choices[0].message.content)

    def _call_anthropic(self, system_prompt: str, user_prompt: str, temperature: float) -> Dict[str, Any]:
        if not self.anthropic_client:
            raise ValueError('Anthropic API key not configured')
        response = self.anthropic_client.messages.create(
            model=self.anthropic_model,
            max_tokens=8192,
            temperature=temperature,
            system=system_prompt + '\n\nRespond with valid JSON only. No markdown.',
            messages=[{'role': 'user', 'content': user_prompt}],
        )
        # Anthropic returns a list of content blocks
        parts = []
        for block in response.content:
            text = getattr(block, 'text', None)
            if text:
                parts.append(text)
        return self._parse_json_content('\n'.join(parts))

    def _providers(self) -> List[Tuple[str, str, Callable[[str, str, float], Dict[str, Any]]]]:
        """Ordered provider chain: name, model id, callable."""
        return [
            ('Groq', self.primary_model, self._call_groq),
            ('Nvidia', self.nvidia_model, self._call_nvidia),
            ('Gemini', self.google_model, self._call_gemini),
            ('OpenAI', self.fallback_model, self._call_openai),
            ('Anthropic', self.anthropic_model, self._call_anthropic),
        ]

    def configured_providers(self) -> List[str]:
        """Return names of providers that have clients ready (fallback order)."""
        ready = []
        if self.groq_client:
            ready.append('Groq')
        if self.nvidia_client:
            ready.append('Nvidia')
        if self.google_client:
            ready.append('Gemini')
        if self.openai_client:
            ready.append('OpenAI')
        if self.anthropic_client:
            ready.append('Anthropic')
        return ready

    def generate_json_response(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Execute the AI request with Redis caching and ordered provider failover.
        Returns a parsed JSON dict or raises Exception when all providers fail.
        """
        from django.core.cache import cache

        cache_key = self._generate_cache_key(system_prompt, user_prompt, temperature)

        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info('AI Gateway: Cache hit. Returning cached response.')
            return json.loads(cached_result)

        errors: List[str] = []
        configured = self.configured_providers()
        if not configured:
            raise Exception(
                'AI Generation failed: no providers configured. '
                'Set GROQ_API_KEY, NVIDIA_API_KEY, GOOGLE_API_KEY, OPENAI_API_KEY, and/or ANTHROPIC_API_KEY.'
            )

        for name, model, call in self._providers():
            if name not in configured:
                continue
            try:
                logger.info(f'AI Gateway: Attempting provider ({name}: {model})')
                parsed = call(system_prompt, user_prompt, temperature)
                cache.set(cache_key, json.dumps(parsed), self.cache_ttl)
                logger.info(f'AI Gateway: Success via {name}')
                return parsed
            except Exception as e:
                msg = f'{name}: {e}'
                errors.append(msg)
                logger.warning(f'AI Gateway: Provider failed ({msg}). Trying next...')

        detail = '; '.join(errors)
        logger.error(f'AI Gateway: All providers failed. {detail}')
        raise Exception(f'AI Generation exhausted all fallback providers. {detail}')


_gateway: Optional[ResilientAIGateway] = None


def get_resilient_gateway() -> ResilientAIGateway:
    global _gateway
    if _gateway is None:
        _gateway = ResilientAIGateway()
    return _gateway


def reset_resilient_gateway() -> None:
    """Clear singleton (useful after env changes in tests)."""
    global _gateway
    _gateway = None
