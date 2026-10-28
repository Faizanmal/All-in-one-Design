"""
Hybrid smart multi-agent UI/UX generation.

Division of labour that makes this reliable: the model decides *structure and
copy*, the deterministic layout engine decides *every pixel*. Models have no
spatial reasoning, so asking them for absolute coordinates on a 1920x1080
canvas is what produced scattered, overlapping output. Asking them for a
compact semantic spec instead gives full layout flexibility (shell, section
mix, ordering, content) while alignment is guaranteed by construction.

Routing by prompt complexity:
- SimpleDesignAgent   : 1 call  (~700 tokens)
- ModerateDesignAgent : 1 call  (~1400 tokens, richer content)
- AdvancedDesignAgent : 2 calls (~2600 tokens, structure then content)
"""
import hashlib
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from django.core.cache import cache

from .layout_engine import compose_layout, normalize_spec

logger = logging.getLogger(__name__)

SECTION_MENU = (
    "stat_row (KPI cards: items[{label,value,trend}]), "
    "chart (title, chart:'bar'|'line', series:[0-1 floats], labels:[short strings]), "
    "list (title, items[{title,meta}]), "
    "cards (title, columns:2-4, items[{title,body}]), "
    "table (title, columns:[names], rows:[[cells]]), "
    "form (title, fields[{label,placeholder}], submit), "
    "hero (title, body, cta), "
    "media (title), "
    "text (title, body)"
)

SPEC_RULES = """You describe UI structure and content. You NEVER output coordinates,
positions, sizes, or pixel values - a layout engine handles all geometry.

Return ONLY a JSON object:
{
  "shell": "sidebar" | "topbar" | "plain",
  "brand": "product name",
  "page_title": "screen name",
  "nav": ["Item", ...],
  "accent": "#2563EB",
  "sections": [ {"type": "...", ...}, ... ]
}

shell guidance:
- "sidebar": app dashboards, admin panels, data tools
- "topbar": simple app screens, profiles, settings
- "plain": landing pages, sign-up / login, marketing

Available section types (choose the ones that fit the request, in the order they
should appear top to bottom):
""" + SECTION_MENU + """

Rules:
- 2 to 5 sections. Pick types that genuinely match the request.
- Write real, specific content - never "Lorem ipsum" or "Item 1".
- Keep labels under 24 characters and body text under 90 characters.
- Output raw JSON only, no markdown fences, no commentary."""


