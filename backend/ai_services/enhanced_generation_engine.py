"""
Enhanced AI Generation Engine
Professional-grade AI generation for Logo, Graphics, and UI/UX with structured placement
"""
import os
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from groq import Groq

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
    """
    
    def __init__(self):
        groq_api_key = os.getenv('GROQ_API_KEY')
        self.client = None
        if groq_api_key:
            try:
                self.client = Groq(api_key=groq_api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
        else:
            logger.warning("GROQ_API_KEY is not set. Using fallback generation.")
            
        self.default_model = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
    
    def generate_design(self, config: GenerationConfig) -> Dict[str, Any]:
        """
        Generate design with professional structure and placement
        """
        if not self.client:
            logger.info("Using fallback generation (no client)")
            return self._get_fallback_structure(config)

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
    

    
    # ... (other methods exist but I'm only modifying up to the start of _apply_logo_positioning, 
    # but I need to make sure I don't delete them. The replacement chunk handles up to the end of _get_fallback_structure)
    # Wait, the tool definition says "This must be a complete drop-in replacement of the TargetContent".
    # I should be careful not to delete methods I don't include.
    # The previous Read showed methods _apply_logo_positioning, _apply_graphic_positioning, _apply_ui_positioning etc.
    # I need to keep them or include them in the chunk.
    # Since I'm using "StartLine: 51, EndLine: 521", I am replacing almost the whole class body EXCEPT the _apply methods if they are in that range.
    # Let me check the line numbers again.
    # _apply_logo_positioning starts at line 353.
    # So if I replace 51 to 521, I AM replacing those methods.
    # I need to include them in the replacement content.
    
    # Alternatively, I can use two chunks:
    # 1. Replace __init__ and generate_design (lines 51-70)
    # 2. Replace _get_fallback_structure (lines 498-521)
    
    # AND I also need to update _extract_and_validate_json call in generate_logo etc because I changed _get_fallback_structure signature to accept config (optional?).
    
    # Let's refine the plan.
    # I will update __init__ and generate_design.
    # I will update _get_fallback_structure.
    # I will update the calls where _get_fallback_structure is called.
    
    # It seems better to replace specific chunks rather than the whole file.
    
    # Chunk 1: __init__ and generate_design
    # Chunk 2: _extract_and_validate_json (calls fallback)
    # Chunk 3: _get_fallback_structure
    
    # But wait, generate_logo etc also need to be wrapped in try/except or checked for self.client.
    
    # Let's do a large replacement for the methods I need to change.
    
    # I will check lines again.
    # __init__ is at 51.
    # generate_design is at 58.
    # _generate_logo is at 72.
    # _generate_graphic is at 151.
    # _generate_ui_ux is at 233.
    # _extract_and_validate_json is at 328.
    # _apply_logo_positioning is at 353.
    
    # I will replace from line 51 to 352. And then replace _get_fallback_structure at the end.
    # This covers __init__, generate_design, _generate_logo, _generate_graphic, _generate_ui_ux, _extract_and_validate_json.
    # I need to keep the implementations of _generate_* mostly intact but wrap them.
    
    # This is getting complicated with one tool call.
    # I'll use multi_replace_file_content.

    
    def _generate_logo(self, config: GenerationConfig) -> Dict[str, Any]:
        """Generate professional logo with structured elements"""
        if not self.client: return self._get_fallback_structure(config)
        
        system_prompt = """You are a world-class brand identity designer.
Create sophisticated, professional conceptual logos using geometric precision.

PRINCIPLES:
1. **Geometric Harmony**: Use combinations of basic shapes (circles, triangles, rects) to create meaningful symbols.
2. **Minimalism**: Less is more. Use negative space effectively.
3. **Typography**: The wordmark should use a font weight that complements the symbol.
4. **Hierarchy**: Symbol on the left, top, or centered. Text proportional to symbol.
5. **Color Theory**: Use the provided palette or generate a professional complementary palette.

Return ONLY valid JSON with this exact structure:
{
  "components": [
    {
      "type": "shape|text|icon",
      "subtype": "circle|triangle|star|rect|polygon|ellipse",
      "content": "text content if text type",
      "position": {"x": number, "y": number},
      "size": {"width": number, "height": number},
      "style": {
        "fill": "#HEX",
        "stroke": "#HEX",
        "strokeWidth": number,
        "fontSize": number,
        "fontFamily": "Inter, Roboto, Playfair Display, Montserrat",
        "fontWeight": "bold|normal|300|600",
        "rotation": number,
        "opacity": number,
        "letterSpacing": number
      },
      "layer": number
    }
  ],
  "metadata": {
    "logotype": "combination|wordmark|pictorial",
    "style": "geometric|minimalist|abstract",
    "color_palette": ["#HEX1", "#HEX2"]
  }
}"""
        
        user_prompt = f"""Design a high-end logo for: "{config.prompt}"
        
Specifications:
- Canvas: {config.canvas_width}x{config.canvas_height}
- Style: {config.style}
{f"- Brand Colors: {', '.join(config.color_scheme)}" if config.color_scheme else ""}

