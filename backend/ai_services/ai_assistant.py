"""
AI Design Assistant Service
Provides advanced AI-powered design features including:
- Design critique and feedback
- Color harmony generation
- Typography pairing suggestions
- Layout optimization
- Design trend analysis
"""
import os
import json
from typing import Dict, List, Any, Optional
from openai import OpenAI


class AIDesignAssistant:
    """AI-powered design assistant with advanced features"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    def critique_design(self, design_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a design and provide constructive critique
        
        Args:
            design_data: Dictionary containing design elements, colors, typography
            
        Returns:
            Dictionary with critique, suggestions, and improvement scores
        """
        prompt = f"""You are an expert design critic. Analyze this design and provide detailed feedback:

Design Details:
- Project Type: {design_data.get('project_type', 'Unknown')}
- Colors Used: {design_data.get('colors', [])}
- Fonts Used: {design_data.get('fonts', [])}
- Element Count: {design_data.get('element_count', 0)}
- Layout Type: {design_data.get('layout_type', 'Unknown')}

Provide critique in the following areas (rate each 1-10):
1. Color Harmony - Are colors working well together?
2. Typography - Font choices and readability
3. Layout & Spacing - Balance and white space usage
4. Visual Hierarchy - Clear flow and emphasis
5. Overall Impact - Professional appearance

Return your analysis as JSON with this structure:
{{
    "overall_score": <1-10>,
    "scores": {{
        "color_harmony": <1-10>,
        "typography": <1-10>,
        "layout_spacing": <1-10>,
        "visual_hierarchy": <1-10>,
        "overall_impact": <1-10>
    }},
    "strengths": [<list of 2-3 strengths>],
    "improvements": [<list of 3-5 specific improvement suggestions>],
    "summary": "<2-3 sentence overall assessment>"
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional design critic with expertise in visual design, UX/UI, and branding."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            critique = json.loads(response.choices[0].message.content)
            return {
                'success': True,
                'critique': critique,
                'tokens_used': response.usage.total_tokens
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_color_palette(
        self,
        base_color: Optional[str] = None,
        mood: Optional[str] = None,
        industry: Optional[str] = None,
        count: int = 5
    ) -> Dict[str, Any]:
        """
        Generate harmonious color palettes based on criteria
        
        Args:
            base_color: Hex color to build palette around
            mood: Desired mood (e.g., 'professional', 'playful', 'elegant')
            industry: Target industry (e.g., 'tech', 'healthcare', 'fashion')
            count: Number of colors in palette
            
        Returns:
            Dictionary with color palette and usage recommendations
        """
        prompt = f"""Generate a professional color palette with {count} colors.

Requirements:
- Base Color: {base_color or 'None (you choose)'}
- Mood: {mood or 'Professional and modern'}
- Industry: {industry or 'General purpose'}

Create a harmonious palette that:
1. Has good contrast for accessibility
2. Works well together visually
3. Suits the specified mood and industry
4. Includes primary, secondary, and accent colors

