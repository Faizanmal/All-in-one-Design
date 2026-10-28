"""
Deterministic logo composition.

The model chooses brand, mark style and palette. This module places a compact
combination mark (symbol + wordmark) dead-center on the artboard so logos
never drift to a corner or misalign mark vs type.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

MARKS = ('mountain', 'abstract', 'circle', 'letter', 'hexagon')


def _hex_ok(value: Any, fallback: str) -> str:
    text = str(value or '').strip()
    if len(text) in (4, 7) and text.startswith('#'):
        try:
            int(text[1:], 16)
            return text.upper() if len(text) == 7 else text
        except ValueError:
            pass
    return fallback


def _mix(a: str, b: str, ratio: float) -> str:
    def parts(value: str) -> Tuple[int, int, int]:
        value = value.lstrip('#')
        if len(value) == 3:
            value = ''.join(ch * 2 for ch in value)
        return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)

    ar, ag, ab = parts(a)
    br, bg, bb = parts(b)
    ratio = max(0.0, min(1.0, ratio))
    return '#{:02X}{:02X}{:02X}'.format(
        round(ar + (br - ar) * ratio),
        round(ag + (bg - ag) * ratio),
        round(ab + (bb - ab) * ratio),
    )


def _is_dark(hex_color: str) -> bool:
    h = hex_color.lstrip('#')
    if len(h) == 3:
        h = ''.join(ch * 2 for ch in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (0.299 * r + 0.587 * g + 0.114 * b) < 150


class LogoLayoutEngine:
    def __init__(self, canvas_width: int, canvas_height: int):
        self.w = max(400, int(canvas_width))
        self.h = max(400, int(canvas_height))
        self.safe = min(self.w, self.h)
        self.scale = max(0.75, min(self.safe / 1080.0, 1.6))
        self.components: List[Dict[str, Any]] = []

    def px(self, value: float) -> int:
        return max(1, int(round(value * self.scale)))

    def fs(self, value: float) -> int:
        return max(18, int(round(value * self.scale)))

    def fit(self, text: Any, width: int, font_size: int) -> str:
        text = str(text or '')
        if not text:
            return ''
        max_chars = max(1, int(width / max(1.0, font_size * 0.55)))
        if len(text) <= max_chars:
            return text
        return text[: max(1, max_chars - 1)].rstrip() + '…'

    def rect(self, x, y, w, h, fill, *, layer=2, radius=0, subtype='mark') -> None:
        self.components.append({
            'type': 'rectangle',
            'subtype': subtype,
            'content': '',
            'position': {'x': int(x), 'y': int(y)},
            'size': {'width': max(1, int(w)), 'height': max(1, int(h))},
            'style': {'fill': fill, 'borderRadius': radius, 'strokeWidth': 0, 'opacity': 1},
            'layer': layer,
        })

    def circle(self, x, y, d, fill, *, layer=2) -> None:
        d = max(8, int(d))
        self.components.append({
            'type': 'circle',
            'subtype': 'circle',
            'content': '',
            'position': {'x': int(x), 'y': int(y)},
            'size': {'width': d, 'height': d},
            'style': {'fill': fill, 'strokeWidth': 0, 'opacity': 1},
            'layer': layer,
        })

    def triangle(self, x, y, w, h, fill, *, layer=2) -> None:
        self.components.append({
            'type': 'shape',
            'subtype': 'triangle',
            'content': '',
            'position': {'x': int(x), 'y': int(y)},
            'size': {'width': max(1, int(w)), 'height': max(1, int(h))},
            'style': {'fill': fill, 'strokeWidth': 0, 'opacity': 1},
            'layer': layer,
        })

    def text(self, content, x, y, w, size, *, fill, weight='bold', align='center', layer=5) -> None:
        content = self.fit(content, w, size)
        if not content:
            return
        self.components.append({
            'type': 'text',
            'subtype': 'wordmark',
            'content': content,
            'position': {'x': int(x), 'y': int(y)},
            'size': {'width': max(1, int(w)), 'height': int(round(size * 1.35))},
            'style': {
                'fill': fill,
                'fontSize': size,
                'fontFamily': 'Inter, Arial, sans-serif',
                'fontWeight': weight,
                'textAlign': align,
                'opacity': 1,
            },
            'layer': layer,
        })

    def compose(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        bg = spec['background']
        primary = spec['primary']
        secondary = spec['secondary']
        brand = spec['brand']
        tagline = spec.get('tagline') or ''
        mark = spec['mark']
        initial = spec.get('initial') or (brand[:1].upper() if brand else 'B')

        self.rect(0, 0, self.w, self.h, bg, layer=0, subtype='background')

        mark_size = self.px(200)
        gap = self.px(28)
        word_size = self.fs(48)
        tag_size = self.fs(18)

        word_w = max(mark_size, int(len(brand) * word_size * 0.56))
        word_w = min(word_w, int(self.w * 0.72))
        tag_w = min(word_w, max(mark_size, int(len(tagline) * tag_size * 0.55))) if tagline else 0

        unit_w = max(mark_size, word_w, tag_w)
        unit_h = mark_size + gap + int(word_size * 1.35)
        if tagline:
            unit_h += self.px(12) + int(tag_size * 1.35)

        origin_x = (self.w - unit_w) // 2
        origin_y = (self.h - unit_h) // 2
        mark_x = origin_x + (unit_w - mark_size) // 2
        mark_y = origin_y

        self._draw_mark(mark, mark_x, mark_y, mark_size, primary, secondary, initial)

        word_y = mark_y + mark_size + gap
        word_x = origin_x + (unit_w - word_w) // 2
        self.text(brand, word_x, word_y, word_w, word_size, fill=primary, weight='bold')

        if tagline:
            tag_y = word_y + int(word_size * 1.35) + self.px(12)
            tag_x = origin_x + (unit_w - tag_w) // 2
            self.text(tagline, tag_x, tag_y, tag_w, tag_size,
                      fill=_mix(primary, bg, 0.45), weight='normal')

        return {
            'components': self.components,
            'layout': {'type': f'logo_{mark}'},
            'metadata': {
                'category': 'logo',
                'layout_mode': 'logo_shell',
                'logotype': 'combination',
                'style': mark,
                'page_background': bg,
                'color_palette': [primary, secondary, bg],
                'canvas_width': self.w,
                'canvas_height': self.h,
                'brand': brand,
            },
        }

    def _draw_mark(self, mark: str, x: int, y: int, size: int,
                   primary: str, secondary: str, initial: str) -> None:
        if mark == 'mountain':
            peak = int(size * 0.62)
            self.triangle(x + int(size * 0.08), y + int(size * 0.28), peak, peak, primary, layer=3)
            self.triangle(x + int(size * 0.38), y + int(size * 0.38), int(peak * 0.78),
                          int(peak * 0.78), secondary, layer=2)
            self.rect(x + int(size * 0.12), y + size - self.px(18), int(size * 0.76),
                      self.px(10), primary, layer=4, radius=self.px(4))
        elif mark == 'circle':
            self.circle(x, y, size, _mix(primary, secondary, 0.15), layer=2)
            inner = int(size * 0.58)
            self.circle(x + (size - inner) // 2, y + (size - inner) // 2, inner, primary, layer=3)
            core = int(size * 0.22)
            self.circle(x + (size - core) // 2, y + (size - core) // 2, core, secondary, layer=4)
        elif mark == 'hexagon':
            self.rect(x + int(size * 0.18), y + int(size * 0.08), int(size * 0.64),
                      int(size * 0.84), primary, layer=2, radius=self.px(16))
            self.triangle(x + int(size * 0.28), y + int(size * 0.22), int(size * 0.44),
                          int(size * 0.44), secondary, layer=3)
        elif mark == 'letter':
            self.circle(x, y, size, primary, layer=2)
            letter_size = self.fs(72)
            letter_fill = '#FFFFFF' if _is_dark(primary) else secondary
            self.text(
                initial, x, y + (size - int(letter_size * 1.2)) // 2,
                size, letter_size, fill=letter_fill, weight='bold', align='center', layer=4,
            )
        else:  # abstract
            self.rect(x + int(size * 0.08), y + int(size * 0.08), int(size * 0.55),
                      int(size * 0.55), primary, layer=2, radius=self.px(20))
            self.circle(x + int(size * 0.38), y + int(size * 0.32), int(size * 0.52),
                        secondary, layer=3)
            self.rect(x + int(size * 0.55), y + int(size * 0.58), int(size * 0.32),
                      int(size * 0.32), primary, layer=4, radius=self.px(10))


def normalize_logo_spec(raw: Any, prompt: str = '',
                        color_scheme: Optional[List[str]] = None) -> Dict[str, Any]:
    raw = raw if isinstance(raw, dict) else {}
    lowered = (prompt or '').lower()

    brand = str(raw.get('brand') or raw.get('name') or '').strip()
    quoted = re.findall(r'["“]([^"”]+)["”]', prompt or '')
    if not brand and quoted:
        brand = quoted[0].strip()
    if not brand:
        match = re.search(r'(?i)logo for\s+["“]?([^"”.\n]+)', prompt or '')
        brand = match.group(1).strip() if match else 'Brand'
    brand = brand.strip()
    # Keep trailing "Co." / "Inc." periods — only drop orphan punctuation.
    if brand.endswith(('..', '.,', ',.')):
        brand = brand.rstrip('.,')

    tagline = str(raw.get('tagline') or '').strip()
    if tagline.lower() in ('none', 'n/a', 'null', 'no tagline'):
        tagline = ''

    mark = str(raw.get('mark') or raw.get('symbol') or '').strip().lower()
    if mark not in MARKS:
        if any(k in lowered for k in ('mountain', 'peak', 'outdoor', 'geo')):
            mark = 'mountain'
        elif any(k in lowered for k in ('tech', 'lab', 'ai', 'abstract', 'energy', 'lumen')):
            mark = 'abstract'
        elif any(k in lowered for k in ('eco', 'nature', 'green', 'organic', 'circle')):
            mark = 'circle'
        elif any(k in lowered for k in ('luxury', 'fashion', 'letter', 'monogram', 'wordmark', 'serif')):
            mark = 'letter'
        else:
            mark = 'abstract'

    primary = _hex_ok(raw.get('primary') or raw.get('accent'), '')
    secondary = _hex_ok(raw.get('secondary'), '')
    background = _hex_ok(raw.get('background'), '')

    if color_scheme:
        colors = [_hex_ok(c, '') for c in color_scheme if str(c).startswith('#')]
        colors = [c for c in colors if c]
        if colors and not primary:
            primary = colors[0]
        if len(colors) > 1 and not secondary:
            secondary = colors[1]
        if len(colors) > 2 and not background:
            background = colors[2]

    for hx in re.findall(r'#[0-9A-Fa-f]{3,6}', prompt or ''):
        val = _hex_ok(hx, '')
        if not val:
            continue
        if not primary:
            primary = val
        elif not secondary and val != primary:
            secondary = val
        elif not background and val not in (primary, secondary):
            background = val

    if not primary:
        primary = '#1B4332' if mark == 'mountain' else '#0F172A'
    if not secondary:
        secondary = _mix(primary, '#FFFFFF', 0.45)
    if not background:
        background = '#FFFFFF'

    return {
        'brand': brand,
        'tagline': tagline,
        'mark': mark,
        'primary': primary,
        'secondary': secondary,
        'background': background,
        'initial': brand[:1].upper() if brand else 'B',
    }


def compose_logo(raw_spec: Any, canvas_width: int, canvas_height: int,
                 prompt: str = '',
                 color_scheme: Optional[List[str]] = None) -> Dict[str, Any]:
    spec = normalize_logo_spec(raw_spec, prompt, color_scheme)
    return LogoLayoutEngine(canvas_width, canvas_height).compose(spec)
