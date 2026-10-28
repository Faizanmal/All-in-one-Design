"""
AI Service Layer for LLM and Image Generation Integration
"""
import os
import json
import logging
from typing import Dict, List
from openai import OpenAI
from .models import AIGenerationRequest
from .resilient_gateway import get_resilient_gateway
from .enhanced_generation_engine import get_generation_engine, GenerationConfig, DesignCategory, PlacementStrategy

logger = logging.getLogger('ai_services')

class AIDesignService:
    """Main AI service for design generation"""
    
    def __init__(self):
        self.gateway = get_resilient_gateway()
        configured = self.gateway.configured_providers()
        self.default_model = (
            configured[0] if configured else os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
        )
        # Legacy Groq client kept for any callers that still expect it
        from groq import Groq
        groq_api_key = os.getenv('GROQ_API_KEY')
        self.client = Groq(api_key=groq_api_key) if groq_api_key else None
    
    def generate_layout_from_prompt(self, prompt: str, design_type: str = 'ui_ux', 
                                    style: str = 'modern', color_scheme: List[str] = None,
                                    user=None, canvas_width: int = None,
                                    canvas_height: int = None,
                                    placement_strategy: str = None) -> Dict:
        """
        Generate a complete layout from a text prompt.
        
        Args:
            prompt: User's design request
            design_type: 'graphic', 'ui_ux', 'logo', 'presentation', or 'social_media'
            style: Design style (modern, minimalist, etc.)
            color_scheme: Preferred color palette
            user: User making the request
            canvas_width: Target canvas width (defaults by design type)
            canvas_height: Target canvas height (defaults by design type)
            placement_strategy: Optional placement strategy name
            
        Returns:
            Dict with design JSON structure
        """
        # Create tracking record
        ai_request = AIGenerationRequest.objects.create(
            user=user,
            request_type='layout',
            prompt=prompt,
            parameters={'design_type': design_type},
            status='processing',
            model_used='enhanced_generation_engine_v1'
        )
        
        try:
            # Map design_type to category
            category_map = {
                'ui_ux': DesignCategory.UI_UX,
                'graphic': DesignCategory.GRAPHIC,
                'logo': DesignCategory.LOGO,
                'presentation': getattr(DesignCategory, 'PRESENTATION', DesignCategory.UI_UX),
                'social_media': getattr(DesignCategory, 'SOCIAL_MEDIA', DesignCategory.GRAPHIC),
            }
            category = category_map.get(design_type, DesignCategory.UI_UX)

            # Logos are square marks; other layouts stay widescreen by default
            if canvas_width is None or canvas_height is None:
                if category == DesignCategory.LOGO:
                    canvas_width = canvas_width or 1024
                    canvas_height = canvas_height or 1024
                else:
                    canvas_width = canvas_width or 1920
                    canvas_height = canvas_height or 1080

            strategy = PlacementStrategy.CENTERED if category == DesignCategory.LOGO else PlacementStrategy.GRID
            if placement_strategy:
                try:
                    strategy = PlacementStrategy(placement_strategy)
                except ValueError:
                    pass
            
            # Create configuration
            config = GenerationConfig(
                category=category,
                prompt=prompt,
                canvas_width=canvas_width,
                canvas_height=canvas_height,
                style=style,
                color_scheme=color_scheme,
                placement_strategy=strategy
            )
            
            # Generate using enhanced engine
            engine = get_generation_engine()
            result = engine.generate_design(config)
            
            logger.debug("Enhanced generation successful")
            
            # Update tracking
            ai_request.status = 'completed'
            ai_request.result = result
            # Approximation since engine handles client
            ai_request.tokens_used = 0 
            ai_request.save()
            
            return result
            
        except Exception as e:
            ai_request.status = 'failed'
            ai_request.error_message = str(e)
            ai_request.save()
            raise
    
    # Legacy method kept but not used for layout generation
    def _get_system_prompt(self, design_type: str) -> str:
        """Get appropriate system prompt based on design type"""
        return "" # Deprecated

    
    def generate_logo(self, company_name: str, industry: str = '', 
                     style: str = 'modern', colors: List[str] = None, 
                     user=None, canvas_width: int = 1024,
                     canvas_height: int = 1024) -> Dict:
        """
        Generate logo variations using AI.
        
        Args:
            company_name: Name of the company
            industry: Industry/business type
            style: Design style (modern, minimalist, vintage, etc.)
            colors: Preferred color scheme
            user: User making the request
            canvas_width: Target canvas width (default 1024 for square logos)
            canvas_height: Target canvas height (default 1024)
            
        Returns:
            Dict with logo variations and metadata
        """
        industry_str = f"in the {industry} industry" if industry else ""
        
        prompt = f"""Create a logo for company '{company_name}' {industry_str}. Company name for wordmark: {company_name}."""
        
        return self.generate_layout_from_prompt(
            prompt=prompt, 
            design_type='logo',
            style=style,
            color_scheme=colors,
            user=user,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            placement_strategy='centered',
        )
    
    def generate_color_palette(self, theme: str, user=None) -> List[str]:
        """
        Generate color palette based on theme.
        
        Args:
            theme: Theme description (e.g., "tropical beach", "corporate professional")
            user: User making the request
            
        Returns:
            List of hex color codes
        """
        ai_request = AIGenerationRequest.objects.create(
            user=user,
            request_type='color_palette',
            prompt=theme,
            status='processing',
            model_used=self.default_model
        )
        
        try:
            result = self.gateway.generate_json_response(
                system_prompt=(
                    'You are a color theory expert. '
                    'Generate harmonious color palettes as JSON arrays of hex codes. '
                    'Return exactly 5 colors that work well together. '
                    'Format: {"colors": ["#RRGGBB", "#RRGGBB", ...]}'
                ),
                user_prompt=f'Generate a color palette for: {theme}',
                temperature=0.7,
            )
            colors = result.get('colors', [])
            
            ai_request.status = 'completed'
            ai_request.result = {'colors': colors}
            ai_request.tokens_used = 0
            ai_request.save()
            
            return colors
            
        except Exception as e:
            ai_request.status = 'failed'
            ai_request.error_message = str(e)
            ai_request.save()
            raise
    
    def suggest_fonts(self, design_style: str, purpose: str = 'general') -> List[str]:
        """
        Suggest appropriate fonts based on design style and purpose.
        
        Args:
            design_style: Style description (modern, elegant, playful, etc.)
            purpose: Purpose (heading, body, logo, etc.)
            
        Returns:
            List of font family names
        """
        result = self.gateway.generate_json_response(
            system_prompt=(
                'You are a typography expert. '
                'Suggest appropriate font families for the given style and purpose. '
                'Return JSON with an array of font names. '
                'Format: {"fonts": ["Font Name 1", "Font Name 2", ...]}'
            ),
            user_prompt=f'Suggest fonts for {design_style} style, purpose: {purpose}',
            temperature=0.5,
        )
        return result.get('fonts', [])
    
    def refine_design(self, current_design: Dict, refinement_instruction: str, 
                     user=None) -> Dict:
        """
        Refine existing design based on user instructions.
        
        Args:
            current_design: Current design JSON
            refinement_instruction: What to change/improve
            user: User making the request
            
        Returns:
            Updated design JSON
        """
        ai_request = AIGenerationRequest.objects.create(
            user=user,
            request_type='refinement',
            prompt=refinement_instruction,
            parameters={'current_design': current_design},
            status='processing',
            model_used=self.default_model
        )
        
        try:
            result = self.gateway.generate_json_response(
                system_prompt=(
                    'You are an expert designer. '
                    'You will receive a current design and instructions to refine it. '
                    'Return the updated design as JSON, maintaining the same structure '
                    'but incorporating the requested changes.'
                ),
                user_prompt=(
                    f'Current design:\n{json.dumps(current_design, indent=2)}\n\n'
                    f'Refinement instruction: {refinement_instruction}\n\n'
                    'Please return the refined design as JSON.'
                ),
                temperature=0.6,
            )
            
            ai_request.status = 'completed'
            ai_request.result = result
            ai_request.tokens_used = 0
            ai_request.save()
            
            return result
            
        except Exception as e:
            ai_request.status = 'failed'
            ai_request.error_message = str(e)
            ai_request.save()
            raise


