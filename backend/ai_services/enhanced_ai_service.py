"""
Enhanced AI design services with variants and smart suggestions
"""
import os
import json
from typing import Dict, List, Any, Optional
from openai import OpenAI
import groq


class EnhancedAIDesignService:
    """
    Enhanced AI design service with multiple variant generation
    and smart design suggestions
    """
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.groq_client = groq.Groq(api_key=os.getenv('GROQ_API_KEY')) if os.getenv('GROQ_API_KEY') else None
    
    def generate_design_variants(
        self,
        prompt: str,
        design_type: str = 'graphic',
        num_variants: int = 3,
        style_preferences: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate multiple design variants from a text prompt
        
        Args:
            prompt: Text description of desired design
            design_type: Type of design (graphic, ui_ux, logo)
            num_variants: Number of variants to generate
            style_preferences: Optional style constraints
            
        Returns:
            Dictionary with multiple design variants and metadata
        """
        style_str = ""
        if style_preferences:
            style_str = f"\nStyle preferences: {json.dumps(style_preferences)}"
        
        system_prompt = """You are an expert AI design generator. Create detailed design specifications 
that can be rendered on a canvas. Focus on practical, implementable designs with specific 
element positioning, styling, and layout."""
        
        user_prompt = f"""Generate {num_variants} different design variants for a {design_type} project.

Design Request: {prompt}{style_str}

For each variant, provide:
1. A unique design concept and approach
2. Detailed layout specification
3. Color palette (5-7 colors with hex codes)
4. Typography choices (heading, body, accent fonts)
5. Element specifications (text, shapes, images)
6. Positioning and sizing for each element

Return as JSON:
{{
    "variants": [
        {{
            "variant_id": 1,
            "concept": "Brief concept description",
            "style": "Design style (minimalist, modern, bold, etc.)",
            "layout": {{
                "canvas": {{"width": 1920, "height": 1080}},
                "grid": {{"columns": 12, "rows": 8}},
                "sections": ["header", "main", "footer"]
            }},
            "color_palette": [
                {{"hex": "#000000", "name": "Primary", "role": "text"}},
                {{"hex": "#FFFFFF", "name": "Background", "role": "background"}}
            ],
            "typography": {{
                "heading": {{"font": "Poppins", "size": 48, "weight": "bold"}},
                "body": {{"font": "Inter", "size": 16, "weight": "regular"}},
                "accent": {{"font": "Roboto", "size": 14, "weight": "medium"}}
            }},
            "elements": [
                {{
                    "type": "text|image|shape|button",
                    "content": "Element content",
                    "position": {{"x": 100, "y": 100}},
                    "size": {{"width": 400, "height": 60}},
                    "style": {{
                        "color": "#000000",
                        "fontSize": 24,
                        "fontFamily": "Poppins",
                        "backgroundColor": "#FFFFFF"
                    }}
                }}
            ],
            "rationale": "Why this design works for the request"
        }}
    ],
    "comparison": "Brief comparison of the variants",
    "recommendation": "Which variant is recommended and why"
}}"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.9,
                max_tokens=3000
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                'success': True,
                'variants': result.get('variants', []),
                'comparison': result.get('comparison', ''),
                'recommendation': result.get('recommendation', ''),
                'tokens_used': response.usage.total_tokens,
                'model': 'gpt-4'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_auto_layout(
        self,
        design_data: Dict,
        target_sizes: List[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """
        Generate responsive variants for different screen sizes
        
        Args:
            design_data: Original design data
            target_sizes: List of target dimensions [{'width': 1920, 'height': 1080}, ...]
            
        Returns:
            Dictionary with responsive layout variants
        """
        if target_sizes is None:
            target_sizes = [
                {'width': 1920, 'height': 1080, 'name': 'desktop'},
                {'width': 768, 'height': 1024, 'name': 'tablet'},
                {'width': 375, 'height': 667, 'name': 'mobile'}
            ]
        
        prompt = f"""Adapt this design for multiple screen sizes while maintaining visual hierarchy and usability.

Original Design:
{json.dumps(design_data, indent=2)[:2000]}

Target Sizes:
{json.dumps(target_sizes, indent=2)}

For each target size, provide:
1. Adapted element positions and sizes
2. Adjusted typography (smaller fonts for mobile)
3. Layout changes (stack vs. side-by-side)
4. Hidden/visible elements based on space
5. Touch-friendly spacing for mobile

Return as JSON:
{{
    "responsive_variants": [
        {{
            "target": {{"width": 1920, "height": 1080, "name": "desktop"}},
            "layout_changes": "Description of layout changes",
            "elements": [
                {{
                    "element_id": "original_element_id",
                    "position": {{"x": 100, "y": 100}},
                    "size": {{"width": 400, "height": 60}},
                    "style": {{"fontSize": 24}},
                    "visible": true
                }}
            ],
            "breakpoint_rules": ["Rule 1", "Rule 2"]
        }}
    ]
}}"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a responsive design expert specializing in adaptive layouts."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                'success': True,
                'responsive_variants': result.get('responsive_variants', []),
                'tokens_used': response.usage.total_tokens
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def suggest_improvements(
        self,
        design_data: Dict,
        focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Suggest specific improvements for a design
        
        Args:
            design_data: Current design data
            focus_areas: Specific areas to focus on (color, typography, layout, spacing)
            
        Returns:
            Dictionary with actionable improvement suggestions
        """
        focus_str = ", ".join(focus_areas) if focus_areas else "all aspects"
        
        prompt = f"""Analyze this design and provide specific, actionable improvement suggestions.

Design Data:
{json.dumps(design_data, indent=2)[:2000]}

Focus Areas: {focus_str}

Provide detailed suggestions for:
1. Color harmony and contrast
2. Typography hierarchy and readability
3. Layout balance and white space
4. Visual flow and focal points
5. Accessibility improvements
6. Modern design trends application

Return as JSON:
{{
    "overall_assessment": {{
        "score": <1-10>,
        "strengths": ["Strength 1", "Strength 2"],
        "weaknesses": ["Weakness 1", "Weakness 2"]
    }},
    "improvements": [
        {{
            "category": "color|typography|layout|spacing|accessibility",
            "priority": "high|medium|low",
            "issue": "Description of current issue",
            "suggestion": "Specific improvement to make",
            "implementation": {{
                "element_id": "specific_element",
                "property": "property_to_change",
                "current_value": "current value",
                "suggested_value": "new value"
            }},
            "rationale": "Why this improves the design"
        }}
    ],
    "quick_wins": [
        {{"action": "Quick improvement 1", "impact": "high|medium|low"}},
        {{"action": "Quick improvement 2", "impact": "high|medium|low"}}
    ],
    "advanced_tips": ["Tip 1", "Tip 2"]
}}"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a senior design critic with expertise in visual design, UX, and accessibility."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                'success': True,
                'assessment': result.get('overall_assessment', {}),
                'improvements': result.get('improvements', []),
                'quick_wins': result.get('quick_wins', []),
                'advanced_tips': result.get('advanced_tips', []),
                'tokens_used': response.usage.total_tokens
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def check_accessibility(self, design_data: Dict) -> Dict[str, Any]:
        """
        Check design for accessibility issues
        
        Args:
            design_data: Design data to check
            
        Returns:
            Dictionary with accessibility report
        """
        prompt = f"""Analyze this design for accessibility compliance (WCAG 2.1 Level AA).

Design Data:
{json.dumps(design_data, indent=2)[:1500]}

Check for:
1. Color contrast ratios (minimum 4.5:1 for normal text, 3:1 for large text)
2. Text size and readability
3. Touch target sizes (minimum 44x44px)
4. Keyboard navigation support
5. Screen reader compatibility
6. Color as sole information carrier

Return as JSON:
{{
    "wcag_level": "A|AA|AAA",
    "overall_score": <0-100>,
    "issues": [
        {{
            "severity": "critical|warning|info",
            "category": "contrast|text_size|touch_targets|keyboard|screen_reader|color_usage",
            "description": "Description of issue",
            "affected_elements": ["element_id_1", "element_id_2"],
            "recommendation": "How to fix",
            "wcag_criterion": "WCAG criterion number"
        }}
    ],
    "passed_checks": ["Check 1", "Check 2"],
    "summary": "Brief accessibility summary"
}}"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a WCAG accessibility expert specializing in inclusive design."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1500
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                'success': True,
                'wcag_level': result.get('wcag_level', 'A'),
                'score': result.get('overall_score', 0),
                'issues': result.get('issues', []),
                'passed_checks': result.get('passed_checks', []),
                'summary': result.get('summary', ''),
                'tokens_used': response.usage.total_tokens
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_brand_assets(
        self,
        brand_description: str,
        asset_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate brand assets (logo variations, color palette, typography)
        
        Args:
            brand_description: Description of the brand
            asset_types: Types of assets to generate
            
        Returns:
            Dictionary with brand asset specifications
        """
        if asset_types is None:
            asset_types = ['logo', 'color_palette', 'typography', 'patterns']
        
        prompt = f"""Create a comprehensive brand identity system based on this description:

Brand Description: {brand_description}

Generate specifications for:
{', '.join(asset_types)}

Return as JSON with detailed specifications for each asset type:
{{
    "brand_essence": {{
        "keywords": ["keyword1", "keyword2"],
        "personality": "Brand personality description",
        "target_audience": "Target audience description"
    }},
    "logo": {{
        "primary": {{
            "concept": "Logo concept",
            "type": "wordmark|lettermark|icon|combination",
            "elements": [<shape/text elements with positions>],
            "colors": ["#HEX1", "#HEX2"]
        }},
        "variations": [
            {{"name": "horizontal", "usage": "When to use"}},
            {{"name": "vertical", "usage": "When to use"}},
            {{"name": "icon_only", "usage": "When to use"}}
        ]
    }},
    "color_palette": {{
        "primary": [{{"hex": "#000000", "name": "Primary", "usage": "Main brand color"}}],
        "secondary": [{{"hex": "#FFFFFF", "name": "Secondary"}}],
        "accent": [{{"hex": "#FF0000", "name": "Accent"}}],
        "neutrals": [{{"hex": "#GRAY", "name": "Neutral"}}]
    }},
    "typography": {{
        "primary_font": {{"name": "Font Name", "weights": [400, 700], "usage": "Headings"}},
        "secondary_font": {{"name": "Font Name", "weights": [400, 600], "usage": "Body text"}},
        "scale": {{"h1": 48, "h2": 36, "h3": 24, "body": 16}}
    }},
    "patterns": [
        {{"name": "Pattern name", "description": "Pattern description", "usage": "When to use"}}
    ]
}}"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a brand identity expert specializing in creating cohesive visual systems."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=2500
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                'success': True,
                'brand_assets': result,
                'tokens_used': response.usage.total_tokens
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
