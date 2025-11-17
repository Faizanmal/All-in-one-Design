"""
AI Service Layer for LLM and Image Generation Integration
"""
import os
import json
from typing import Dict, List
from openai import OpenAI
from groq import Groq
from .models import AIGenerationRequest


class AIDesignService:
    """Main AI service for design generation"""
    
    def __init__(self):
        # self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        groq_api_key = os.getenv('GROQ_API_KEY')
        print(f"Initializing AIDesignService with GROQ_API_KEY: {'Set' if groq_api_key else 'Not Set'}")
        if not groq_api_key:
            # Provide a clear runtime error instead of allowing the Groq client to raise a library-specific exception
            raise RuntimeError(
                "GROQ_API_KEY is not set in environment. Add GROQ_API_KEY to backend/.env or your system environment and restart the Django server."
            )
        self.client = Groq(api_key=groq_api_key)
        # Valid Groq models: llama-3.3-70b-versatile, llama-3.1-70b-versatile, mixtral-8x7b-32768
        self.default_model = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
        print(f"Using model: {self.default_model}")
        # self.default_model = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
    
    def generate_layout_from_prompt(self, prompt: str, design_type: str = 'ui_ux', 
                                    user=None) -> Dict:
        """
        Generate a complete layout from a text prompt.
        
        Args:
            prompt: User's design request
            design_type: 'graphic', 'ui_ux', or 'logo'
            user: User making the request
            
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
            model_used=self.default_model
        )
        
        try:
            # Build system prompt based on design type
            system_prompt = self._get_system_prompt(design_type)
            
            print(f"Calling Groq API with model: {self.default_model}")
            print(f"Prompt: {prompt[:100]}...")
            
            # Call Groq LLM (note: Groq doesn't support response_format parameter)
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": system_prompt + "\n\nIMPORTANT: You must respond with valid JSON only, no other text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )
            
            print("Groq API call successful")
            
            # Extract JSON from response (Groq may include extra text)
            content = response.choices[0].message.content
            print(f"Response content length: {len(content)}")
            print(f"Raw Groq response: {content[:500]}...")  # Print first 500 chars
            
            # Try to find JSON in the response
            if '{' in content:
                json_start = content.index('{')
                json_end = content.rindex('}') + 1
                json_str = content[json_start:json_end]
                result = json.loads(json_str)
            else:
                result = json.loads(content)
            
            print(f"Parsed JSON keys: {list(result.keys())}")
            print(f"Components count: {len(result.get('components', []))}")
            
            # Update tracking
            ai_request.status = 'completed'
            ai_request.result = result
            ai_request.tokens_used = response.usage.total_tokens if hasattr(response.usage, 'total_tokens') else 0
            ai_request.save()
            
            return result
            
        except Exception as e:
            ai_request.status = 'failed'
            ai_request.error_message = str(e)
            ai_request.save()
            raise
    
    def _get_system_prompt(self, design_type: str) -> str:
        """Get appropriate system prompt based on design type"""
        
        if design_type == 'ui_ux':
            return """You are an expert UI/UX designer. Generate a complete UI design as JSON.
            
Your response must be valid JSON with this structure:
{
  "components": [
    {
      "type": "header|button|text|image|input|map|card|navigation|footer",
      "text": "Optional text content",
      "position": {"x": 0, "y": 0},
      "size": {"width": "100%", "height": "60px"},
      "style": {
        "backgroundColor": "#FFFFFF",
        "color": "#000000",
        "fontSize": "16px",
        "fontFamily": "Inter",
        "padding": "20px",
        "borderRadius": "8px"
      },
      "children": [] // Nested components if needed
    }
  ],
  "colorPalette": ["#primary", "#secondary", "#accent"],
  "suggestedFonts": ["Inter", "Roboto"],
  "canvasWidth": 1920,
  "canvasHeight": 1080
}

Make designs modern, accessible, and follow UI/UX best practices."""

        elif design_type == 'graphic':
            return """You are an expert graphic designer. Generate a complete graphic design as JSON.

Your response must be valid JSON with this structure:
{
  "components": [
    {
      "type": "text|image|shape|icon",
      "text": "Optional text",
      "position": {"x": 100, "y": 100},
      "size": {"width": 400, "height": 200},
      "style": {
        "fontSize": "48px",
        "fontFamily": "Montserrat",
        "fontWeight": "bold",
        "color": "#000000",
        "textAlign": "center"
      },
      "rotation": 0,
      "opacity": 1,
      "zIndex": 0
    }
  ],
  "colorPalette": ["#primary", "#secondary", "#accent"],
  "suggestedFonts": ["Montserrat", "Playfair Display"],
  "canvasWidth": 1920,
  "canvasHeight": 1080,
  "background": "#FFFFFF"
}

