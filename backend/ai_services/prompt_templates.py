"""
Industry-specific AI prompt templates and enhanced prompt engineering.
Provides structured, detailed prompts for different industries and use cases.
"""

# Industry-specific design system prompts
INDUSTRY_PROMPTS = {
    'technology': {
        'style_guide': 'Clean, minimalist design with subtle gradients. Use geometric shapes, thin fonts, and plenty of whitespace. Primary colors: blues, teals, purples.',
        'typography': 'Modern sans-serif fonts like Inter, SF Pro, or Roboto. Use font hierarchy with clear size differentiation.',
        'components': ['dashboard cards', 'stat widgets', 'navigation bars', 'data tables', 'progress indicators', 'notification badges'],
        'color_schema': ['#0F172A', '#3B82F6', '#06B6D4', '#10B981', '#F1F5F9'],
    },
    'healthcare': {
        'style_guide': 'Trustworthy, clean design with calming colors. Emphasize readability and accessibility. Use rounded shapes and warm tones.',
        'typography': 'Highly readable fonts like Open Sans, Nunito, or Source Sans Pro. Larger base font sizes for accessibility.',
        'components': ['appointment cards', 'patient profiles', 'medical forms', 'health metrics', 'care timeline'],
        'color_schema': ['#0D9488', '#0EA5E9', '#FFFFFF', '#F0FDF4', '#1E293B'],
    },
    'ecommerce': {
        'style_guide': 'Conversion-focused design with clear CTAs. Product imagery prominence, trust indicators, and easy navigation.',
        'typography': 'Bold headlines with Poppins or Montserrat. Body text with Inter or Lato for readability.',
        'components': ['product cards', 'shopping cart', 'price badges', 'review stars', 'category filters', 'hero banners'],
        'color_schema': ['#DC2626', '#F59E0B', '#FFFFFF', '#111827', '#F3F4F6'],
    },
    'finance': {
        'style_guide': 'Professional, data-rich design. Use charts and graphs. Convey security and reliability.',
        'typography': 'Professional fonts like IBM Plex Sans, Noto Sans. Monospace for numbers like JetBrains Mono.',
        'components': ['balance cards', 'transaction lists', 'portfolio charts', 'KPI widgets', 'security badges'],
        'color_schema': ['#1E3A5F', '#059669', '#DC2626', '#FFFFFF', '#F8FAFC'],
    },
    'education': {
        'style_guide': 'Engaging, colorful design that encourages learning. Interactive elements, progress tracking, gamification.',
        'typography': 'Friendly fonts like Nunito, Quicksand, or Comfortaa for headings. Inter for body text.',
        'components': ['course cards', 'progress bars', 'quiz widgets', 'achievement badges', 'calendar events'],
        'color_schema': ['#7C3AED', '#F59E0B', '#10B981', '#3B82F6', '#FEF3C7'],
    },
    'restaurant': {
        'style_guide': 'Warm, appetizing design with food imagery prominence. Rich colors and elegant typography.',
        'typography': 'Elegant serif for headings like Playfair Display or Cormorant. Clean sans-serif for menu items.',
        'components': ['menu cards', 'reservation forms', 'food galleries', 'review sections', 'location maps'],
        'color_schema': ['#92400E', '#DC2626', '#FEF3C7', '#1F2937', '#FFFFFF'],
    },
    'real_estate': {
        'style_guide': 'Luxury, clean design showcasing properties. Large imagery, virtual tours, and clear pricing.',
        'typography': 'Sophisticated fonts like Playfair Display for headings, Lato for descriptions.',
        'components': ['property cards', 'image galleries', 'price displays', 'agent profiles', 'search filters', 'map views'],
        'color_schema': ['#1E3A5F', '#B8860B', '#FFFFFF', '#F8FAFC', '#334155'],
    },
    'fitness': {
        'style_guide': 'Energetic, motivational design with bold colors. Dynamic shapes, progress visualization.',
        'typography': 'Strong, bold fonts like Oswald or Anton for headlines. Clean body text with Roboto.',
        'components': ['workout cards', 'progress rings', 'leaderboards', 'exercise timers', 'nutrition trackers'],
        'color_schema': ['#DC2626', '#F97316', '#1E1E1E', '#FAFAFA', '#10B981'],
    },
    'travel': {
        'style_guide': 'Inspiring, adventure-focused design with destination imagery. Clear booking flows.',
        'typography': 'Adventurous headings with Poppins or Montserrat. Readable prices and details with Inter.',
        'components': ['destination cards', 'booking forms', 'itinerary timelines', 'review summaries', 'photo galleries'],
        'color_schema': ['#0EA5E9', '#F59E0B', '#FFFFFF', '#0F172A', '#E0F2FE'],
    },
    'saas': {
        'style_guide': 'Modern, feature-focused design. Clean pricing tables, feature comparisons, clear onboarding.',
        'typography': 'Tech-forward fonts like Inter, Plus Jakarta Sans with clear hierarchy.',
        'components': ['pricing tables', 'feature cards', 'onboarding steps', 'integration logos', 'testimonial cards', 'CTA sections'],
        'color_schema': ['#6366F1', '#0F172A', '#FFFFFF', '#F1F5F9', '#10B981'],
    },
}