INSTRUCTIONS:
1. **Symbol**: Create a central symbol using 2-4 overlapping or adjacent 'shape' elements. Use different colors/opacities for depth.
2. **Wordmark**: Add the company name "{config.prompt}" as a 'text' element. Choose a font that matches the style (e.g., serif for luxury, sans-serif for tech).
3. **Tagline**: If appropriate for "{config.style}", add a tagline below.
4. **Composition**: Ensure the logo is centered.
5. **Spacing**: Maintain clear space between symbol and text.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"},
            )
            
            content = response.choices[0].message.content
            result = self._extract_and_validate_json(content, config)
            result = self._apply_logo_positioning(result, config)
            return result
        except Exception as e:
            logger.error(f"Logo generation failed: {e}")
            return self._get_fallback_structure(config)
    
    def _generate_graphic(self, config: GenerationConfig) -> Dict[str, Any]:
        """Generate professional graphic design with structured layout"""
        if not self.client: return self._get_fallback_structure(config)
        
        system_prompt = """You are a senior graphic designer creating high-impact layout designs.

PRINCIPLES:
1. **Visual Hierarchy**: Headline > Subheadline > Imagery > Call to Action.
2. **Composition**: Use the Rule of Thirds.
3. **Background**: Create depth using background shapes or patterns (circles/rectangles with low opacity).

Return ONLY valid JSON with this exact structure:
{
  "components": [
    {
      "type": "text|shape|image|button|rectangle",
      "subtype": "circle|triangle|star",
      "content": "text content",
      "position": {"x": number, "y": number},
      "size": {"width": number, "height": number},
      "style": {
        "fill": "#HEX",
        "stroke": "#HEX",
        "strokeWidth": number,
        "fontSize": number,
        "fontFamily": "font name",
        "fontWeight": "bold|normal",
        "textAlign": "left|center|right",
        "opacity": number,
        "borderRadius": number
      },
      "layer": number
    }
  ],
  "layout": { "type": "composition" }
}"""
        
        user_prompt = f"""Design a professional marketing graphic based on: "{config.prompt}"

Specifications:
- Canvas: {config.canvas_width}x{config.canvas_height}
- Style: {config.style}
{f"- Palette: {', '.join(config.color_scheme)}" if config.color_scheme else ""}

INSTRUCTIONS:
1. **Background**: Add a full-width background 'rectangle' with a main color. Add 1-2 large abstract 'shape' elements with low opacity for texture.
2. **Headline**: Large, bold 'text' element.
3. **Subhead**: Supporting 'text' below the headline.
4. **Imagery**: Add an 'image' placeholder.
5. **CTA Button**: A 'button' element.
6. **Decoration**: Add small decorative 'shape' elements.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"},
            )
            
            content = response.choices[0].message.content
            result = self._extract_and_validate_json(content, config)
            result = self._apply_graphic_positioning(result, config)
            return result
        except Exception as e:
            logger.error(f"Graphic generation failed: {e}")
            return self._get_fallback_structure(config)
    
    def _generate_ui_ux(self, config: GenerationConfig) -> Dict[str, Any]:
        """Generate professional UI/UX design with structured components"""
        if not self.client: return self._get_fallback_structure(config)
        
        system_prompt = """You are a Lead Product Designer creating high-fidelity, modern UI mockups.

PRINCIPLES:
1. **Atomic Design**: Build interfaces using atoms (buttons, inputs), molecules (forms, cards), and organisms (headers, sections).
2. **Visual Hierarchy**: Use size, color, and spacing to guide the eye. Important elements should stand out.
3. **Modern Aesthetics**: Use soft shadows, rounded corners, generous whitespace, and consistent typography.
4. **Content Realism**: NEVER use 'Lorem Ipsum'. Use realistic text relevant to the context.

Return ONLY valid JSON with this exact structure:
{
  "components": [
    {
      "type": "text|rectangle|image|button|input|icon|circle",
      "subtype": "header|hero|card_bg|button_bg|input_bg|profile_pic|icon_element",
      "content": "text content (for text) or icon-name (for icon)",
      "position": {"x": number, "y": number},
      "size": {"width": number, "height": number},
      "style": {
        "fill": "#HEX",
        "stroke": "#HEX",
        "strokeWidth": number,
        "borderRadius": number,
        "fontSize": number,
        "fontFamily": "Inter, Roboto, Open Sans",
        "fontWeight": "bold|500|normal",
        "shadow": {"color": "#00000020", "blur": 10, "x": 0, "y": 4},
        "opacity": number,
        "textAlign": "left|center|right"
      },
      "layer": number
    }
  ],
  "layout": { "type": "ui_mockup" }
}"""
        
        user_prompt = f"""Design a stunning, high-fidelity UI mockup for: "{config.prompt}"
        
Specifications:
- Canvas: {config.canvas_width}x{config.canvas_height}
- Style: {config.style}
{f"- Theme Colors: {', '.join(config.color_scheme)}" if config.color_scheme else ""}

INSTRUCTIONS:
1. **Navigation**: Create a top navigation bar (rectangle) with logo (text/icon) and menu items.
2. **Hero Section**: Large header text, subtext, and a prominent call-to-action button. Use an abstract shape or placeholder image for visual interest.
3. **Main Content**:
   - If dashboard: Add cards with stats (numbers + label) and a chart placeholder.
   - If landing page: Add value proposition cards or feature list.