Return as JSON:
{{
    "palette": [
        {{
            "hex": "#RRGGBB",
            "name": "Color name",
            "role": "primary|secondary|accent|background|text",
            "usage": "Brief description of when to use this color"
        }}
    ],
    "description": "Brief description of the palette",
    "color_scheme": "monochromatic|analogous|complementary|triadic|tetradic",
    "accessibility": {{
        "wcag_compliant": true|false,
        "notes": "Accessibility considerations"
    }}
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a color theory expert specializing in creating harmonious, accessible color palettes for digital design."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=800
            )
            
            palette = json.loads(response.choices[0].message.content)
            return {
                'success': True,
                'palette': palette,
                'tokens_used': response.usage.total_tokens
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def suggest_typography(
        self,
        design_type: str,
        mood: str = 'professional',
        brand_attributes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Suggest font pairings for a design
        
        Args:
            design_type: Type of design (e.g., 'website', 'poster', 'logo')
            mood: Desired mood
            brand_attributes: List of brand characteristics
            
        Returns:
            Dictionary with font suggestions and pairing rationale
        """
        brand_str = ", ".join(brand_attributes) if brand_attributes else "professional, modern"
        
        prompt = f"""Suggest professional font pairings for a {design_type} design.

Requirements:
- Design Type: {design_type}
- Mood: {mood}
- Brand Attributes: {brand_str}

Provide 3 font pairing options with:
1. Heading font
2. Body text font
3. Accent/special font (optional)
4. Rationale for the pairing
5. Usage guidelines

Return as JSON:
{{
    "pairings": [
        {{
            "heading_font": {{
                "name": "Font name",
                "fallback": "Font fallback stack",
                "weight": "Recommended weights",
                "characteristics": "Brief description"
            }},
            "body_font": {{
                "name": "Font name",
                "fallback": "Font fallback stack",
                "weight": "Recommended weights",
                "characteristics": "Brief description"
            }},
            "accent_font": {{
                "name": "Font name (or null)",
                "usage": "When to use"
            }},
            "rationale": "Why this pairing works",
            "example_usage": {{
                "heading_size": "Size recommendation",
                "body_size": "Size recommendation",
                "line_height": "Line height recommendations"
            }}
        }}
    ],
    "general_tips": [<List of typography tips for this design type>]
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a typography expert with deep knowledge of font pairing, readability, and visual hierarchy."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1200
            )
            
            typography = json.loads(response.choices[0].message.content)
            return {
                'success': True,
                'typography': typography,
                'tokens_used': response.usage.total_tokens
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def optimize_layout(self, design_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Suggest layout improvements and optimizations
        
        Args:
            design_data: Current design layout information
            
        Returns:
            Dictionary with layout optimization suggestions
        """
        prompt = f"""Analyze this layout and suggest improvements:

Current Layout:
- Elements: {design_data.get('element_count', 0)} elements
- Layout Type: {design_data.get('layout_type', 'Unknown')}
- Canvas Size: {design_data.get('width')}x{design_data.get('height')}
- Element Distribution: {design_data.get('element_distribution', 'Unknown')}

Provide specific suggestions for:
1. Spacing and padding improvements
2. Visual hierarchy adjustments
3. Alignment corrections
4. Grid system recommendations
5. Responsive considerations

Return as JSON:
{{
    "improvements": [
        {{
            "category": "spacing|alignment|hierarchy|grid|responsive",
            "issue": "What needs improvement",
            "suggestion": "Specific recommendation",
            "priority": "high|medium|low"
        }}
    ],
    "grid_recommendation": {{
        "columns": <number>,
        "gutter": "<size>",
        "margin": "<size>",
        "rationale": "Why this grid works"
    }},
    "spacing_scale": [<Suggested spacing values>],
    "best_practices": [<List of applicable best practices>]
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a layout and UX expert specializing in visual hierarchy, spacing, and responsive design."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            optimization = json.loads(response.choices[0].message.content)
            return {
                'success': True,
                'optimization': optimization,
                'tokens_used': response.usage.total_tokens
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_design_trends(
        self,
        industry: str,
        design_type: str
    ) -> Dict[str, Any]:
        """
        Provide insights on current design trends
        
        Args:
            industry: Target industry
            design_type: Type of design
            
        Returns:
            Dictionary with current trends and recommendations
        """
        prompt = f"""Provide insights on current design trends for {design_type} in the {industry} industry.

Include:
1. Top 5 current trends with descriptions
2. Color trends
3. Typography trends
4. Layout and composition trends
5. What to avoid (dated practices)
6. Predictions for upcoming trends

Return as JSON:
{{
    "current_trends": [
        {{
            "name": "Trend name",
            "description": "What it is",
            "examples": "How it's being used",
            "popularity": "high|medium|emerging"
        }}
    ],
    "color_trends": {{
        "popular_palettes": [<List of trending color combinations>],
        "trending_colors": [<List of specific colors>]
    }},
    "typography_trends": [<List of font and type trends>],
    "layout_trends": [<List of layout approaches>],
    "avoid": [<List of dated or overused elements>],
    "predictions": [<List of emerging trends>]
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a design trend analyst with up-to-date knowledge of contemporary design practices across industries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=1500
            )
            
            trends = json.loads(response.choices[0].message.content)
            return {
                'success': True,
                'trends': trends,
                'tokens_used': response.usage.total_tokens
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def suggest_improvements(
        self,
        design_data: Dict[str, Any],
        focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive improvement suggestions
        
        Args:
            design_data: Complete design information
            focus_areas: Specific areas to focus on
            
        Returns:
            Dictionary with prioritized improvement suggestions
        """
        focus = ", ".join(focus_areas) if focus_areas else "all aspects"
        
        prompt = f"""Provide comprehensive improvement suggestions for this design.

Design Information:
{json.dumps(design_data, indent=2)}

Focus Areas: {focus}

Provide actionable suggestions that will have the most impact on:
1. Visual appeal
2. User experience
3. Brand consistency
4. Accessibility
5. Modern design standards

Return as JSON with prioritized suggestions:
{{
    "quick_wins": [<List of easy, high-impact changes>],
    "major_improvements": [<List of more involved improvements>],
    "long_term": [<List of strategic design considerations>],
    "priority_order": [<List ranking all suggestions by impact>]
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a comprehensive design consultant providing actionable, prioritized improvement recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1200
            )
            
            suggestions = json.loads(response.choices[0].message.content)
            return {
                'success': True,
                'suggestions': suggestions,
                'tokens_used': response.usage.total_tokens
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
