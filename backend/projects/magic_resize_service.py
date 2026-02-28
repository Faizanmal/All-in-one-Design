"""
Magic Resize Service

One-click resize of designs to multiple social media and print formats.
Intelligently repositions and scales elements to fit different aspect ratios.
"""
import copy
import math
import logging
from typing import Optional

logger = logging.getLogger('projects')

# Standard format presets organized by category
FORMAT_PRESETS = {
    # Social Media
    'instagram_post': {'name': 'Instagram Post', 'width': 1080, 'height': 1080, 'category': 'social'},
    'instagram_story': {'name': 'Instagram Story', 'width': 1080, 'height': 1920, 'category': 'social'},
    'instagram_reel': {'name': 'Instagram Reel', 'width': 1080, 'height': 1920, 'category': 'social'},
    'facebook_post': {'name': 'Facebook Post', 'width': 1200, 'height': 630, 'category': 'social'},
    'facebook_cover': {'name': 'Facebook Cover', 'width': 820, 'height': 312, 'category': 'social'},
    'facebook_story': {'name': 'Facebook Story', 'width': 1080, 'height': 1920, 'category': 'social'},
    'twitter_post': {'name': 'Twitter/X Post', 'width': 1200, 'height': 675, 'category': 'social'},
    'twitter_header': {'name': 'Twitter/X Header', 'width': 1500, 'height': 500, 'category': 'social'},
    'linkedin_post': {'name': 'LinkedIn Post', 'width': 1200, 'height': 627, 'category': 'social'},
    'linkedin_cover': {'name': 'LinkedIn Cover', 'width': 1584, 'height': 396, 'category': 'social'},
    'pinterest_pin': {'name': 'Pinterest Pin', 'width': 1000, 'height': 1500, 'category': 'social'},
    'youtube_thumbnail': {'name': 'YouTube Thumbnail', 'width': 1280, 'height': 720, 'category': 'social'},
    'youtube_cover': {'name': 'YouTube Channel Art', 'width': 2560, 'height': 1440, 'category': 'social'},
    'tiktok_video': {'name': 'TikTok Video', 'width': 1080, 'height': 1920, 'category': 'social'},
    'snapchat_ad': {'name': 'Snapchat Ad', 'width': 1080, 'height': 1920, 'category': 'social'},
    'whatsapp_status': {'name': 'WhatsApp Status', 'width': 1080, 'height': 1920, 'category': 'social'},

    # Display Ads
    'leaderboard': {'name': 'Leaderboard (728×90)', 'width': 728, 'height': 90, 'category': 'ads'},
    'medium_rectangle': {'name': 'Medium Rectangle (300×250)', 'width': 300, 'height': 250, 'category': 'ads'},
    'wide_skyscraper': {'name': 'Wide Skyscraper (160×600)', 'width': 160, 'height': 600, 'category': 'ads'},
    'large_rectangle': {'name': 'Large Rectangle (336×280)', 'width': 336, 'height': 280, 'category': 'ads'},
    'half_page': {'name': 'Half Page (300×600)', 'width': 300, 'height': 600, 'category': 'ads'},
    'billboard': {'name': 'Billboard (970×250)', 'width': 970, 'height': 250, 'category': 'ads'},

    # Print
    'a4_portrait': {'name': 'A4 Portrait', 'width': 2480, 'height': 3508, 'category': 'print'},
    'a4_landscape': {'name': 'A4 Landscape', 'width': 3508, 'height': 2480, 'category': 'print'},
    'us_letter': {'name': 'US Letter', 'width': 2550, 'height': 3300, 'category': 'print'},
    'business_card': {'name': 'Business Card', 'width': 1050, 'height': 600, 'category': 'print'},
    'postcard': {'name': 'Postcard', 'width': 1800, 'height': 1200, 'category': 'print'},
    'poster_18x24': {'name': 'Poster 18×24"', 'width': 5400, 'height': 7200, 'category': 'print'},
    'flyer_5x7': {'name': 'Flyer 5×7"', 'width': 1500, 'height': 2100, 'category': 'print'},

    # Presentations
    'presentation_16_9': {'name': 'Presentation 16:9', 'width': 1920, 'height': 1080, 'category': 'presentation'},
    'presentation_4_3': {'name': 'Presentation 4:3', 'width': 1024, 'height': 768, 'category': 'presentation'},

    # Web
    'desktop_wallpaper': {'name': 'Desktop Wallpaper', 'width': 1920, 'height': 1080, 'category': 'web'},
    'mobile_wallpaper': {'name': 'Mobile Wallpaper', 'width': 1080, 'height': 1920, 'category': 'web'},
    'email_header': {'name': 'Email Header', 'width': 600, 'height': 200, 'category': 'web'},
    'web_banner': {'name': 'Web Banner', 'width': 1920, 'height': 400, 'category': 'web'},
    'favicon': {'name': 'Favicon', 'width': 512, 'height': 512, 'category': 'web'},
    'og_image': {'name': 'Open Graph Image', 'width': 1200, 'height': 630, 'category': 'web'},
}


