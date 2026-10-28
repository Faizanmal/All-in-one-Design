"""
Enhanced AI Generation Engine
Professional-grade AI generation for Logo, Graphics, and UI/UX with structured placement
Integrates with Smart Router for intelligent strategy selection
"""
import os
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class DesignCategory(Enum):
    """Design categories with specific generation rules"""
    LOGO = "logo"
    GRAPHIC = "graphic"
    UI_UX = "ui_ux"
    PRESENTATION = "presentation"
    SOCIAL_MEDIA = "social_media"


class PlacementStrategy(Enum):
    """Strategies for element placement"""
    GRID = "grid"
    CENTERED = "centered"
    LAYERED = "layered"
    FLOW = "flow"
    SYMMETRICAL = "symmetrical"


@dataclass
class GenerationConfig:
    """Configuration for AI generation"""
    category: DesignCategory
    prompt: str
    canvas_width: int = 1920
    canvas_height: int = 1080
    style: str = "modern"
    color_scheme: Optional[List[str]] = None
    placement_strategy: PlacementStrategy = PlacementStrategy.GRID
    include_guidelines: bool = True
    include_variations: bool = True


class EnhancedGenerationEngine:
    """
    Enhanced generation engine with structured placement and professional features
    Uses Smart Router for UI/UX generation
    """
    
    def __init__(self):
        from .resilient_gateway import get_resilient_gateway
        self.gateway = get_resilient_gateway()
        self.default_model = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
    
    def generate_design(self, config: GenerationConfig) -> Dict[str, Any]:
        """
        Generate design with professional structure and placement
        """
        try:
            # Generate based on category
            if config.category == DesignCategory.LOGO:
                return self._generate_logo(config)
            elif config.category == DesignCategory.GRAPHIC:
                return self._generate_graphic(config)
            elif config.category == DesignCategory.UI_UX:
                return self._generate_ui_ux(config)
            elif config.category == DesignCategory.PRESENTATION:
                return self._generate_presentation(config)
            elif config.category == DesignCategory.SOCIAL_MEDIA:
                return self._generate_social_media(config)
            else:
                raise ValueError(f"Unknown category: {config.category}")
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return self._get_fallback_structure(config)

    def _generate_logo(self, config: GenerationConfig) -> Dict[str, Any]:
        """Generate logos via semantic brief + deterministic centered layout."""
        from .logo_layout_engine import compose_logo

        system_prompt = """You are a brand identity designer. Describe a logo concept.
You NEVER output coordinates, sizes, or pixel values.

Return ONLY a JSON object:
{
  "brand": "exact company name",
  "tagline": "" or short tagline,
  "mark": "mountain" | "abstract" | "circle" | "letter" | "hexagon",
  "primary": "#HEX",
  "secondary": "#HEX",
  "background": "#HEX"
}

mark guidance:
- "mountain": outdoor, peaks, adventure, geo brands
- "abstract": tech, labs, startups, energy
- "circle": eco, organic, wellness
- "letter": luxury, fashion, monogram / wordmark-led
- "hexagon": industrial, mobility, structured brands

Rules:
- If the request quotes a brand name or hex colors, use them VERBATIM.
- Leave tagline empty unless the request asks for one.
- Prefer a clean light or white background unless the request asks for dark.
- Output raw JSON only, no markdown."""

        user_prompt = f"""Request: {config.prompt}
Visual style: {config.style}
{f'Preferred palette: {", ".join(config.color_scheme)}' if config.color_scheme else ''}
Return the JSON logo brief."""

        try:
            try:
                raw = self.gateway.generate_json_response(system_prompt, user_prompt, temperature=0.55)
            except Exception as exc:
                logger.warning('Logo spec call failed (%s); composing from prompt defaults', exc)
                raw = {}
            if not isinstance(raw, dict):
                raw = {}

            result = compose_logo(
                raw,
                config.canvas_width,
                config.canvas_height,
                prompt=config.prompt,
                color_scheme=config.color_scheme,
            )
            metadata = result.setdefault('metadata', {})
            metadata['strategy'] = 'logo_engine'
            metadata['spec_received'] = bool(raw)
            return result
        except Exception as e:
            logger.error(f"Logo generation failed: {e}")
            try:
                return compose_logo(
                    {}, config.canvas_width, config.canvas_height,
                    prompt=config.prompt, color_scheme=config.color_scheme,
                )
            except Exception:
                return self._get_fallback_structure(config)
    
    def _generate_graphic(self, config: GenerationConfig) -> Dict[str, Any]:
        """Generate marketing graphics via semantic spec + layout engine.

        The model only chooses format, copy and palette. Asking it for absolute
        pixel coordinates produced the sparse posters with tiny CTAs and
        floating decorative shapes. Geometry is owned by graphic_layout_engine.
        """
        from .graphic_layout_engine import compose_graphic

        system_prompt = """You are a senior art director. Describe a marketing graphic.
You NEVER output coordinates, sizes, or pixel values.

Return ONLY a JSON object:
{
  "format": "split" | "stacked" | "centered" | "banner",
  "brand": "brand or product name",
  "headline": "full campaign headline",
  "subhead": "one supporting sentence",
  "cta": "button label (2-4 words)",
  "media_label": "short image caption",
  "accent": "#HEX",
  "background": "#HEX"
}

format guidance:
- "split": social post / product launch (copy left, media right) — default for most ads
- "stacked": poster, story, flyer (media on top, copy below)
- "centered": elegant minimal announcement
- "banner": wide web / email header

Copy rules (critical):
- If the request quotes a headline, brand, CTA, or supporting line, copy them VERBATIM.
- Do NOT shorten, rewrite, or drop words from quoted copy.
- Headline may be up to 12 words / two short lines. Prefer the full campaign line over a truncated slogan.
- Subhead should be a complete sentence (8-20 words) when the request provides supporting copy.
- Prefer a strong filled background (deep charcoal, navy, warm cream, forest) over plain white.
- Accent must contrast the background.
- Output raw JSON only, no markdown."""

        user_prompt = f"""Request: {config.prompt}
Visual style: {config.style}
{f'Preferred palette: {", ".join(config.color_scheme)}' if config.color_scheme else ''}
Preserve any quoted headline/brand/CTA from the request exactly. Return the JSON creative brief."""

        try:
            try:
                raw = self.gateway.generate_json_response(system_prompt, user_prompt, temperature=0.6)
            except Exception as exc:
                logger.warning('Graphic spec call failed (%s); composing from prompt defaults', exc)
                raw = {}

            if not isinstance(raw, dict):
                raw = {}

            result = compose_graphic(
                raw,
                config.canvas_width,
                config.canvas_height,
                prompt=config.prompt,
                color_scheme=config.color_scheme,
            )
            metadata = result.setdefault('metadata', {})
            metadata['strategy'] = 'graphic_engine'
            metadata['spec_received'] = bool(raw)
            return result
        except Exception as e:
            logger.error(f"Graphic generation failed: {e}")
            try:
                return compose_graphic(
                    {}, config.canvas_width, config.canvas_height,
                    prompt=config.prompt, color_scheme=config.color_scheme,
                )
            except Exception:
                return self._get_fallback_structure(config)
    
    def _generate_ui_ux(self, config: GenerationConfig) -> Dict[str, Any]:
        """Generate UI/UX via the smart router.

        The router returns geometry from the deterministic layout engine, which
        is already exact, in-bounds and non-overlapping. The generic post-passes
        must NOT run on it: they clamp every element to x,y >= 16 (which shifts
        full-bleed backgrounds and the sidebar), re-estimate sizes, rescale to a
        target fill, and treat a label nested inside a card as an overlap to be
        pushed below it - which is what shattered these layouts previously.
        """
        from .smart_router import get_smart_router, SmartConfig
        from .layout_engine import compose_layout

        try:
            smart_config = SmartConfig(
                prompt=config.prompt,
                canvas_width=config.canvas_width,
                canvas_height=config.canvas_height,
                style=config.style,
                color_scheme=config.color_scheme,
                enable_caching=True,
            )

            router = get_smart_router(self.gateway)
            result = router.generate(smart_config)

            if not result.get('components'):
                logger.warning('Smart router returned no components, composing default layout')
                result = compose_layout(
                    {}, config.canvas_width, config.canvas_height, prompt=config.prompt
                )

            metadata = result.setdefault('metadata', {})
            if metadata.get('layout_mode') != 'ui_shell':
                # Not engine geometry - fall back to the legacy correction passes.
                result = self._normalize_component_sizes(result)
                result = self._validate_alignment(result, config)
                result = self._ensure_bounds(result, config, scale_to_fit=True, target_fill=0.90)
                result = self._snap_components_to_grid(result, grid_size=8)
                metadata = result.setdefault('metadata', {})

            metadata['canvas_width'] = config.canvas_width
            metadata['canvas_height'] = config.canvas_height
            metadata['category'] = 'ui_ux'

            return result
        except Exception as e:
            logger.error(f"Smart UI/UX generation failed: {e}")
            try:
                return compose_layout(
                    {}, config.canvas_width, config.canvas_height, prompt=config.prompt
                )
            except Exception:
                return self._get_fallback_structure(config)

    def _generate_presentation(self, config: GenerationConfig) -> Dict[str, Any]:
        """Generate professional presentation slide layout"""
        system_prompt = """You are a master presentation designer.
Create clear, high-impact slide layouts.

PRINCIPLES:
1. **Clarity**: Keep text minimal (max 6 lines per slide).
2. **Visuals**: Use icons, data visualizations, or imagery to support points.
3. **Structure**: Title at top, content centered or split-screen.

Return ONLY valid JSON with this exact structure:
{
  "components": [
    {
      "type": "text|shape|image|icon|chart",
      "subtype": "title|subtitle|body|bullet|background|infographic",
      "content": "text content or data points",
      "position": {"x": number, "y": number},
      "size": {"width": number, "height": number},
      "style": { "fill": "#HEX", "fontSize": number, "fontFamily": "font name", "fontWeight": "bold|normal" },
      "layer": number
    }
  ],
  "layout": { "type": "slide" }
}"""
        
        user_prompt = f"""Design a presentation slide for: "{config.prompt}"
Specifications:
- Canvas: {config.canvas_width}x{config.canvas_height}
- Style: {config.style}
{f"- Palette: {', '.join(config.color_scheme)}" if config.color_scheme else ""}
"""
        try:
            result = self.gateway.generate_json_response(system_prompt, user_prompt, temperature=0.7)
            if 'components' not in result:
                logger.warning("No components in result, using fallback")
                return self._get_fallback_structure(config)
            result = self._normalize_component_sizes(result)
            result = self._ensure_bounds(result, config, scale_to_fit=True, target_fill=0.9)
            result = self._snap_components_to_grid(result, grid_size=8)
            return result
        except Exception as e:
            logger.error(f"Presentation generation failed: {e}")
            return self._get_fallback_structure(config)

    def _generate_social_media(self, config: GenerationConfig) -> Dict[str, Any]:
        """Generate high-engagement social media post layout"""
        system_prompt = """You are an expert social media designer.
Create eye-catching, high-converting social media posts.

Return ONLY valid JSON with this exact structure:
{
  "components": [
    {
      "type": "text|shape|image",
      "subtype": "header|call_to_action|background|graphic",
      "content": "text content",
      "position": {"x": number, "y": number},
      "size": {"width": number, "height": number},
      "style": { "fill": "#HEX", "fontSize": number, "fontFamily": "font name", "fontWeight": "bold|normal" },
      "layer": number
    }
  ],
  "layout": { "type": "social_post" }
}"""
        
        user_prompt = f"""Design a social media post for: "{config.prompt}"
Specifications:
- Canvas: {config.canvas_width}x{config.canvas_height}
- Style: {config.style}
{f"- Palette: {', '.join(config.color_scheme)}" if config.color_scheme else ""}
"""
        try:
            result = self.gateway.generate_json_response(system_prompt, user_prompt, temperature=0.7)
            if 'components' not in result:
                logger.warning("No components in result, using fallback")
                return self._get_fallback_structure(config)
            result = self._normalize_component_sizes(result)
            result = self._apply_placement_strategy(result, config)
            result = self._ensure_bounds(result, config, scale_to_fit=True, target_fill=0.92)
            result = self._snap_components_to_grid(result, grid_size=8)
            return result
        except Exception as e:
            logger.error(f"Social media generation failed: {e}")
            return self._get_fallback_structure(config)
    
    def _estimate_component_size(self, component: Dict) -> tuple:
        """Return (width, height), estimating text when size is missing/wrong."""
        size = component.get('size') or {}
        width = float(size.get('width') or 0)
        height = float(size.get('height') or 0)
        style = component.get('style') or {}
        ctype = (component.get('type') or '').lower()
        subtype = (component.get('subtype') or '').lower()

        if ctype in ('text', 'header', 'footer', 'navigation') or subtype in ('header', 'wordmark', 'tagline'):
            font_size = float(style.get('fontSize') or 16)
            content = str(component.get('content') or '')
            if width <= 0:
                width = max(40.0, len(content) * font_size * 0.55)
            if height <= 0:
                height = font_size * 1.35
        elif subtype == 'circle' or ctype in ('icon', 'symbol'):
            # Circles are stored as bounding boxes; keep square
            side = max(width, height, 40.0)
            if width <= 0 or height <= 0:
                width = height = side
            else:
                width = height = min(width, height)
        else:
            if width <= 0:
                width = 100.0
            if height <= 0:
                height = 100.0

        return width, height

    def _normalize_component_sizes(self, result: Dict, default_text_align: str = 'center') -> Dict:
        """Fill missing/invalid sizes so centering math is trustworthy."""
        for component in result.get('components', []):
            if not isinstance(component, dict):
                continue
            pos = component.setdefault('position', {'x': 0, 'y': 0})
            pos['x'] = float(pos.get('x') or 0)
            pos['y'] = float(pos.get('y') or 0)
            width, height = self._estimate_component_size(component)
            component['size'] = {'width': width, 'height': height}
            style = component.setdefault('style', {})
            ctype = (component.get('type') or '').lower()
            if ctype in ('text', 'header', 'footer') and not style.get('textAlign'):
                style['textAlign'] = default_text_align
        return result

    def _apply_logo_positioning(self, result: Dict, config: GenerationConfig) -> Dict:
        """Center the logo group on the canvas using estimated real bounds."""
        components = [c for c in result.get('components', []) if isinstance(c, dict)]
        if not components:
            return result

        bounds = self._component_bounds(components)
        if not bounds:
            return result

        min_x, min_y, max_x, max_y = bounds
        current_center_x = (min_x + max_x) / 2
        current_center_y = (min_y + max_y) / 2
        offset_x = (config.canvas_width / 2) - current_center_x
        offset_y = (config.canvas_height / 2) - current_center_y

        for component in components:
            component['position']['x'] += offset_x
            component['position']['y'] += offset_y

        return result

    def _apply_placement_strategy(self, result: Dict, config: GenerationConfig) -> Dict:
        """Dispatch to the configured placement strategy."""
        strategy = config.placement_strategy
        if strategy in (PlacementStrategy.CENTERED, PlacementStrategy.SYMMETRICAL):
            return self._position_centered(result, config)
        if strategy == PlacementStrategy.GRID:
            return self._position_in_grid(result, config)
        if strategy == PlacementStrategy.LAYERED:
            return self._position_layered(result, config)
        if strategy == PlacementStrategy.FLOW:
            return self._position_flow(result, config)
        return result

    def _position_in_grid(self, result: Dict, config: GenerationConfig) -> Dict:
        """Nudge elements onto an 8px rhythm without destroying relative layout."""
        return self._snap_components_to_grid(result, grid_size=8)

    def _position_centered(self, result: Dict, config: GenerationConfig) -> Dict:
        """Center all elements as a group"""
        return self._apply_logo_positioning(result, config)

    def _position_layered(self, result: Dict, config: GenerationConfig) -> Dict:
        """Keep relative positions; only normalize sizes (depth via layer)."""
        return result

    def _position_flow(self, result: Dict, config: GenerationConfig) -> Dict:
        """Stack non-background elements vertically with consistent gaps."""
        components = [c for c in result.get('components', []) if isinstance(c, dict)]
        if len(components) < 2:
            return result

        def is_background(c: Dict) -> bool:
            ctype = (c.get('type') or '').lower()
            subtype = (c.get('subtype') or '').lower()
            return ctype in ('background',) or subtype in ('background',)

        foreground = [c for c in components if not is_background(c)]
        foreground.sort(key=lambda c: (c['position']['y'], c['position']['x']))

        gap = 24
        padding = 48
        cursor_y = padding
        for component in foreground:
            width = component['size']['width']
            component['position']['x'] = max(padding, (config.canvas_width - width) / 2)
            component['position']['y'] = cursor_y
            cursor_y += component['size']['height'] + gap

        return result

    def _snap_components_to_grid(self, result: Dict, grid_size: int = 8) -> Dict:
        """Snap component positions (and sizes) to a grid."""
        for component in result.get('components', []):
            if not isinstance(component, dict):
                continue
            pos = component.get('position') or {}
            size = component.get('size') or {}
            pos['x'] = round(float(pos.get('x', 0)) / grid_size) * grid_size
            pos['y'] = round(float(pos.get('y', 0)) / grid_size) * grid_size
            if size.get('width'):
                size['width'] = max(grid_size, round(float(size['width']) / grid_size) * grid_size)
            if size.get('height'):
                size['height'] = max(grid_size, round(float(size['height']) / grid_size) * grid_size)
            component['position'] = pos
            component['size'] = size
        return result

    def _validate_alignment(self, result: Dict, config: GenerationConfig) -> Dict:
        """Validate and fix component alignment issues."""
        components = result.get('components', [])
        if not components:
            return result
        
        canvas_w = float(config.canvas_width)
        canvas_h = float(config.canvas_height)
        min_padding = 16
        min_gap = 12
        
        # Check for overlaps and misalignments
        for i, comp in enumerate(components):
            if not isinstance(comp, dict):
                continue
            
            pos = comp.get('position', {})
            size = comp.get('size', {})
            x = float(pos.get('x', 0))
            y = float(pos.get('y', 0))
            w = float(size.get('width', 0))
            h = float(size.get('height', 0))
            
            # Enforce minimum padding from edges
            if x < min_padding:
                x = min_padding
            if y < min_padding:
                y = min_padding
            if x + w > canvas_w - min_padding:
                x = max(min_padding, canvas_w - min_padding - w)
            if y + h > canvas_h - min_padding:
                y = max(min_padding, canvas_h - min_padding - h)
            
            comp['position']['x'] = x
            comp['position']['y'] = y
            
            # Check for overlaps with other components and fix
            for j, other in enumerate(components):
                if i >= j or not isinstance(other, dict):
                    continue
                
                other_pos = other.get('position', {})
                other_size = other.get('size', {})
                ox = float(other_pos.get('x', 0))
                oy = float(other_pos.get('y', 0))
                ow = float(other_size.get('width', 0))
                oh = float(other_size.get('height', 0))
                
                # Check if components overlap
                if not (x + w + min_gap < ox or ox + ow + min_gap < x or 
                        y + h + min_gap < oy or oy + oh + min_gap < y):
                    # They overlap, shift current component down
                    y = oy + oh + min_gap
                    comp['position']['y'] = y
        
        return result

    def _ensure_bounds(
        self,
        result: Dict,
        config: GenerationConfig,
        scale_to_fit: bool = False,
        target_fill: float = 0.9,
        padding: float = None,
        max_enlarge: float = 2.5,
        always_center: bool = False,
    ) -> Dict:
        """Clamp / optionally scale content so it fits and stays centered."""
        components = [c for c in result.get('components', []) if isinstance(c, dict)]
        if not components:
            return result

        canvas_w = float(config.canvas_width)
        canvas_h = float(config.canvas_height)
        pad = padding if padding is not None else min(canvas_w, canvas_h) * 0.04
        bounds = self._component_bounds(components, canvas_w, canvas_h)
        if not bounds:
            return result

        min_x, min_y, max_x, max_y = bounds
        content_w = max(1.0, max_x - min_x)
        content_h = max(1.0, max_y - min_y)
        max_w = max(1.0, canvas_w - 2 * pad)
        max_h = max(1.0, canvas_h - 2 * pad)

        scale = 1.0
        if scale_to_fit:
            if content_w > max_w or content_h > max_h:
                scale = min(max_w / content_w, max_h / content_h)
            elif target_fill and content_w < max_w * target_fill and content_h < max_h * target_fill:
                enlarge = min((max_w * target_fill) / content_w, (max_h * target_fill) / content_h)
                if enlarge > 1.0 and enlarge <= max_enlarge:
                    scale = enlarge

        foreground = [
            c for c in components
            if not self._is_page_background(c, canvas_w, canvas_h)
        ]
        scalable = foreground if foreground else components

        if scale != 1.0:
            center_x = (min_x + max_x) / 2
            center_y = (min_y + max_y) / 2
            for component in scalable:
                pos = component['position']
                size = component['size']
                pos['x'] = center_x + (pos['x'] - center_x) * scale
                pos['y'] = center_y + (pos['y'] - center_y) * scale
                size['width'] *= scale
                size['height'] *= scale
                style = component.get('style') or {}
                if style.get('fontSize'):
                    style['fontSize'] = max(8, round(float(style['fontSize']) * scale))
                if style.get('strokeWidth'):
                    style['strokeWidth'] = max(0, float(style['strokeWidth']) * scale)

        if scale != 1.0 or always_center:
            # Re-center foreground group; keep page backgrounds pinned
            bounds = self._component_bounds(scalable, canvas_w, canvas_h)
            if bounds:
                min_x, min_y, max_x, max_y = bounds
                offset_x = (canvas_w / 2) - ((min_x + max_x) / 2)
                offset_y = (canvas_h / 2) - ((min_y + max_y) / 2)
                for component in scalable:
                    component['position']['x'] += offset_x
                    component['position']['y'] += offset_y

        # Re-pin full-bleed backgrounds after transforms
        for component in components:
            if self._is_page_background(component, canvas_w, canvas_h):
                component['position'] = {'x': 0, 'y': 0}
                component['size'] = {'width': canvas_w, 'height': canvas_h}
                component.setdefault('style', {})
                component['style']['opacity'] = component['style'].get('opacity', 1) or 1

        # Final clamp so nothing sits outside the canvas
        for component in scalable:
            pos = component['position']
            size = component['size']
            width = size.get('width', 0)
            height = size.get('height', 0)
            pos['x'] = min(max(0, pos['x']), max(0, canvas_w - width))
            pos['y'] = min(max(0, pos['y']), max(0, canvas_h - height))

        return result
    
    @staticmethod
    def _is_page_background(component: Dict, canvas_w: float, canvas_h: float) -> bool:
        subtype = (component.get('subtype') or '').lower()
        ctype = (component.get('type') or '').lower()
        size = component.get('size') or {}
        pos = component.get('position') or {}
        try:
            cw = float(size.get('width') or 0)
            ch = float(size.get('height') or 0)
            x = float(pos.get('x') or 0)
            y = float(pos.get('y') or 0)
        except (TypeError, ValueError):
            return False
        if subtype in ('background', 'page') or ctype == 'background':
            return True
        return (
            ctype in ('rectangle', 'rect', 'shape')
            and x <= 8 and y <= 8
            and cw >= canvas_w * 0.9
            and ch >= canvas_h * 0.9
        )

    def _component_bounds(self, components: List[Dict], canvas_w: float = 0, canvas_h: float = 0) -> Optional[tuple]:
        if not components:
            return None
        # Prefer foreground bounds so full-bleed backgrounds don't fake "already full"
        if canvas_w and canvas_h:
            foreground = [
                c for c in components
                if not self._is_page_background(c, canvas_w, canvas_h)
            ]
            use = foreground if foreground else components
        else:
            use = [
                c for c in components
                if (c.get('subtype') or '').lower() not in ('background', 'page')
            ] or components

        min_x = min(c['position']['x'] for c in use)
        min_y = min(c['position']['y'] for c in use)
        max_x = max(c['position']['x'] + c['size']['width'] for c in use)
        max_y = max(c['position']['y'] + c['size']['height'] for c in use)
        return min_x, min_y, max_x, max_y
    
    def _get_fallback_structure(self, config: Optional[GenerationConfig] = None) -> Dict[str, Any]:
        """Get fallback structure when generation fails"""
        width = config.canvas_width if config else 1920
        height = config.canvas_height if config else 1080
        
        return {
            "components": [
                {
                    "type": "text",
                    "subtype": "header",
                    "content": "Design Generation Failed",
                    "position": {"x": width // 2 - 200, "y": height // 2 - 50},
                    "size": {"width": 400, "height": 60},
                    "style": {
                        "fontSize": 48,
                        "fontFamily": "Inter, Arial, sans-serif",
                        "fontWeight": "bold",
                        "fill": "#EF4444",
                        "textAlign": "center"
                    },
                    "layer": 10
                },
                {
                    "type": "text",
                    "subtype": "message",
                    "content": "Please check your AI configuration or try again.",
                    "position": {"x": width // 2 - 250, "y": height // 2 + 30},
                    "size": {"width": 500, "height": 40},
                    "style": {
                        "fontSize": 24,
                        "fontFamily": "Inter, Arial, sans-serif",
                        "fontWeight": "normal",
                        "fill": "#6B7280",
                        "textAlign": "center"
                    },
                    "layer": 10
                },
                {
                    "type": "rectangle",
                    "subtype": "background",
                    "position": {"x": 50, "y": 50},
                    "size": {"width": width - 100, "height": height - 100},
                    "style": {
                        "fill": "#F9FAFB",
                        "stroke": "#E5E7EB",
                        "strokeWidth": 2,
                        "rx": 16,
                        "ry": 16
                    },
                    "layer": 0
                }
            ],
            "metadata": {
                "status": "fallback",
                "message": "Generated with fallback structure due to processing error"
            }
        }


# Singleton instance
_engine = None

def get_generation_engine() -> EnhancedGenerationEngine:
    """Get singleton instance of generation engine"""
    global _engine
    if _engine is None:
        _engine = EnhancedGenerationEngine()
    return _engine