class AIImageService:
    """Service for AI image and icon generation"""
    
    def __init__(self):
        # Image generation requires OpenAI (Groq doesn't support images)
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            self.client = OpenAI(api_key=openai_key)
            self.image_generation_available = True
        else:
            self.client = None
            self.image_generation_available = False
    
    def generate_image(self, prompt: str, size: str = "1024x1024", 
                      style: str = "vivid", user=None) -> str:
        """
        Generate image using DALL-E.
        
        Args:
            prompt: Image description
            size: Image size (1024x1024, 1792x1024, 1024x1792)
            style: vivid or natural
            user: User making the request
            
        Returns:
            URL of generated image
        """
        if not self.image_generation_available:
            raise ValueError("Image generation is not available. Please set OPENAI_API_KEY in environment variables.")
        
        ai_request = AIGenerationRequest.objects.create(
            user=user,
            request_type='image',
            prompt=prompt,
            parameters={'size': size, 'style': style},
            status='processing',
            model_used='dall-e-3'
        )
        
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                style=style,
                n=1,
            )
            
            image_url = response.data[0].url
            
            ai_request.status = 'completed'
            ai_request.result = {'image_url': image_url}
            ai_request.save()
            
            return image_url
            
        except Exception as e:
            ai_request.status = 'failed'
            ai_request.error_message = str(e)
            ai_request.save()
            raise
    
    def generate_logo_image(self, company_name: str, style: str, 
                           colors: str, user=None) -> List[str]:
        """
        Generate logo images using DALL-E.
        
        Args:
            company_name: Company name
            style: Logo style description
            colors: Color description
            user: User making the request
            
        Returns:
            List of image URLs
        """
        prompt = f"""Professional logo design for '{company_name}'.
Style: {style}
Colors: {colors}
Clean, simple, vector-style logo on white background.
Suitable for business use."""
        
        return self.generate_image(prompt, size="1024x1024", style="vivid", user=user)
