"""
Deterministic layout engine for marketing / graphic designs.

Same contract as the UI layout engine: the model supplies copy, palette and
composition intent. This module owns every pixel so sparse LLM placements
(tiny CTAs, decorative shapes floating in empty canvas) cannot happen.
"""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

FORMATS = ('split', 'stacked', 'centered', 'banner')


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
    return (0.299 * r + 0.587 * g + 0.114 * b) < 140


class GraphicLayoutEngine:
    """Flows a graphic spec into a filled, hierarchical composition."""

    def __init__(self, canvas_width: int, canvas_height: int):
        self.w = max(480, int(canvas_width))
        self.h = max(360, int(canvas_height))
        self.scale = max(0.7, min(self.w / 1440.0, self.h / 900.0, 2.0))
        self.components: List[Dict[str, Any]] = []

    def sp(self, value: float) -> int:
        return max(8, int(round(value * self.scale / 8.0)) * 8)

    def px(self, value: float) -> int:
        return int(round(value * self.scale))

    def fs(self, value: float) -> int:
        return max(14, int(round(value * self.scale)))

    def fit(self, text: Any, width: int, font_size: int) -> str:
        text = str(text or '')
        if not text:
            return ''
        max_chars = max(1, int(width / max(1.0, font_size * 0.55)))
        if len(text) <= max_chars:
            return text
        return text[: max(1, max_chars - 1)].rstrip() + '…'

    def wrap(self, text: Any, width: int, font_size: int, max_lines: int = 2) -> List[str]:
        """Break copy into up to max_lines that each fit the width."""
        text = str(text or '').strip()
        if not text:
            return []
        max_chars = max(8, int(width / max(1.0, font_size * 0.55)))
        words = text.split()
        lines: List[str] = []
        current = ''
        for word in words:
            candidate = f'{current} {word}'.strip()
            if len(candidate) <= max_chars:
                current = candidate
                continue
            if current:
                lines.append(current)
            current = word
            if len(lines) >= max_lines - 1:
                # Last line absorbs the remainder, truncated if needed.
                rest = ' '.join([current] + words[words.index(word) + 1:])
                lines.append(self.fit(rest, width, font_size))
                return lines
        if current:
            lines.append(current)
        return lines[:max_lines]

    def rect(self, x, y, w, h, fill, *, layer=1, radius=0, stroke=None,
             stroke_width=0, opacity=1, subtype='surface', rotation=0) -> None:
        style: Dict[str, Any] = {
            'fill': fill,
            'borderRadius': radius,
            'opacity': opacity,
            'strokeWidth': stroke_width or 0,
        }
        if stroke and stroke_width:
            style['stroke'] = stroke
        if rotation:
            style['rotation'] = rotation
        self.components.append({
            'type': 'rectangle',
            'subtype': subtype,
            'content': '',
            'position': {'x': int(x), 'y': int(y)},
            'size': {'width': max(1, int(w)), 'height': max(1, int(h))},
            'style': style,
            'layer': layer,
        })

    def circle(self, x, y, diameter, fill, *, layer=2, opacity=1) -> None:
        d = max(8, int(diameter))
        self.components.append({
            'type': 'circle',
            'subtype': 'circle',
            'content': '',
            'position': {'x': int(x), 'y': int(y)},
            'size': {'width': d, 'height': d},
            'style': {'fill': fill, 'strokeWidth': 0, 'opacity': opacity},
            'layer': layer,
        })

    def text(self, content, x, y, w, size, *, fill='#0F172A', weight='normal',
             layer=5, align='left') -> None:
        content = self.fit(content, w, size)
        if not content:
            return
        self.components.append({
            'type': 'text',
            'subtype': 'copy',
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

    def button(self, label, x, y, w, h, *, fill, text_fill='#FFFFFF', layer=6) -> None:
        size = self.fs(16)
        self.components.append({
            'type': 'button',
            'subtype': 'cta',
            'content': self.fit(label or 'Learn more', w - self.px(24), size),
            'position': {'x': int(x), 'y': int(y)},
            'size': {'width': max(1, int(w)), 'height': max(1, int(h))},
            'style': {
                'fill': fill,
                'backgroundColor': fill,
                'color': text_fill,
                'fontSize': size,
                'fontWeight': '600',
                'borderRadius': self.px(10),
            },
            'layer': layer,
        })

    def media(self, label, x, y, w, h, *, fill, layer=3) -> None:
        self.components.append({
            'type': 'image',
            'subtype': 'media',
            'content': str(label or 'Image'),
            'position': {'x': int(x), 'y': int(y)},
            'size': {'width': max(1, int(w)), 'height': max(1, int(h))},
            'style': {
                'fill': fill,
                'borderRadius': self.px(16),
                'borderColor': _mix(fill, '#000000', 0.08),
                'borderWidth': 1,
            },
            'layer': layer,
        })

    # ---- compositions ----------------------------------------------------

    def compose(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        fmt = spec['format']
        bg = spec['background']
        accent = spec['accent']
        dark = _is_dark(bg)
        text = '#F8FAFC' if dark else '#0F172A'
        muted = _mix(text, bg, 0.45)
        soft = _mix(accent, bg, 0.78 if dark else 0.82)
        media_fill = _mix(accent, '#FFFFFF' if not dark else '#000000', 0.55)

        self.rect(0, 0, self.w, self.h, bg, layer=0, subtype='background')

        # Soft atmospheric accents — always clipped to margins, never the hero.
        pad = self.sp(48)
        self.circle(-self.sp(80), self.h - self.sp(280), self.sp(360), soft,
                    layer=1, opacity=0.55)
        self.circle(self.w - self.sp(200), -self.sp(60), self.sp(280), soft,
                    layer=1, opacity=0.4)

        if fmt == 'split':
            self._split(spec, pad, text, muted, accent, media_fill, dark)
        elif fmt == 'stacked':
            self._stacked(spec, pad, text, muted, accent, media_fill, dark)
        elif fmt == 'banner':
            self._banner(spec, pad, text, muted, accent, media_fill, dark)
        else:
            self._centered(spec, pad, text, muted, accent, media_fill, dark)

        return {
            'components': self.components,
            'layout': {'type': f'graphic_{fmt}'},
            'metadata': {
                'category': 'graphic',
                'layout_mode': 'graphic_shell',
                'format': fmt,
                'page_background': bg,
                'accent': accent,
                'canvas_width': self.w,
                'canvas_height': self.h,
                'brand': spec.get('brand'),
                'headline': spec.get('headline'),
            },
        }

    def _copy_block(self, spec, x, y, w, text, muted, accent, *,
                    align='left', headline_size=None, max_lines_room=None) -> int:
        """Draw brand → headline → subhead. Returns y after the block."""
        cursor = y
        brand = spec.get('brand')
        if brand:
            self.text(brand.upper(), x, cursor, w, self.fs(14),
                      fill=accent, weight='600', align=align)
            cursor += self.px(36)

        headline = spec.get('headline') or 'Untitled'
        h_size = headline_size or self.fs(56)
        # Shrink a notch if a single line still overflows after wrapping prep.
        for _ in range(4):
            lines = self.wrap(headline, w, h_size, max_lines=2)
            if len(lines) == 1 or (lines and not lines[-1].endswith('…')):
                break
            h_size = max(self.fs(32), h_size - 4)

        for line in self.wrap(headline, w, h_size, max_lines=2):
            self.text(line, x, cursor, w, h_size, fill=text, weight='bold', align=align)
            cursor += int(h_size * 1.25)
        cursor += self.px(16)

        subhead = spec.get('subhead')
        if subhead:
            for line in self.wrap(subhead, w, self.fs(20), max_lines=2):
                self.text(line, x, cursor, w, self.fs(20), fill=muted, align=align)
                cursor += self.px(30)
            cursor += self.px(8)
        return cursor

    def _split(self, spec, pad, text, muted, accent, media_fill, dark) -> None:
        gap = self.sp(48)
        col_w = (self.w - pad * 2 - gap) // 2
        left_x = pad
        right_x = pad + col_w + gap

        # Media panel fills the right column almost edge-to-edge vertically.
        media_h = self.h - pad * 2
        self.media(spec.get('media_label') or 'Featured', right_x, pad, col_w, media_h,
                   fill=media_fill)
        # Accent bar on the media edge for polish.
        self.rect(right_x, pad, self.px(10), media_h, accent, layer=4)

        copy_top = pad + self.sp(40)
        after = self._copy_block(spec, left_x, copy_top, col_w - self.sp(16),
                                text, muted, accent, headline_size=self.fs(52))

        btn_w = self.sp(220)
        btn_h = self.px(56)
        btn_y = min(self.h - pad - btn_h, max(after + self.sp(24), self.h // 2))
        self.button(spec.get('cta') or 'Learn more', left_x, btn_y, btn_w, btn_h,
                    fill=accent, text_fill='#FFFFFF' if not _is_dark(accent) else '#0F172A')

    def _stacked(self, spec, pad, text, muted, accent, media_fill, dark) -> None:
        media_h = int(self.h * 0.52)
        media_w = self.w - pad * 2
        self.media(spec.get('media_label') or 'Featured', pad, pad, media_w, media_h,
                   fill=media_fill)
        self.rect(pad, pad + media_h - self.px(8), media_w, self.px(8), accent, layer=4)

        copy_y = pad + media_h + self.sp(36)
        copy_w = min(self.sp(900), self.w - pad * 2)
        after = self._copy_block(spec, pad, copy_y, copy_w, text, muted, accent,
                                headline_size=self.fs(48))

        btn_w = self.sp(220)
        btn_h = self.px(56)
        self.button(spec.get('cta') or 'Learn more', pad,
                    min(self.h - pad - btn_h, after + self.sp(8)),
                    btn_w, btn_h, fill=accent,
                    text_fill='#FFFFFF' if not _is_dark(accent) else '#0F172A')

    def _centered(self, spec, pad, text, muted, accent, media_fill, dark) -> None:
        # Soft media plate behind the copy for presence without stealing focus.
        plate_w = min(self.sp(720), self.w - pad * 2)
        plate_h = min(self.sp(420), int(self.h * 0.55))
        plate_x = (self.w - plate_w) // 2
        plate_y = (self.h - plate_h) // 2 - self.sp(40)
        self.media(spec.get('media_label') or 'Featured', plate_x, plate_y,
                   plate_w, plate_h, fill=media_fill, layer=2)
        self.rect(plate_x, plate_y, plate_w, plate_h,
                  '#000000' if not dark else '#FFFFFF',
                  layer=3, radius=self.px(16), opacity=0.35)

        copy_w = min(self.sp(760), self.w - pad * 2)
        copy_x = (self.w - copy_w) // 2
        # Vertically center the text stack over the plate.
        approx_block = self.px(220)
        copy_y = plate_y + (plate_h - approx_block) // 2
        after = self._copy_block(spec, copy_x, copy_y, copy_w, text, muted, accent,
                                align='center', headline_size=self.fs(48))

        btn_w = self.sp(220)
        btn_h = self.px(56)
        self.button(spec.get('cta') or 'Learn more',
                    (self.w - btn_w) // 2,
                    min(self.h - pad - btn_h, after + self.sp(16)),
                    btn_w, btn_h, fill=accent,
                    text_fill='#FFFFFF' if not _is_dark(accent) else '#0F172A')

    def _banner(self, spec, pad, text, muted, accent, media_fill, dark) -> None:
        # Full-bleed accent strip on the left edge.
        rail = self.sp(24)
        self.rect(0, 0, rail, self.h, accent, layer=1)

        media_w = int(self.w * 0.34)
        media_h = self.h - pad * 2
        media_x = self.w - pad - media_w
        self.media(spec.get('media_label') or 'Featured', media_x, pad, media_w, media_h,
                   fill=media_fill)

        copy_x = pad + rail
        copy_w = media_x - copy_x - self.sp(40)
        copy_y = pad + self.sp(48)
        after = self._copy_block(spec, copy_x, copy_y, copy_w, text, muted, accent,
                                headline_size=self.fs(48))

        btn_w = self.sp(200)
        btn_h = self.px(52)
        self.button(spec.get('cta') or 'Learn more', copy_x,
                    min(self.h - pad - btn_h, after + self.sp(16)),
                    btn_w, btn_h, fill=accent,
                    text_fill='#FFFFFF' if not _is_dark(accent) else '#0F172A')


def _extract_quoted(prompt: str) -> List[str]:
    return [m.strip() for m in re.findall(r'["“]([^"”]+)["”]', prompt or '') if m.strip()]


def _extract_labeled(prompt: str, labels: Tuple[str, ...]) -> Optional[str]:
    for label in labels:
        match = re.search(
            rf'(?i){re.escape(label)}\s*[:\-]\s*["“]?([^"”\n.]+)',
            prompt or '',
        )
        if match:
            return match.group(1).strip().strip('"“”')
    return None


def _prefer_fuller(model_value: str, candidates: List[str], *, min_words: int = 3) -> str:
    """If the model shortened quoted copy, restore the longer original."""
    current = (model_value or '').strip()
    best = current
    for candidate in candidates:
        text = (candidate or '').strip().rstrip('.')
        if not text:
            continue
        if not current:
            best = text
            continue
        # Model returned a prefix/stem of the quoted line.
        if text.lower().startswith(current.lower()) and len(text) > len(current) + 2:
            if len(text) > len(best):
                best = text
        # Model returned something much shorter than an explicit quote.
        elif (len(current.split()) < min_words and len(text.split()) >= min_words
              and current.lower() in text.lower()):
            if len(text) > len(best):
                best = text
    return best


def normalize_graphic_spec(raw: Any, prompt: str = '',
                           color_scheme: Optional[List[str]] = None) -> Dict[str, Any]:
    raw = raw if isinstance(raw, dict) else {}
    lowered = (prompt or '').lower()
    quoted = _extract_quoted(prompt)

    fmt = str(raw.get('format') or '').strip().lower()
    if fmt not in FORMATS:
        if any(k in lowered for k in ('story', 'stories', 'reel', 'poster', 'flyer')):
            fmt = 'stacked'
        elif any(k in lowered for k in ('banner', 'header', 'web banner', 'ad')):
            fmt = 'banner'
        elif any(k in lowered for k in ('centered', 'minimal', 'elegant')):
            fmt = 'centered'
        else:
            fmt = 'split'

    brand = str(raw.get('brand') or '').strip()
    headline = str(raw.get('headline') or raw.get('title') or '').strip()
    subhead = str(raw.get('subhead') or raw.get('subtitle') or raw.get('body') or '').strip()
    cta = str(raw.get('cta') or raw.get('button') or '').strip()
    media_label = str(raw.get('media_label') or raw.get('image_label') or '').strip()

    labeled_brand = _extract_labeled(prompt, ('Brand name', 'Brand', 'Company'))
    labeled_cta = _extract_labeled(prompt, ('CTA', 'button that says', 'button', 'CTA button'))
    if labeled_brand:
        brand = labeled_brand
    if labeled_cta:
        cta = labeled_cta

    # Longest quoted string is almost always the campaign headline.
    if quoted:
        headline = _prefer_fuller(headline, quoted, min_words=4)
        # A shorter remaining quote can be supporting copy.
        extras = [q for q in quoted if q.rstrip('.').lower() != headline.rstrip('.').lower()]
        if extras and (not subhead or len(subhead.split()) < 5):
            subhead = _prefer_fuller(subhead, extras, min_words=4)

    # Recover supporting copy mentioned narratively in the prompt.
    about = re.search(r'(?i)supporting line about\s+([^.,;]+)', prompt or '')
    if about and (not subhead or len(subhead.split()) < 5):
        fragment = about.group(1).strip()
        if fragment and fragment.lower() not in subhead.lower():
            subhead = fragment[0].upper() + fragment[1:]
            if not subhead.endswith('.'):
                subhead += '.'

    if not headline:
        headline = quoted[0] if quoted else (prompt or 'New Collection').strip()
        if len(headline) > 72:
            headline = headline[:69].rsplit(' ', 1)[0] + '…'
    if not subhead:
        subhead = 'Designed for people who care about the details.'
    if not cta:
        cta_match = re.search(r'(?i)(?:says|cta|button)\s+[\"“]([^\"”]+)[\"”]', prompt or '')
        if cta_match:
            cta = cta_match.group(1).strip()
        else:
            cta = 'Shop Now' if any(k in lowered for k in ('shop', 'sale', 'buy', 'product')) else 'Learn more'
    if not brand:
        brand = labeled_brand or 'Studio'
    if not media_label:
        media_label = 'Product'

    accent = _hex_ok(raw.get('accent'), '')
    background = _hex_ok(raw.get('background'), '')
    if color_scheme:
        for color in color_scheme:
            if not accent and str(color).startswith('#'):
                accent = _hex_ok(color, '')
            elif not background and str(color).startswith('#'):
                background = _hex_ok(color, '')

    if not accent:
        accent = '#F97316' if any(k in lowered for k in ('coffee', 'warm', 'summer', 'food')) else '#2563EB'
    if not background:
        # Prefer a strong filled field over the washed-out default the LLM used.
        background = '#1C1917' if fmt in ('split', 'banner') else '#FFF7ED'

    return {
        'format': fmt,
        'brand': brand,
        'headline': headline,
        'subhead': subhead,
        'cta': cta,
        'media_label': media_label,
        'accent': accent,
        'background': background,
    }


def compose_graphic(raw_spec: Any, canvas_width: int, canvas_height: int,
                    prompt: str = '',
                    color_scheme: Optional[List[str]] = None) -> Dict[str, Any]:
    spec = normalize_graphic_spec(raw_spec, prompt, color_scheme)
    return GraphicLayoutEngine(canvas_width, canvas_height).compose(spec)