# Design type templates
DESIGN_TYPE_PROMPTS = {
    'landing_page': """Design a high-converting landing page with:
- Hero section with compelling headline, sub-headline, and CTA button
- Trust indicators (logos, testimonials, stats)
- Feature/benefit sections with icons
- Social proof section
- Final CTA section
- Footer with links
Use visual hierarchy to guide the eye from top to bottom.""",

    'dashboard': """Design a data-rich dashboard interface with:
- Navigation sidebar or top bar
- Summary KPI cards at the top
- Charts and graphs (line, bar, donut)
- Activity feed or recent items list
- Quick action buttons
- User profile area
Prioritize data density while maintaining readability.""",

    'mobile_app': """Design a mobile app screen with:
- Top navigation/status bar
- Main content area optimized for touch
- Bottom tab navigation (4-5 items)
- Card-based content layout
- Touch-friendly button sizes (min 44px)
- Safe areas for notch/home indicator
Follow iOS/Android design guidelines.""",

    'social_media': """Design a social media post/ad with:
- Eye-catching visual focal point
- Bold, readable headline text
- Brand logo/watermark placement
- Call-to-action element
- Platform-appropriate dimensions
- High contrast for feed visibility
Optimize for scroll-stopping impact.""",

    'email_template': """Design a professional email template with:
- Pre-header area
- Branded header with logo
- Hero image/banner section
- Content blocks with clear typography
- CTA buttons (clearly visible)
- Footer with unsubscribe link
- Social media icons
Ensure 600px max width for email clients.""",

    'presentation': """Design a presentation slide with:
- Clear title hierarchy
- Supporting visual or data chart
- Minimal text (6x6 rule)
- Consistent brand elements
- Speaker notes area
- Slide number
Use visual storytelling principles.""",

    'business_card': """Design a professional business card with:
- Name and title prominently displayed
- Company logo
- Contact information (phone, email, website)
- Social media handles
- QR code (optional)
- Clean, uncluttered layout
Standard size: 3.5" x 2" (90mm x 50mm).""",
}


def get_enhanced_prompt(prompt: str, design_type: str = 'ui_ux', 
                        industry: str = '', style: str = 'modern',
                        canvas_width: int = 1920, canvas_height: int = 1080) -> str:
    """
    Generate an enhanced, industry-specific prompt from user input.
    
    Args:
        prompt: User's original design request
        design_type: Type of design (ui_ux, graphic, logo, etc.)
        industry: Industry context for specialized prompts
        style: Design style preference
        canvas_width: Canvas width in pixels
        canvas_height: Canvas height in pixels
    
    Returns:
        Enhanced prompt string with industry context and design best practices
    """
    parts = [f"Create a {style} design based on: {prompt}"]
    
    # Add industry context
    industry_key = industry.lower().replace(' ', '_') if industry else ''
    if industry_key in INDUSTRY_PROMPTS:
        ind = INDUSTRY_PROMPTS[industry_key]
        parts.append(f"\nIndustry Context ({industry}):")
        parts.append(f"- Style: {ind['style_guide']}")
        parts.append(f"- Typography: {ind['typography']}")
        parts.append(f"- Suggested components: {', '.join(ind['components'][:4])}")
        parts.append(f"- Color palette: {', '.join(ind['color_schema'])}")
    
    # Add design type context
    design_key = design_type.lower().replace(' ', '_')
    if design_key in DESIGN_TYPE_PROMPTS:
        parts.append(f"\nDesign Type Guidelines:\n{DESIGN_TYPE_PROMPTS[design_key]}")
    
    # Add canvas context
    parts.append(f"\nCanvas: {canvas_width}x{canvas_height}px")
    
    # Add universal design principles
    parts.append("""
Design Principles to Follow:
- Use clear visual hierarchy with size, weight, and color contrast
- Maintain consistent spacing (8px grid system)  
- Ensure text contrast ratio meets WCAG AA (4.5:1 minimum)
- Use no more than 2-3 fonts and 3-5 colors
- Include proper padding and margins for breathing room
- Align elements to a grid for professional appearance""")
    
    return '\n'.join(parts)


# AI error messages for user-facing feedback
AI_ERROR_MESSAGES = {
    'rate_limit': {
        'title': 'Rate Limit Reached',
        'message': 'You\'ve made too many AI requests. Please wait a few minutes before trying again.',
        'suggestion': 'Consider upgrading your plan for higher limits.',
        'retry_after': 60,
    },
    'quota_exceeded': {
        'title': 'Monthly Quota Exceeded',
        'message': 'You\'ve reached your monthly AI generation limit.',
        'suggestion': 'Upgrade to Pro for unlimited AI generations.',
        'retry_after': None,
    },
    'invalid_prompt': {
        'title': 'Invalid Prompt',
        'message': 'The design prompt could not be processed. Try being more specific.',
        'suggestion': 'Include details like design type, colors, industry, and layout preferences.',
        'retry_after': 0,
    },
    'generation_failed': {
        'title': 'Generation Failed',
        'message': 'The AI service encountered an error generating your design.',
        'suggestion': 'Try simplifying your prompt or try again in a moment.',
        'retry_after': 5,
    },
    'service_unavailable': {
        'title': 'AI Service Unavailable',
        'message': 'The AI service is temporarily unavailable.',
        'suggestion': 'Please try again in a few minutes. Our team has been notified.',
        'retry_after': 30,
    },
    'content_blocked': {
        'title': 'Content Policy',
        'message': 'The request was flagged by our content policy filter.',
        'suggestion': 'Please modify your prompt to comply with our content guidelines.',
        'retry_after': 0,
    },
}


def get_ai_error_response(error_type: str, details: str = '') -> dict:
    """Get a user-friendly error response for AI failures."""
    error_info = AI_ERROR_MESSAGES.get(error_type, AI_ERROR_MESSAGES['generation_failed'])
    response = {
        'error': True,
        'error_type': error_type,
        'title': error_info['title'],
        'message': error_info['message'],
        'suggestion': error_info['suggestion'],
    }
    if error_info.get('retry_after') is not None:
        response['retry_after'] = error_info['retry_after']
    if details:
        response['details'] = details
    return response