class MagicResizeService:
    """
    Intelligently resizes designs to different format presets.

    Uses smart element repositioning:
    - Scale: proportionally scales all elements
    - Reflow: repositions elements based on importance and reading order
    - Center: centers content in the new canvas
    - Fill: scales to fill while maintaining aspect ratio (crops edges)
    """

    @staticmethod
    def get_presets(category: Optional[str] = None) -> dict:
        """Return all format presets, optionally filtered by category."""
        if category:
            return {k: v for k, v in FORMAT_PRESETS.items() if v['category'] == category}
        return FORMAT_PRESETS

    @staticmethod
    def get_categories() -> list[dict]:
        """Return available categories."""
        return [
            {'id': 'social', 'name': 'Social Media', 'icon': 'share-2'},
            {'id': 'ads', 'name': 'Display Ads', 'icon': 'megaphone'},
            {'id': 'print', 'name': 'Print', 'icon': 'printer'},
            {'id': 'presentation', 'name': 'Presentations', 'icon': 'presentation'},
            {'id': 'web', 'name': 'Web', 'icon': 'globe'},
        ]

    def resize(
        self,
        design_data: dict,
        source_width: int,
        source_height: int,
        target_format: str,
        strategy: str = 'smart',
    ) -> dict:
        """
        Resize a design to a target format.

        Args:
            design_data: The design JSON data containing elements
            source_width: Original canvas width
            source_height: Original canvas height
            target_format: Key from FORMAT_PRESETS or custom format string
            strategy: 'smart', 'scale', 'center', 'fill'

        Returns:
            New design_data dict resized for the target format.
        """
        preset = FORMAT_PRESETS.get(target_format)
        if not preset:
            raise ValueError(f'Unknown format: {target_format}')

        target_width = preset['width']
        target_height = preset['height']

        resized = copy.deepcopy(design_data)

        if strategy == 'smart':
            return self._smart_resize(resized, source_width, source_height, target_width, target_height)
        elif strategy == 'scale':
            return self._scale_resize(resized, source_width, source_height, target_width, target_height)
        elif strategy == 'center':
            return self._center_resize(resized, source_width, source_height, target_width, target_height)
        elif strategy == 'fill':
            return self._fill_resize(resized, source_width, source_height, target_width, target_height)
        else:
            return self._smart_resize(resized, source_width, source_height, target_width, target_height)

    def batch_resize(
        self,
        design_data: dict,
        source_width: int,
        source_height: int,
        target_formats: list[str],
        strategy: str = 'smart',
    ) -> dict[str, dict]:
        """
        Resize to multiple formats at once.

        Returns:
            Dict mapping format key to resized design_data.
        """
        results = {}
        for fmt in target_formats:
            try:
                results[fmt] = self.resize(design_data, source_width, source_height, fmt, strategy)
                results[fmt]['_format'] = FORMAT_PRESETS.get(fmt, {})
            except Exception as exc:
                logger.warning('Resize failed for %s: %s', fmt, exc)
                results[fmt] = {'error': str(exc)}
        return results

    # ------------------------------------------------------------------
    # Resize strategies
    # ------------------------------------------------------------------

    def _smart_resize(self, data, sw, sh, tw, th):
        """
        Smart resize: combines scaling with intelligent repositioning.
        
        - Background elements scale to fill
        - Text elements maintain readability (min font size)
        - Elements near edges stay near edges
        - Center elements stay centered
        """
        elements = data.get('elements', data.get('objects', []))
        if not elements:
            return data

        scale_x = tw / sw
        scale_y = th / sh
        uniform_scale = min(scale_x, scale_y)

        new_elements = []
        for elem in elements:
            new_elem = copy.deepcopy(elem)
            pos = elem.get('position', {})
            size = elem.get('size', {})
            ex = pos.get('x', elem.get('left', 0))
            ey = pos.get('y', elem.get('top', 0))
            ew = size.get('width', elem.get('width', 100))
            eh = size.get('height', elem.get('height', 100))
            elem_type = elem.get('type', elem.get('component_type', ''))

            # Determine element position zone (edge vs center)
            cx_ratio = (ex + ew / 2) / sw  # 0–1 how far right
            cy_ratio = (ey + eh / 2) / sh  # 0–1 how far down

            if elem_type in ('background', 'bg'):
                # Background: scale to fill
                new_ew = tw
                new_eh = th
                new_ex = 0
                new_ey = 0
            else:
                # Scale dimensions
                new_ew = ew * uniform_scale
                new_eh = eh * uniform_scale

                # Reposition: maintain relative position
                new_ex = cx_ratio * tw - new_ew / 2
                new_ey = cy_ratio * th - new_eh / 2

                # Clamp to canvas
                new_ex = max(0, min(new_ex, tw - new_ew))
                new_ey = max(0, min(new_ey, th - new_eh))

            # Text: ensure readability
            if elem_type in ('text', 'i-text', 'textbox'):
                font_size = elem.get('fontSize', elem.get('properties', {}).get('fontSize', 16))
                new_font_size = max(10, round(font_size * uniform_scale))
                if 'fontSize' in new_elem:
                    new_elem['fontSize'] = new_font_size
                if 'properties' in new_elem and 'fontSize' in new_elem['properties']:
                    new_elem['properties']['fontSize'] = new_font_size

            # Write back position
            if 'position' in new_elem:
                new_elem['position'] = {'x': round(new_ex), 'y': round(new_ey)}
            else:
                new_elem['left'] = round(new_ex)
                new_elem['top'] = round(new_ey)

            if 'size' in new_elem:
                new_elem['size'] = {'width': round(new_ew), 'height': round(new_eh)}
            else:
                new_elem['width'] = round(new_ew)
                new_elem['height'] = round(new_eh)

            # Scale other properties
            if 'scaleX' in new_elem:
                new_elem['scaleX'] = new_elem.get('scaleX', 1) * uniform_scale
            if 'scaleY' in new_elem:
                new_elem['scaleY'] = new_elem.get('scaleY', 1) * uniform_scale

            new_elements.append(new_elem)

        if 'elements' in data:
            data['elements'] = new_elements
        elif 'objects' in data:
            data['objects'] = new_elements

        data['_resized'] = {'target_width': tw, 'target_height': th, 'strategy': 'smart'}
        return data

    def _scale_resize(self, data, sw, sh, tw, th):
        """Simple proportional scale of all elements."""
        elements = data.get('elements', data.get('objects', []))
        scale_x = tw / sw
        scale_y = th / sh

        for elem in elements:
            self._apply_scale(elem, scale_x, scale_y)

        data['_resized'] = {'target_width': tw, 'target_height': th, 'strategy': 'scale'}
        return data

    def _center_resize(self, data, sw, sh, tw, th):
        """Scale uniformly and center content on the new canvas."""
        elements = data.get('elements', data.get('objects', []))
        uniform = min(tw / sw, th / sh)
        offset_x = (tw - sw * uniform) / 2
        offset_y = (th - sh * uniform) / 2

        for elem in elements:
            self._apply_scale(elem, uniform, uniform)
            self._apply_offset(elem, offset_x, offset_y)

        data['_resized'] = {'target_width': tw, 'target_height': th, 'strategy': 'center'}
        return data

    def _fill_resize(self, data, sw, sh, tw, th):
        """Scale to fill (may crop) and center."""
        elements = data.get('elements', data.get('objects', []))
        scale = max(tw / sw, th / sh)
        offset_x = (tw - sw * scale) / 2
        offset_y = (th - sh * scale) / 2

        for elem in elements:
            self._apply_scale(elem, scale, scale)
            self._apply_offset(elem, offset_x, offset_y)

        data['_resized'] = {'target_width': tw, 'target_height': th, 'strategy': 'fill'}
        return data

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _apply_scale(elem, sx, sy):
        if 'position' in elem:
            elem['position']['x'] = round(elem['position'].get('x', 0) * sx)
            elem['position']['y'] = round(elem['position'].get('y', 0) * sy)
        else:
            elem['left'] = round(elem.get('left', 0) * sx)
            elem['top'] = round(elem.get('top', 0) * sy)

        if 'size' in elem:
            elem['size']['width'] = round(elem['size'].get('width', 100) * sx)
            elem['size']['height'] = round(elem['size'].get('height', 100) * sy)
        else:
            elem['width'] = round(elem.get('width', 100) * sx)
            elem['height'] = round(elem.get('height', 100) * sy)

    @staticmethod
    def _apply_offset(elem, ox, oy):
        if 'position' in elem:
            elem['position']['x'] = round(elem['position'].get('x', 0) + ox)
            elem['position']['y'] = round(elem['position'].get('y', 0) + oy)
        else:
            elem['left'] = round(elem.get('left', 0) + ox)
            elem['top'] = round(elem.get('top', 0) + oy)