4. **Detailing**: Add subtle shadows to cards and buttons. Use rounded corners (borderRadius: 8-16).
5. **Positioning**: EXPLICITLY set x, y coordinates to create a balanced layout. Ensure elements do not overlap unintentionally.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"},
            )
            
            content = response.choices[0].message.content
            result = self._extract_and_validate_json(content, config)
            result = self._apply_ui_positioning(result, config)
            return result
        except Exception as e:
            logger.error(f"UI/UX generation failed: {e}")
            return self._get_fallback_structure(config)

    def _generate_presentation(self, config: GenerationConfig) -> Dict[str, Any]:
        """Generate professional presentation slide layout"""
        if not self.client: return self._get_fallback_structure(config)
        
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
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                temperature=0.7,
                response_format={"type": "json_object"},
            )
            result = self._extract_and_validate_json(response.choices[0].message.content, config)
            return self._ensure_bounds(result, config)
        except Exception as e:
            logger.error(f"Presentation generation failed: {e}")
            return self._get_fallback_structure(config)

    def _generate_social_media(self, config: GenerationConfig) -> Dict[str, Any]:
        """Generate high-engagement social media post layout"""
        if not self.client: return self._get_fallback_structure(config)
        
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
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                temperature=0.7,
                response_format={"type": "json_object"},
            )
            result = self._extract_and_validate_json(response.choices[0].message.content, config)
            return self._ensure_bounds(result, config)
        except Exception as e:
            logger.error(f"Social media generation failed: {e}")
            return self._get_fallback_structure(config)
    
    def _extract_and_validate_json(self, content: str, config: Optional[GenerationConfig] = None) -> Dict[str, Any]:
        """Extract and validate JSON from AI response"""
        try:
            # Try to find JSON in the response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                logger.error("No JSON found in response")
                return self._get_fallback_structure(config)
            
            json_str = content[start_idx:end_idx]
            result = json.loads(json_str)
            
            # Validate required fields
            if 'components' not in result:
                logger.warning("No components in result, using fallback")
                return self._get_fallback_structure(config)
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return self._get_fallback_structure(config)
    
    def _apply_logo_positioning(self, result: Dict, config: GenerationConfig) -> Dict:
        """Apply centered, symmetrical positioning for logos"""
        components = result.get('components', [])
        
        if not components:
            return result
        
        # Calculate center
        center_x = config.canvas_width // 2
        center_y = config.canvas_height // 2
        
        # Find bounding box of all elements
        if len(components) > 0:
            min_x = min(c['position']['x'] for c in components)
            max_x = max(c['position']['x'] + c.get('size', {}).get('width', 0) for c in components)
            min_y = min(c['position']['y'] for c in components)
            max_y = max(c['position']['y'] + c.get('size', {}).get('height', 0) for c in components)
            
            # Calculate offset to center
            current_center_x = (min_x + max_x) / 2
            current_center_y = (min_y + max_y) / 2
            offset_x = center_x - current_center_x
            offset_y = center_y - current_center_y
            
            # Apply offset to all components
            for component in components:
                component['position']['x'] += offset_x
                component['position']['y'] += offset_y
        
        return result
    
    def _apply_graphic_positioning(self, result: Dict, config: GenerationConfig) -> Dict:
        """Apply structured positioning for graphics based on strategy"""
        # For graphics, we generally trust the AI's layout if it followed instructions
        # But we ensure everything is within bounds
        return self._ensure_bounds(result, config)
    
    def _apply_ui_positioning(self, result: Dict, config: GenerationConfig) -> Dict:
        """Apply UI-specific positioning checks"""
        # We trust the AI's explicit coordinates from the "Atomic Design" prompt.
        # This function previously forced a vertical stack, which breaks complex composed layouts.
        # Now we only ensure bounds and basic validation.
        return self._ensure_bounds(result, config)
    
    def _position_in_grid(self, result: Dict, config: GenerationConfig) -> Dict:
        """Position elements in a grid"""
        # Implementation kept for legacy compatibility but may be unused if prompts specify coordinates
        return self._ensure_bounds(result, config)
    
    def _position_centered(self, result: Dict, config: GenerationConfig) -> Dict:
        """Center all elements"""
        return self._apply_logo_positioning(result, config)
    
    def _position_layered(self, result: Dict, config: GenerationConfig) -> Dict:
        """Position elements in layers with depth"""
        return self._ensure_bounds(result, config)
    
    def _ensure_bounds(self, result: Dict, config: GenerationConfig) -> Dict:
        """Ensure all elements are within canvas bounds"""
        components = result.get('components', [])
        
        for component in components:
            pos = component.get('position', {})
            size = component.get('size', {})
            
            # Simple bounds check - prevent negative coordinates
            # We allow off-screen to right/bottom if intended (scrolling), but keeping top-left visible is good practice
            pos['x'] = max(0, pos.get('x', 0))
            pos['y'] = max(0, pos.get('y', 0))
        
        return result
    
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