Make designs visually appealing and suitable for social media, posters, or marketing."""

        else:  # logo
            return """You are an expert logo designer. Generate logo design concepts as JSON.

Your response must be valid JSON with this structure:
{
  "variations": [
    {
      "name": "Variation 1",
      "components": [
        {
          "type": "text|shape|icon",
          "text": "Company Name",
          "position": {"x": 100, "y": 100},
          "style": {
            "fontSize": "48px",
            "fontFamily": "Helvetica",
            "fontWeight": "bold",
            "color": "#000000"
          }
        }
      ],
      "colorPalette": ["#primary", "#secondary"]
    }
  ],
  "suggestedFonts": ["Helvetica", "Futura"],
  "styleNotes": "Modern and minimalist approach"
}

Create professional, memorable, and scalable logo designs."""
    
    def generate_logo(self, company_name: str, industry: str = '', 
                     style: str = 'modern', colors: List[str] = None, 
                     user=None) -> Dict:
        """
        Generate logo variations using AI.
        
        Args:
            company_name: Name of the company
            industry: Industry/business type
            style: Design style (modern, minimalist, vintage, etc.)
            colors: Preferred color scheme
            user: User making the request
            
        Returns:
            Dict with logo variations and metadata
        """
        colors_str = ', '.join(colors) if colors else 'professional color palette'
        industry_str = f"in the {industry} industry" if industry else ""
        
        prompt = f"""Generate 3 logo variations for company '{company_name}' {industry_str}.
Style: {style}
Colors: {colors_str}

Each variation should be unique and professional."""
        
        return self.generate_layout_from_prompt(prompt, 'logo', user)
    
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
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": """You are a color theory expert. 
                    Generate harmonious color palettes as JSON arrays of hex codes.
                    Return exactly 5 colors that work well together.
                    Format: {"colors": ["#RRGGBB", "#RRGGBB", ...]}
                    IMPORTANT: Respond with valid JSON only, no other text."""},
                    {"role": "user", "content": f"Generate a color palette for: {theme}"}
                ],
            )
            
            content = response.choices[0].message.content
            # Extract JSON from response
            if '{' in content:
                json_start = content.index('{')
                json_end = content.rindex('}') + 1
                json_str = content[json_start:json_end]
                result = json.loads(json_str)
            else:
                result = json.loads(content)
            
            colors = result.get('colors', [])
            
            ai_request.status = 'completed'
            ai_request.result = {'colors': colors}
            ai_request.tokens_used = response.usage.total_tokens if hasattr(response.usage, 'total_tokens') else 0
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
        response = self.client.chat.completions.create(
            model=self.default_model,
            messages=[
                {"role": "system", "content": """You are a typography expert.
                Suggest appropriate font families for the given style and purpose.
                Return JSON with array of font names.
                Format: {"fonts": ["Font Name 1", "Font Name 2", ...]}
                IMPORTANT: Respond with valid JSON only, no other text."""},
                {"role": "user", "content": f"Suggest fonts for {design_style} style, purpose: {purpose}"}
            ],
        )
        
        content = response.choices[0].message.content
        # Extract JSON from response
        if '{' in content:
            json_start = content.index('{')
            json_end = content.rindex('}') + 1
            json_str = content[json_start:json_end]
            result = json.loads(json_str)
        else:
            result = json.loads(content)
        
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
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": """You are an expert designer.
                    You will receive a current design and instructions to refine it.
                    Return the updated design as JSON, maintaining the same structure but incorporating the requested changes.
                    IMPORTANT: Respond with valid JSON only, no other text."""},
                    {"role": "user", "content": f"""Current design:
{json.dumps(current_design, indent=2)}

Refinement instruction: {refinement_instruction}

Please return the refined design as JSON."""}
                ],
            )
            
            content = response.choices[0].message.content
            # Extract JSON from response
            if '{' in content:
                json_start = content.index('{')
                json_end = content.rindex('}') + 1
                json_str = content[json_start:json_end]
                result = json.loads(json_str)
            else:
                result = json.loads(content)
            
            ai_request.status = 'completed'
            ai_request.result = result
            ai_request.tokens_used = response.usage.total_tokens if hasattr(response.usage, 'total_tokens') else 0
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
