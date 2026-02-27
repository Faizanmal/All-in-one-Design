"""
Advanced AI Service
Enhanced AI capabilities including image-to-design, style transfer, voice-to-design, and trend analysis
"""
import os
import json
import base64
import logging
from typing import Dict, List
from groq import Groq
from .models import AIGenerationRequest

logger = logging.getLogger('ai_services')


class AdvancedAIService:
    """Advanced AI service for enhanced design capabilities"""
    
    def __init__(self):
        groq_api_key = os.getenv('GROQ_API_KEY')
        if not groq_api_key:
            raise RuntimeError("GROQ_API_KEY is not set")
        self.client = Groq(api_key=groq_api_key)
        self.default_model = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
        self.vision_model = os.getenv('GROQ_VISION_MODEL', 'llama-3.2-90b-vision-preview')
    
    def image_to_design(self, image_base64: str, prompt: str = "", 
                        design_type: str = 'ui_ux',
                        options: Dict = None, user=None) -> Dict:
        """
        Convert an image to a design structure
        
        Args:
            image_base64: Base64 encoded image
            prompt: Additional instructions
            design_type: Target design type
            options: Extraction options
            user: User making the request
            
        Returns:
            Dict with design structure
        """
        options = options or {}
        
        # Create tracking record
        ai_request = AIGenerationRequest.objects.create(
            user=user,
            request_type='layout',
            prompt=f"Image to design conversion: {prompt}",
            parameters={
                'design_type': design_type,
                'options': options
            },
            status='processing',
            model_used=self.vision_model
        )
        
        try:
            system_prompt = self._get_image_analysis_prompt(design_type, options)
            
            response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt or "Analyze this image and extract the design structure."
                            }
                        ]
                    }
                ],
                temperature=0.7,
            )
            
            content = response.choices[0].message.content
            
            # Parse JSON from response
            result = self._extract_json(content)
            
            ai_request.status = 'completed'
            ai_request.result = result
            ai_request.save()
            
            return result
            
        except Exception as e:
            ai_request.status = 'failed'
            ai_request.error_message = str(e)
            ai_request.save()
            raise
    
    def apply_style_transfer(self, design_data: Dict, style_preset: str,
                             style_description: str = "",
                             options: Dict = None, user=None) -> Dict:
        """
        Apply style transfer to a design
        
        Args:
            design_data: Current design structure
            style_preset: Style to apply
            style_description: Custom style description
            options: Transfer options
            user: User making the request
            
        Returns:
            Dict with transformed design
        """
        options = options or {}
        
        ai_request = AIGenerationRequest.objects.create(
            user=user,
            request_type='refinement',
            prompt=f"Style transfer: {style_preset}",
            parameters={
                'style_preset': style_preset,
                'style_description': style_description,
                'options': options
            },
            status='processing',
            model_used=self.default_model
        )
        
        try:
            system_prompt = self._get_style_transfer_prompt(style_preset, options)
            
            user_prompt = f"""Transform this design using the "{style_preset}" style.
            
{f'Style description: {style_description}' if style_description else ''}

Current design:
{json.dumps(design_data, indent=2)}

Apply the style transformation while preserving the overall layout and structure.
Return ONLY valid JSON with the transformed design."""
            
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
            )
            
            content = response.choices[0].message.content
            result = self._extract_json(content)
            
            ai_request.status = 'completed'
            ai_request.result = result
            ai_request.save()
            
            return result
            
        except Exception as e:
            ai_request.status = 'failed'
            ai_request.error_message = str(e)
            ai_request.save()
            raise
    
    def transcribe_audio_to_design(self, audio_base64: str, 
                                   design_type: str = 'ui_ux',
                                   additional_context: str = "",
                                   user=None) -> Dict:
        """
        Convert voice description to design
        
        Note: This is a simplified implementation. In production,
        you would use a dedicated speech-to-text service like Whisper.
        
        Args:
            audio_base64: Base64 encoded audio
            design_type: Target design type
            additional_context: Extra context
            user: User making the request
            
        Returns:
            Dict with transcription and generated design
        """
        # For now, we'll simulate transcription
        # In production, integrate with Whisper API or similar
        
        ai_request = AIGenerationRequest.objects.create(
            user=user,
            request_type='layout',
            prompt=f"Voice to design: {additional_context}",
            parameters={
                'design_type': design_type,
                'input_type': 'voice'
            },
            status='processing',
            model_used=self.default_model
        )
        
        try:
            # Transcribe audio using Groq Whisper API
            transcribed_text = self._transcribe_audio(audio_base64)

            if not transcribed_text:
                ai_request.status = 'failed'
                ai_request.error_message = 'Transcription returned empty text'
                ai_request.save()
                return {
                    'status': 'transcription_failed',
                    'message': 'Could not transcribe audio. Please try again with clearer audio.',
                    'ai_request_id': ai_request.id,
                }

            ai_request.prompt = f"Voice to design: {transcribed_text}"
            ai_request.save()

            # Generate design from the transcription
            design_result = self.generate_from_transcription(
                transcribed_text, design_type, user
            )

            return {
                'status': 'completed',
                'transcription': transcribed_text,
                'design': design_result,
                'ai_request_id': ai_request.id,
            }
            
        except Exception as e:
            ai_request.status = 'failed'
            ai_request.error_message = str(e)
            ai_request.save()
            raise
    
    def generate_from_transcription(self, transcribed_text: str,
                                    design_type: str = 'ui_ux',
                                    user=None) -> Dict:
        """
        Generate design from transcribed voice text
        
        Args:
            transcribed_text: Transcribed voice text
            design_type: Target design type
            user: User making the request
            
        Returns:
            Dict with generated design
        """
        from .services import AIDesignService
        
        # Use the main design service
        design_service = AIDesignService()
        return design_service.generate_layout_from_prompt(
            prompt=transcribed_text,
            design_type=design_type,
            user=user
        )

    def _transcribe_audio(self, audio_base64: str) -> str:
        """
        Transcribe audio using Groq's Whisper API.

        Args:
            audio_base64: Base64 encoded audio data

        Returns:
            Transcribed text string
        """
        import tempfile
        import os

        audio_bytes = base64.b64decode(audio_base64)

        # Write to a temp file since Groq expects a file path
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            with open(tmp_path, 'rb') as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    model='whisper-large-v3',
                    file=audio_file,
                    response_format='text',
                )
            return transcription.strip() if isinstance(transcription, str) else str(transcription).strip()
        except Exception:
            logger.exception('Groq Whisper transcription failed')
            raise
        finally:
            os.unlink(tmp_path)
    
    def analyze_design_trends(self, design_data: Dict, 
                              industry: str = 'general',
                              user=None) -> Dict:
        """
        Analyze a design against current trends
        
        Args:
            design_data: Design to analyze
            industry: Target industry
            user: User making the request
            
        Returns:
            Dict with trend analysis
        """
        ai_request = AIGenerationRequest.objects.create(
            user=user,
            request_type='refinement',
            prompt=f"Trend analysis for {industry}",
            parameters={'industry': industry},
            status='processing',
            model_used=self.default_model
        )
        
        try:
            system_prompt = """You are an expert design trend analyst. Analyze the given design and:
1. Evaluate its alignment with current design trends
2. Score different aspects (colors, typography, layout, style)
3. Provide specific recommendations for modernization
4. Identify which trends it follows and which it could adopt

Return your analysis as valid JSON with this structure:
{
    "overall_score": 75,
    "scores": {
        "colors": 80,
        "typography": 70,
        "layout": 75,
        "style": 72
    },
    "current_trends_followed": [
        {"trend": "Glassmorphism", "match_percentage": 60}
    ],
    "recommended_trends": [
        {"trend": "Neumorphism", "reason": "Would enhance the modern feel"}
    ],
    "recommendations": [
        {
            "area": "colors",
            "current": "Using muted colors",
            "suggestion": "Consider adding vibrant accent colors",
            "trend_reference": "Bold color accents are trending in 2024"
        }
    ],
    "summary": "Overall analysis summary..."
}"""
            
            user_prompt = f"""Analyze this {industry} design for trend alignment:

{json.dumps(design_data, indent=2)}

Consider current 2024/2025 design trends and provide actionable recommendations."""
            
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
            )
            
            content = response.choices[0].message.content
            result = self._extract_json(content)
            
            ai_request.status = 'completed'
            ai_request.result = result
            ai_request.save()
            
            return result
            
        except Exception as e:
            ai_request.status = 'failed'
            ai_request.error_message = str(e)
            ai_request.save()
            raise
    
    def get_design_suggestions(self, design_data: Dict,
                               focus_areas: List[str] = None,
                               user=None) -> List[Dict]:
        """
        Get AI-powered improvement suggestions for a design
        
        Args:
            design_data: Design to analyze
            focus_areas: Areas to focus on (colors, typography, layout, etc.)
            user: User making the request
            
        Returns:
            List of suggestions
        """
        focus_areas = focus_areas or ['colors', 'typography', 'layout', 'accessibility']
        
        ai_request = AIGenerationRequest.objects.create(
            user=user,
            request_type='refinement',
            prompt="Design improvement suggestions",
            parameters={'focus_areas': focus_areas},
            status='processing',
            model_used=self.default_model
        )
        
        try:
            system_prompt = f"""You are an expert UI/UX designer. Analyze the design and provide specific, actionable improvement suggestions.

Focus areas: {', '.join(focus_areas)}

For each suggestion, provide:
1. A clear title
2. The issue identified
3. The recommended improvement
4. Priority level (low/medium/high/critical)
5. The specific elements affected

Return as JSON array:
[
    {{
        "type": "color",
        "priority": "high",
        "title": "Low contrast text",
        "description": "The body text has insufficient contrast ratio",
        "current_value": "#666666 on #FFFFFF",
        "suggested_value": "#333333 on #FFFFFF",
        "affected_elements": ["text-body-1", "text-body-2"],
        "impact": "Improves readability and accessibility"
    }}
]"""
            
            user_prompt = f"""Analyze this design and provide improvement suggestions:

{json.dumps(design_data, indent=2)}"""
            
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
            )
            
            content = response.choices[0].message.content
            result = self._extract_json(content)
            
            # Ensure result is a list
            if isinstance(result, dict) and 'suggestions' in result:
                result = result['suggestions']
            elif not isinstance(result, list):
                result = [result]
            
            ai_request.status = 'completed'
            ai_request.result = {'suggestions': result}
            ai_request.save()
            
            return result
            
        except Exception as e:
            ai_request.status = 'failed'
            ai_request.error_message = str(e)
            ai_request.save()
            raise
    
    def _get_image_analysis_prompt(self, design_type: str, options: Dict) -> str:
        """Get system prompt for image analysis"""
        return f"""You are an expert design analyzer. Analyze the provided image and extract a complete design structure.

Design type: {design_type}

Extract the following (based on options):
- Layout structure and hierarchy
- Color palette (hex codes)
- Typography (fonts, sizes, weights)
- UI components and their properties
- Spacing and alignment patterns
- Visual effects (shadows, gradients, etc.)

Return a valid JSON structure compatible with a design editor:
{{
    "layout": {{
        "width": 1920,
        "height": 1080,
        "backgroundColor": "#FFFFFF"
    }},
    "colorPalette": ["#000000", "#FFFFFF", ...],
    "typography": {{
        "primaryFont": "Inter",
        "secondaryFont": "Poppins",
        "baseFontSize": 16
    }},
    "elements": [
        {{
            "id": "elem-1",
            "type": "rectangle",
            "position": {{"x": 0, "y": 0}},
            "size": {{"width": 100, "height": 100}},
            "fills": [{{"type": "solid", "color": "#000000"}}],
            ...
        }}
    ]
}}"""
    
    def _get_style_transfer_prompt(self, style_preset: str, options: Dict) -> str:
        """Get system prompt for style transfer"""
        style_descriptions = {
            'apple': 'Clean, minimalist, with subtle gradients and refined typography. Use SF Pro font style, generous whitespace, and iOS-inspired rounded corners.',
            'google_material': 'Material Design 3 style with bold colors, elevation shadows, and rounded shapes. Use Roboto font style and Material icons.',
            'microsoft_fluent': 'Fluent Design with acrylic blur effects, subtle animations, and Segoe UI font style. Light, airy feel with depth.',
            'minimalist': 'Ultra-minimal with maximum whitespace, limited colors (mostly black/white/gray), thin fonts, and subtle UI elements.',
            'brutalist': 'Bold, raw design with high contrast, stark colors, unconventional layouts, and dramatic typography.',
            'scandinavian': 'Warm, cozy aesthetic with muted colors, organic shapes, plenty of whitespace, and clean typography.',
            'retro': 'Vintage-inspired with warm colors, gradients, rounded shapes, and nostalgic typography (80s/90s style).',
            'futuristic': 'Cyberpunk-inspired with dark themes, neon accents, geometric shapes, and tech-forward typography.',
            'organic': 'Natural, flowing design with earth tones, curved shapes, handwritten fonts, and organic textures.',
            'corporate': 'Professional, trustworthy design with blue-heavy palette, clean typography, and structured layouts.',
            'playful': 'Fun, vibrant design with bold colors, rounded shapes, playful fonts, and animated elements.',
            'elegant': 'Sophisticated design with muted luxurious colors, serif typography, and refined details.',
        }
        
        style_desc = style_descriptions.get(style_preset, 'Modern, clean design style.')
        
        return f"""You are an expert design transformer. Transform the given design to match the "{style_preset}" style.

Style characteristics:
{style_desc}

Transformation rules:
1. Maintain the overall layout structure
2. Transform colors to match the style palette
3. Update typography to match the style
4. Adjust spacing and sizing as appropriate
5. Add or modify effects to match the style

Return ONLY valid JSON with the transformed design structure."""
    
    def _extract_json(self, content: str) -> Dict:
        """Extract JSON from response content"""
        # Try direct parsing first
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        # Find JSON in response
        if '{' in content:
            start = content.index('{')
            end = content.rindex('}') + 1
            try:
                return json.loads(content[start:end])
            except json.JSONDecodeError:
                pass
        
        if '[' in content:
            start = content.index('[')
            end = content.rindex(']') + 1
            try:
                return json.loads(content[start:end])
            except json.JSONDecodeError:
                pass
        
        raise ValueError("Could not extract valid JSON from response")


# Singleton instance
_advanced_ai_service = None

def get_advanced_ai_service() -> AdvancedAIService:
    """Get or create the advanced AI service instance"""
    global _advanced_ai_service
    if _advanced_ai_service is None:
        _advanced_ai_service = AdvancedAIService()
    return _advanced_ai_service