class ComplexityLevel(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


@dataclass
class SmartConfig:
    prompt: str
    canvas_width: int = 1920
    canvas_height: int = 1080
    style: str = "modern"
    color_scheme: Optional[List[str]] = None
    complexity_override: Optional[ComplexityLevel] = None
    enable_caching: bool = True
    max_tokens: Optional[int] = None
    max_refinement_cycles: int = 3

    def accent(self) -> Optional[str]:
        for color in (self.color_scheme or []):
            text = str(color or '').strip()
            if text.startswith('#') and len(text) in (4, 7):
                return text
        return None


class ComplexityAnalyzer:
    """Scores a prompt so we spend tokens proportional to the need."""

    SIMPLE_KEYWORDS = [
        'dashboard', 'form', 'login', 'signup', 'sign up', 'profile', 'settings',
        'list', 'table', 'card', 'button', 'input', 'home', 'landing',
    ]

    COMPLEX_KEYWORDS = [
        'analytics', 'real-time', 'interactive', 'dynamic', 'advanced',
        'multi-step', 'workflow', 'pipeline', 'integration', 'custom',
        'intelligent', 'ai-powered', 'machine learning', 'predictive',
        'comprehensive', 'enterprise',
    ]

    # Distinct content features a prompt can ask for. Two or more means the
    # screen needs real composition, so it is worth the richer content pass.
    FEATURE_SIGNALS = {
        'stats': ('stat', 'metric', 'kpi', 'number', 'count'),
        'chart': ('chart', 'graph', 'trend', 'analytics', 'progress'),
        'table': ('table', 'grid', 'record', 'order'),
        'list': ('list', 'activity', 'feed', 'timeline', 'recent', 'history'),
        'form': ('form', 'input', 'field', 'login', 'signup', 'sign up', 'register'),
        'hero': ('hero', 'landing', 'banner', 'marketing', 'pricing'),
        'media': ('image', 'photo', 'gallery', 'video'),
    }

    def analyze(self, prompt: str) -> Tuple[ComplexityLevel, Dict[str, Any]]:
        lowered = (prompt or '').lower()
        clauses = len([c for c in lowered.replace(';', ',').split(',') if c.strip()])
        simple_hits = sum(1 for kw in self.SIMPLE_KEYWORDS if kw in lowered)
        complex_hits = sum(1 for kw in self.COMPLEX_KEYWORDS if kw in lowered)
        words = len(lowered.split())
        features = [
            name for name, keywords in self.FEATURE_SIGNALS.items()
            if any(kw in lowered for kw in keywords)
        ]

        if clauses >= 5 or complex_hits >= 2 or words >= 50 or len(features) >= 4:
            complexity = ComplexityLevel.COMPLEX
        elif clauses <= 2 and words <= 14 and simple_hits >= 1 and len(features) <= 1:
            complexity = ComplexityLevel.SIMPLE
        else:
            complexity = ComplexityLevel.MODERATE

        metadata = {
            'requirement_count': clauses,
            'complexity_score': round(
                max(0.0, min(1.0, (clauses + complex_hits * 2 + len(features)) / 12)), 2
            ),
            'detected_features': features,
            'has_data': 'stats' in features,
            'has_interaction': 'form' in features,
            'has_visualization': 'chart' in features,
            'word_count': words,
        }
        return complexity, metadata


class PromptCache:
    """Caches finished designs so repeat prompts cost zero tokens."""

    def __init__(self, enable: bool = True, ttl: int = 86400):
        self.enable = enable
        self.ttl = ttl

    def get_key(self, prompt: str, canvas_w: int, canvas_h: int, style: str) -> str:
        key_data = f"{prompt}:{canvas_w}:{canvas_h}:{style}"
        return f"design_spec_v2:{hashlib.md5(key_data.encode()).hexdigest()}"

    def get(self, prompt: str, canvas_w: int, canvas_h: int, style: str) -> Optional[Dict]:
        if not self.enable:
            return None
        cached = cache.get(self.get_key(prompt, canvas_w, canvas_h, style))
        if cached:
            logger.info('Design cache hit - no tokens spent')
        return cached

    def set(self, prompt: str, canvas_w: int, canvas_h: int, style: str, result: Dict) -> None:
        if not self.enable:
            return
        cache.set(self.get_key(prompt, canvas_w, canvas_h, style), result, self.ttl)


class _SpecAgent:
    """Shared plumbing for agents that request a semantic spec."""

    strategy = 'simple'
    tokens_estimated = 700

    def __init__(self, gateway):
        self.gateway = gateway

    def _request_spec(self, system_prompt: str, user_prompt: str,
                      temperature: float) -> Dict[str, Any]:
        result = self.gateway.generate_json_response(system_prompt, user_prompt, temperature)
        if isinstance(result, dict):
            return result
        logger.warning('%s agent: model returned %s instead of an object',
                       self.strategy, type(result).__name__)
        return {}

    def _compose(self, spec: Dict[str, Any], config: SmartConfig,
                 extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        design = compose_layout(
            spec,
            config.canvas_width,
            config.canvas_height,
            prompt=config.prompt,
            accent_override=config.accent(),
        )
        design['metadata'].update({
            'strategy': self.strategy,
            'tokens_estimated': self.tokens_estimated,
        })
        if extra:
            design['metadata'].update(extra)
        return design


class SimpleDesignAgent(_SpecAgent):
    """One compact call for straightforward screens."""

    strategy = 'simple'
    tokens_estimated = 700

    def generate(self, config: SmartConfig) -> Dict[str, Any]:
        logger.info('Using SIMPLE strategy (~700 tokens)')
        user_prompt = (
            f"Request: {config.prompt}\n"
            f"Visual style: {config.style}\n"
            "Choose the shell and 2-4 sections that best fit. Return the JSON spec."
        )
        try:
            spec = self._request_spec(SPEC_RULES, user_prompt, 0.5)
        except Exception as exc:
            logger.error('Simple spec generation failed: %s', exc)
            spec = {}
        return self._compose(spec, config, {'spec_received': bool(spec)})


class ModerateDesignAgent(_SpecAgent):
    """Single richer call - detailed content in one pass beats a brittle
    multi-stage pipeline and costs fewer tokens."""

    strategy = 'moderate'
    tokens_estimated = 1400

    def generate(self, config: SmartConfig) -> Dict[str, Any]:
        logger.info('Using MODERATE strategy (~1400 tokens)')
        user_prompt = (
            f"Request: {config.prompt}\n"
            f"Visual style: {config.style}\n"
            "Design a complete, realistic screen with 3-5 sections.\n"
            "Fill every section with domain-appropriate content: real metric names and\n"
            "plausible numbers for stat_row, weekday or month labels for chart, concrete\n"
            "event descriptions with relative timestamps for list.\n"
            "Pick an accent hex colour that suits the subject. Return the JSON spec."
        )
        try:
            spec = self._request_spec(SPEC_RULES, user_prompt, 0.6)
        except Exception as exc:
            logger.error('Moderate spec generation failed: %s', exc)
            spec = {}
        return self._compose(spec, config, {'spec_received': bool(spec)})


class AdvancedDesignAgent(_SpecAgent):
    """Two calls: pick the structure, then write the content for it."""

    strategy = 'advanced'
    tokens_estimated = 2600

    def generate(self, config: SmartConfig) -> Dict[str, Any]:
        logger.info('Using ADVANCED strategy (~2600 tokens)')

        structure = self._plan_structure(config)
        spec = self._write_content(config, structure)

        # Content pass is the richer of the two; fall back to the plan if it failed.
        if not (spec.get('sections') if isinstance(spec, dict) else None):
            spec = structure

        design = self._compose(spec, config, {
            'structure_received': bool(structure.get('sections')),
            'content_received': bool(isinstance(spec, dict) and spec.get('sections')),
        })
        design['metadata']['quality_score'] = self._score(design)
        return design

    def _plan_structure(self, config: SmartConfig) -> Dict[str, Any]:
        system_prompt = (
            "You are an information architect. Decide the shell and the ordered list of\n"
            "section types for a UI request. Do not write final content yet and never\n"
            "output coordinates or sizes.\n\n"
            "Return ONLY JSON:\n"
            '{"shell": "sidebar"|"topbar"|"plain", "brand": "...", "page_title": "...",\n'
            ' "nav": [...], "accent": "#RRGGBB",\n'
            ' "sections": [{"type": "...", "title": "...", "purpose": "one line"}]}\n\n'
            "Section types available:\n" + SECTION_MENU + "\n\n"
            "Use 3-5 sections. Order them by importance, top to bottom."
        )
        user_prompt = (
            f"Request: {config.prompt}\n"
            f"Visual style: {config.style}\n"
            "Plan the structure."
        )
        try:
            return self._request_spec(system_prompt, user_prompt, 0.4)
        except Exception as exc:
            logger.error('Structure planning failed: %s', exc)
            return {}

    def _write_content(self, config: SmartConfig, structure: Dict[str, Any]) -> Dict[str, Any]:
        plan = normalize_spec(structure, config.prompt)
        outline = ', '.join(
            f"{s.get('type')}" + (f" ({s['title']})" if s.get('title') else '')
            for s in plan['sections']
        )
        user_prompt = (
            f"Request: {config.prompt}\n"
            f"Visual style: {config.style}\n"
            f"Approved shell: {plan['shell']}\n"
            f"Approved sections in order: {outline}\n\n"
            "Keep that shell and that section order. Fill in every field with specific,\n"
            "domain-accurate content and plausible numbers. Return the complete JSON spec."
        )
        try:
            return self._request_spec(SPEC_RULES, user_prompt, 0.6)
        except Exception as exc:
            logger.error('Content generation failed: %s', exc)
            return {}

    def _score(self, design: Dict[str, Any]) -> float:
        """Structural quality check. Geometry is engine-guaranteed, so this
        measures richness: section variety, content density, colour use."""
        components = design.get('components', [])
        section_types = design.get('metadata', {}).get('section_types', [])
        if not components:
            return 0.0

        checks = [
            min(1.0, len(components) / 24.0),
            min(1.0, len(section_types) / 4.0),
            1.0 if len(set(section_types)) >= 3 else 0.5,
            min(1.0, len({
                c.get('style', {}).get('fill')
                for c in components if c.get('style', {}).get('fill')
            }) / 5.0),
            min(1.0, len([c for c in components if c.get('type') == 'text']) / 12.0),
        ]
        return round(sum(checks) / len(checks), 3)


class SmartDesignRouter:
    """Routes each prompt to the cheapest agent that can do it justice."""

    def __init__(self, gateway):
        self.gateway = gateway
        self.analyzer = ComplexityAnalyzer()
        self.cache = PromptCache(enable=True)
        self.simple_agent = SimpleDesignAgent(gateway)
        self.moderate_agent = ModerateDesignAgent(gateway)
        self.advanced_agent = AdvancedDesignAgent(gateway)

    def generate(self, config: SmartConfig) -> Dict[str, Any]:
        self.cache.enable = config.enable_caching
        cached = self.cache.get(
            config.prompt, config.canvas_width, config.canvas_height, config.style
        )
        if cached:
            return cached

        complexity, metadata = self.analyzer.analyze(config.prompt)
        if config.complexity_override:
            complexity = config.complexity_override
        logger.info('Complexity level: %s', complexity.value)

        agent = {
            ComplexityLevel.SIMPLE: self.simple_agent,
            ComplexityLevel.MODERATE: self.moderate_agent,
            ComplexityLevel.COMPLEX: self.advanced_agent,
        }[complexity]

        try:
            result = agent.generate(config)
        except Exception as exc:
            logger.error('Agent %s failed, composing default layout: %s',
                         complexity.value, exc)
            result = compose_layout(
                {}, config.canvas_width, config.canvas_height,
                prompt=config.prompt, accent_override=config.accent(),
            )
            result['metadata']['strategy'] = 'engine_default'

        result.setdefault('metadata', {}).update(metadata)
        result['metadata']['complexity_level'] = complexity.value

        self.cache.set(
            config.prompt, config.canvas_width, config.canvas_height,
            config.style, result,
        )

        logger.info(
            'Design complete - strategy=%s tokens~%s components=%d sections=%s',
            result['metadata'].get('strategy'),
            result['metadata'].get('tokens_estimated'),
            len(result.get('components', [])),
            result['metadata'].get('section_types'),
        )
        return result


def get_smart_router(gateway) -> SmartDesignRouter:
    return SmartDesignRouter(gateway)
