"""
AI Background Remover Service

Provides background removal using multiple strategies:
1. rembg (local, fast, no API costs)
2. OpenAI / DALL-E inpainting (cloud, high quality)
3. Remove.bg API (cloud, production-ready)

Falls back through providers based on availability.
"""

import io
import os
import base64
import logging
import hashlib
from typing import Optional
from PIL import Image, ImageFilter

from django.conf import settings
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.utils import timezone

logger = logging.getLogger(__name__)


class BackgroundRemoverService:
    """Remove backgrounds from images using AI."""

    SUPPORTED_FORMATS = {'png', 'jpg', 'jpeg', 'webp', 'bmp', 'tiff'}
    MAX_IMAGE_SIZE = 25 * 1024 * 1024  # 25MB
    MAX_DIMENSION = 4096

    def __init__(self):
        self.remove_bg_api_key = getattr(settings, 'REMOVE_BG_API_KEY', os.environ.get('REMOVE_BG_API_KEY', ''))
        self.openai_api_key = getattr(settings, 'OPENAI_API_KEY', os.environ.get('OPENAI_API_KEY', ''))

    def remove_background(
        self,
        image_data: bytes,
        method: str = 'auto',
        output_format: str = 'png',
        refine_edges: bool = True,
        background_color: Optional[str] = None,
    ) -> dict:
        """
        Remove background from image.

        Args:
            image_data: Raw image bytes
            method: 'auto', 'rembg', 'remove_bg_api', 'basic'
            output_format: Output format (png recommended for transparency)
            refine_edges: Apply edge refinement post-processing
            background_color: Optional hex color for replacement background

        Returns:
            dict with 'image_data' (bytes), 'format', 'width', 'height', 'method_used'
        """
        # Validate input
        if len(image_data) > self.MAX_IMAGE_SIZE:
            raise ValueError(f"Image too large. Maximum size is {self.MAX_IMAGE_SIZE // (1024*1024)}MB")

        try:
            img = Image.open(io.BytesIO(image_data))
        except Exception:
            raise ValueError("Invalid image file")

        # Resize if too large
        if img.width > self.MAX_DIMENSION or img.height > self.MAX_DIMENSION:
            img.thumbnail((self.MAX_DIMENSION, self.MAX_DIMENSION), Image.LANCZOS)

        # Convert to RGB if needed (some formats don't support RGBA input)
        original_mode = img.mode

        # Check cache
        cache_key = f"bg_remove_{hashlib.md5(image_data[:1024]).hexdigest()}_{method}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        # Try methods in order
        result_img = None
        method_used = method

        if method == 'auto':
            # Try rembg first (free, local), then Remove.bg API, then basic
            for m in ['rembg', 'remove_bg_api', 'basic']:
                try:
                    result_img = self._remove_with_method(img, image_data, m)
                    method_used = m
                    break
                except Exception as e:
                    logger.debug(f"Method {m} failed: {e}")
                    continue
        else:
            result_img = self._remove_with_method(img, image_data, method)
            method_used = method

        if result_img is None:
            raise RuntimeError("All background removal methods failed")

        # Post-processing
        if refine_edges:
            result_img = self._refine_edges(result_img)

        # Apply background color if specified
        if background_color:
            result_img = self._apply_background_color(result_img, background_color)

        # Convert to output format
        output_buffer = io.BytesIO()
        save_format = output_format.upper()
        if save_format == 'JPG':
            save_format = 'JPEG'

        if save_format == 'JPEG':
            # JPEG doesn't support transparency, composite on white
            if result_img.mode == 'RGBA':
                bg = Image.new('RGB', result_img.size, (255, 255, 255))
                bg.paste(result_img, mask=result_img.split()[3])
                result_img = bg
            result_img.save(output_buffer, format=save_format, quality=95)
        else:
            if result_img.mode != 'RGBA':
                result_img = result_img.convert('RGBA')
            result_img.save(output_buffer, format=save_format)

        output_bytes = output_buffer.getvalue()

        result = {
            'image_data': output_bytes,
            'image_base64': base64.b64encode(output_bytes).decode('utf-8'),
            'format': output_format,
            'width': result_img.width,
            'height': result_img.height,
            'method_used': method_used,
            'file_size': len(output_bytes),
        }

        # Cache for 30 minutes
        cache.set(cache_key, result, 60 * 30)

        return result

    def _remove_with_method(self, img: Image.Image, raw_data: bytes, method: str) -> Image.Image:
        """Dispatch to specific removal method."""
        if method == 'rembg':
            return self._remove_rembg(raw_data)
        elif method == 'remove_bg_api':
            return self._remove_bg_api(raw_data)
        elif method == 'basic':
            return self._remove_basic(img)
        else:
            raise ValueError(f"Unknown method: {method}")

    def _remove_rembg(self, image_data: bytes) -> Image.Image:
        """Use rembg library for local background removal."""
        try:
            from rembg import remove
            output = remove(image_data)
            return Image.open(io.BytesIO(output)).convert('RGBA')
        except ImportError:
            raise RuntimeError("rembg not installed. Install with: pip install rembg[gpu]")

    def _remove_bg_api(self, image_data: bytes) -> Image.Image:
        """Use Remove.bg API."""
        if not self.remove_bg_api_key:
            raise RuntimeError("REMOVE_BG_API_KEY not configured")

        import requests

        response = requests.post(
            'https://api.remove.bg/v1.0/removebg',
            files={'image_file': ('image.png', image_data)},
            data={'size': 'auto', 'format': 'png'},
            headers={'X-Api-Key': self.remove_bg_api_key},
            timeout=60,
        )

        if response.status_code != 200:
            raise RuntimeError(f"Remove.bg API error: {response.status_code}")

        return Image.open(io.BytesIO(response.content)).convert('RGBA')

    def _remove_basic(self, img: Image.Image) -> Image.Image:
        """
        Basic background removal using color-based segmentation.
        Works reasonably well for images with solid/simple backgrounds.
        """
        img = img.convert('RGBA')
        data = img.getdata()

        # Detect dominant edge color (likely background)
        edge_pixels = []
        w, h = img.size
        for x in range(w):
            edge_pixels.append(data[x])  # top row
            edge_pixels.append(data[(h - 1) * w + x])  # bottom row
        for y in range(h):
            edge_pixels.append(data[y * w])  # left col
            edge_pixels.append(data[y * w + (w - 1)])  # right col

        # Average edge color
        if edge_pixels:
            avg_r = sum(p[0] for p in edge_pixels) // len(edge_pixels)
            avg_g = sum(p[1] for p in edge_pixels) // len(edge_pixels)
            avg_b = sum(p[2] for p in edge_pixels) // len(edge_pixels)
        else:
            avg_r, avg_g, avg_b = 255, 255, 255

        # Remove pixels similar to background color
        threshold = 40
        new_data = []
        for item in data:
            r, g, b = item[0], item[1], item[2]
            dist = ((r - avg_r) ** 2 + (g - avg_g) ** 2 + (b - avg_b) ** 2) ** 0.5
            if dist < threshold:
                new_data.append((r, g, b, 0))  # transparent
            else:
                new_data.append((r, g, b, 255))

        img.putdata(new_data)
        return img

    def _refine_edges(self, img: Image.Image) -> Image.Image:
        """Smooth and refine edges of the alpha channel."""
        if img.mode != 'RGBA':
            return img

        # Extract alpha channel and apply slight blur for smoother edges
        r, g, b, alpha = img.split()

        # Slight gaussian blur on alpha to smooth jagged edges
        alpha = alpha.filter(ImageFilter.GaussianBlur(radius=0.5))

        # Re-threshold to keep edges clean
        alpha = alpha.point(lambda p: 0 if p < 20 else (255 if p > 235 else p))

        img = Image.merge('RGBA', (r, g, b, alpha))
        return img

    def _apply_background_color(self, img: Image.Image, hex_color: str) -> Image.Image:
        """Replace transparent areas with a solid color."""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        bg = Image.new('RGBA', img.size, (r, g, b, 255))
        bg.paste(img, mask=img.split()[3])
        return bg

    def replace_background(
        self,
        image_data: bytes,
        background_image_data: bytes,
    ) -> dict:
        """
        Remove foreground background and composite onto a new background image.
        """
        # Remove background from foreground
        result = self.remove_background(image_data, output_format='png')
        fg = Image.open(io.BytesIO(result['image_data'])).convert('RGBA')

        # Open background
        bg = Image.open(io.BytesIO(background_image_data)).convert('RGBA')
        bg = bg.resize(fg.size, Image.LANCZOS)

        # Composite
        composite = Image.alpha_composite(bg, fg)

        output_buffer = io.BytesIO()
        composite.save(output_buffer, format='PNG')
        output_bytes = output_buffer.getvalue()

        return {
            'image_data': output_bytes,
            'image_base64': base64.b64encode(output_bytes).decode('utf-8'),
            'format': 'png',
            'width': composite.width,
            'height': composite.height,
            'method_used': result['method_used'],
            'file_size': len(output_bytes),
        }
