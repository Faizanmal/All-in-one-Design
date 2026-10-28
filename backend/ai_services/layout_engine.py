"""
Deterministic layout engine for AI-generated UI designs.

The LLM supplies a semantic spec (which shell, which sections, what copy).
This module owns every pixel. Because sections are flowed into disjoint
vertical bands and each section positions its own children relative to its
own box, overlap and drift are impossible by construction.

Spec shape (all keys optional, everything is defaulted):
{
  "shell": "sidebar" | "topbar" | "plain",
  "brand": "FitTrack",
  "page_title": "Dashboard",
  "nav": ["Dashboard", "Workouts", ...],
  "accent": "#2563EB",
  "sections": [
    {"type": "stat_row", "items": [{"label","value","trend"}]},
    {"type": "chart", "title", "chart": "bar"|"line", "series": [0.0-1.0],
     "labels": ["Mon", ...]},
    {"type": "list", "title", "items": [{"title","meta"}]},
    {"type": "cards", "title", "columns": 3, "items": [{"title","body"}]},
    {"type": "table", "title", "columns": [...], "rows": [[...]]},
    {"type": "form", "title", "fields": [{"label","placeholder"}], "submit"},
    {"type": "hero", "title", "body", "cta"},
    {"type": "text", "title", "body"},
    {"type": "media", "title"}
  ]
}
"""
from __future__ import annotations

import logging
import math
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

PAGE_BG = '#F1F5F9'
SURFACE = '#FFFFFF'
BORDER = '#E2E8F0'
TRACK = '#F8FAFC'
TEXT_PRIMARY = '#0F172A'
TEXT_SECONDARY = '#64748B'
TEXT_MUTED = '#94A3B8'
POSITIVE = '#16A34A'
NEGATIVE = '#DC2626'

DEFAULT_ACCENT = '#2563EB'

# Sections that should absorb leftover vertical space so the page fills.
FLEXIBLE = {'chart', 'list', 'table', 'cards', 'media', 'hero'}

# Sections whose height can be reduced without hiding content. Everything else
# (list, table, form) renders a fixed number of rows and would silently drop
# entries, so those are only compressed as a last resort.
SAFE_COMPRESS = {'chart', 'media', 'hero', 'cards', 'text', 'stat_row'}

# Interior metrics, shared by the measure and render passes so a section is
# never measured shorter than the rows it is about to draw (which silently
# truncated list items and form fields).
PANEL_TOP = 20          # panel padding above the title
TITLE_BLOCK = 38        # space a panel title consumes
PANEL_BOTTOM = 16

LIST_ROW = 60
TABLE_HEAD = 34
TABLE_HEAD_GAP = 6
TABLE_ROW = 40
FORM_PAD = 28
FORM_TITLE = 44
FORM_BLOCK = 72
FORM_SUBMIT = 72
CARD_ROW = 150

LIST_CHROME = PANEL_TOP + TITLE_BLOCK + PANEL_BOTTOM
TABLE_CHROME = PANEL_TOP + TITLE_BLOCK + TABLE_HEAD + TABLE_HEAD_GAP + PANEL_BOTTOM
FORM_CHROME = 26 + FORM_TITLE + FORM_SUBMIT + FORM_PAD

# Natural (unscaled, 1440x900-reference) heights per section type.
NATURAL_HEIGHT = {
    'stat_row': 116,
    'chart': 320,
    'list': 320,
    'cards': 240,
    'table': 300,
    'form': 360,
    'hero': 300,
    'text': 150,
    'media': 260,
}

# Smallest height at which a section still reads correctly. The fit pass
# compresses toward these before dropping a section the user asked for.
MIN_HEIGHT = {
    'stat_row': 96,
    'chart': 200,
    'list': 180,
    'cards': 160,
    'table': 200,
    'form': 300,
    'hero': 240,
    'text': 88,
    'media': 140,
}


def _hex_ok(value: Any, fallback: str) -> str:
    text = str(value or '').strip()
    if len(text) in (4, 7) and text.startswith('#'):
        try:
            int(text[1:], 16)
            return text.upper()
        except ValueError:
            pass
    return fallback


def _mix(hex_color: str, other: str, ratio: float) -> str:
    """Blend two hex colors. ratio=0 returns hex_color, 1 returns other."""
    def parts(value: str) -> Tuple[int, int, int]:
        value = value.lstrip('#')
        if len(value) == 3:
            value = ''.join(ch * 2 for ch in value)
        return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)

    ar, ag, ab = parts(hex_color)
    br, bg, bb = parts(other)
    ratio = max(0.0, min(1.0, ratio))
    return '#{:02X}{:02X}{:02X}'.format(
        round(ar + (br - ar) * ratio),
        round(ag + (bg - ag) * ratio),
        round(ab + (bb - ab) * ratio),
    )


def _trend_color(trend: str) -> str:
    text = str(trend or '').strip()
    if text.startswith('+'):
        return POSITIVE
    if text.startswith('-'):
        return NEGATIVE
    return TEXT_SECONDARY


class LayoutEngine:
    """Flows a semantic spec into exact, non-overlapping component geometry."""

    def __init__(self, canvas_width: int, canvas_height: int, accent: str = DEFAULT_ACCENT):
        self.w = max(480, int(canvas_width))
        self.h = max(360, int(canvas_height))
        self.accent = _hex_ok(accent, DEFAULT_ACCENT)
        self.accent_soft = _mix(self.accent, '#FFFFFF', 0.45)
        # One uniform scale keeps proportions intact. It has to respect BOTH
        # axes: keying off width alone makes sections taller than a short
        # canvas can hold, so a larger canvas would fit less content.
        self.scale = max(0.7, min(self.w / 1440.0, self.h / 900.0, 2.2))
        self.components: List[Dict[str, Any]] = []

    # ---- unit helpers -----------------------------------------------------

    def sp(self, value: float) -> int:
        """Scale a spacing/size value and snap it to the 8px grid."""
        return max(8, int(round(value * self.scale / 8.0)) * 8)

    def px(self, value: float) -> int:
        """Scale a value without grid snapping (for interior offsets)."""
        return int(round(value * self.scale))

    def fs(self, value: float) -> int:
        """Scale a font size, keeping it legible."""
        return max(11, int(round(value * self.scale)))

    def fit(self, text: Any, width: int, font_size: int) -> str:
        """Truncate text so it cannot overflow its box (IText does not wrap)."""
        text = str(text or '')
        if not text:
            return ''
        max_chars = max(1, int(width / max(1.0, font_size * 0.55)))
        if len(text) <= max_chars:
            return text
        return text[:max(1, max_chars - 1)].rstrip() + '…'

    # ---- emit helpers -----------------------------------------------------

    def rect(self, x, y, w, h, fill, *, layer=1, radius=0, stroke=None, stroke_width=0,
             subtype='surface', rotation=0) -> None:
        style: Dict[str, Any] = {'fill': fill, 'borderRadius': radius, 'opacity': 1}
        if rotation:
            style['rotation'] = rotation
        if stroke and stroke_width:
            style['stroke'] = stroke
            style['strokeWidth'] = stroke_width
        else:
            style['strokeWidth'] = 0
        self.components.append({
            'type': 'rectangle',
            'subtype': subtype,
            'content': '',
            'position': {'x': int(x), 'y': int(y)},
            'size': {'width': max(1, int(w)), 'height': max(1, int(h))},
            'style': style,
            'layer': layer,
        })

    def card(self, x, y, w, h, *, layer=1, radius=None) -> None:
        self.rect(
            x, y, w, h, SURFACE,
            layer=layer,
            radius=self.px(12) if radius is None else radius,
            stroke=BORDER, stroke_width=1,
            subtype='card',
        )

    def text(self, content, x, y, w, size, *, fill=TEXT_PRIMARY, weight='normal',
             layer=4, align='left') -> None:
        content = self.fit(content, w, size)
        if not content:
            return
        self.components.append({
            'type': 'text',
            'subtype': 'label',
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

    def circle(self, x, y, diameter, fill, *, layer=4) -> None:
        diameter = max(8, int(diameter))
        self.components.append({
            'type': 'circle',
            'subtype': 'circle',
            'content': '',
            'position': {'x': int(x), 'y': int(y)},
            'size': {'width': diameter, 'height': diameter},
            'style': {'fill': fill, 'strokeWidth': 0, 'opacity': 1},
            'layer': layer,
        })

    def button(self, label, x, y, w, h, *, fill=None, layer=5, font_size=None) -> None:
        size = font_size or self.fs(14)
        self.components.append({
            'type': 'button',
            'subtype': 'button',
            'content': self.fit(label or 'Action', w - self.px(16), size),
            'position': {'x': int(x), 'y': int(y)},
            'size': {'width': max(1, int(w)), 'height': max(1, int(h))},
            'style': {
                'fill': fill or self.accent,
                'backgroundColor': fill or self.accent,
                'color': '#FFFFFF',
                'fontSize': size,
                'fontWeight': '600',
                'borderRadius': self.px(8),
            },
            'layer': layer,
        })

    def input(self, placeholder, x, y, w, h, *, layer=5) -> None:
        self.components.append({
            'type': 'input',
            'subtype': 'input',
            'content': self.fit(placeholder or '', w - self.px(24), self.fs(13)),
            'position': {'x': int(x), 'y': int(y)},
            'size': {'width': max(1, int(w)), 'height': max(1, int(h))},
            'style': {'borderColor': BORDER, 'borderWidth': 1, 'borderRadius': self.px(8)},
            'layer': layer,
        })

    # ---- section measuring / rendering ------------------------------------

    def natural_height(self, section: Dict[str, Any]) -> int:
        stype = section.get('type', 'text')
        base = NATURAL_HEIGHT.get(stype, 200)

        # A few extra px of slack absorbs grid-snap rounding, so scaling never
        # shaves off the last row.
        slack = 8

        if stype == 'cards':
            items = section.get('items') or []
            columns = max(1, int(section.get('columns') or 3))
            rows = max(1, -(-len(items) // columns))
            base = TITLE_BLOCK + rows * CARD_ROW
        elif stype == 'list':
            items = section.get('items') or []
            base = LIST_CHROME + max(1, len(items)) * LIST_ROW + slack
        elif stype == 'table':
            rows = section.get('rows') or []
            base = TABLE_CHROME + max(1, len(rows)) * TABLE_ROW + slack
        elif stype == 'form':
            fields = section.get('fields') or []
            base = FORM_CHROME + max(1, len(fields)) * FORM_BLOCK + slack

        return self.sp(base)

    def render_section(self, section: Dict[str, Any], x: int, y: int, w: int, h: int) -> None:
        renderer = {
            'stat_row': self._stat_row,
            'chart': self._chart,
            'list': self._list,
            'cards': self._cards,
            'table': self._table,
            'form': self._form,
            'hero': self._hero,
            'text': self._text_block,
            'media': self._media,
        }.get(section.get('type', 'text'), self._text_block)
        renderer(section, x, y, w, h)

    def _panel_title(self, title: Any, x: int, y: int, w: int) -> int:
        """Draw a panel heading, return the y offset consumed."""
        if not title:
            return 0
        self.text(title, x, y, w, self.fs(16), weight='600')
        return self.px(TITLE_BLOCK)

    def _stat_row(self, section, x, y, w, h) -> None:
        items = [i for i in (section.get('items') or []) if isinstance(i, dict)]
        if not items:
            return
        count = min(len(items), 5)
        items = items[:count]
        gap = self.sp(16)
        card_w = (w - gap * (count - 1)) // count
        pad = self.px(20)

        for index, item in enumerate(items):
            # Last card absorbs the rounding remainder so the row ends flush.
            cw = card_w if index < count - 1 else w - (card_w + gap) * (count - 1)
            cx = x + index * (card_w + gap)
            self.card(cx, y, cw, h, layer=2)
            inner = cw - pad * 2
            self.text(item.get('label'), cx + pad, y + self.px(16), inner,
                      self.fs(13), fill=TEXT_SECONDARY)
            self.text(item.get('value'), cx + pad, y + self.px(42), inner,
                      self.fs(30), weight='bold', layer=5)
            trend = str(item.get('trend') or '').strip()
            if trend and h > self.px(96):
                self.text(trend, cx + pad, y + h - self.px(30), inner,
                          self.fs(12), fill=_trend_color(trend), weight='600', layer=5)

    def _chart(self, section, x, y, w, h) -> None:
        self.card(x, y, w, h, layer=2)
        pad = self.px(24)
        inner_x = x + pad
        inner_w = w - pad * 2
        top = y + self.px(PANEL_TOP)
        top += self._panel_title(section.get('title') or 'Overview', inner_x, top, inner_w)

        plot_y = top
        plot_h = max(self.px(80), (y + h - pad) - plot_y)
        self.rect(inner_x, plot_y, inner_w, plot_h, TRACK, layer=2,
                  radius=self.px(8), stroke=BORDER, stroke_width=1, subtype='plot')

        series = [
            max(0.05, min(1.0, float(v)))
            for v in (section.get('series') or [])
            if isinstance(v, (int, float))
        ] or [0.38, 0.72, 0.55, 0.95, 0.48, 0.82, 0.6]
        series = series[:12]

        labels = [str(l) for l in (section.get('labels') or [])][:len(series)]
        label_band = self.px(24) if labels else 0

        gutter = self.px(16)
        bars_x = inner_x + gutter
        bars_w = inner_w - gutter * 2
        base_y = plot_y + plot_h - self.px(12) - label_band
        max_bar = max(self.px(24), base_y - plot_y - self.px(12))

        if section.get('chart') == 'line':
            step = bars_w / max(1, len(series) - 1) if len(series) > 1 else bars_w
            points = [
                (bars_x + step * index, base_y - max_bar * value)
                for index, value in enumerate(series)
            ]
            # Fabric has no polyline, so each segment is a thin rotated rect.
            thickness = max(2, self.px(3))
            for (x1, y1), (x2, y2) in zip(points, points[1:]):
                length = math.hypot(x2 - x1, y2 - y1)
                if length < 1:
                    continue
                angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
                self.rect(round(x1), round(y1 - thickness / 2), round(length), thickness,
                          self.accent, layer=3, radius=0, subtype='line', rotation=angle)
            for gx, gy in points:
                dot = self.px(9)
                self.circle(round(gx - dot / 2), round(gy - dot / 2), dot, self.accent, layer=5)
                inner = self.px(4)
                self.circle(round(gx - inner / 2), round(gy - inner / 2), inner, SURFACE, layer=6)
            self.rect(bars_x, base_y, bars_w, max(2, self.px(2)), BORDER, layer=2)
            if labels:
                for index, (gx, _) in enumerate(points):
                    if index >= len(labels):
                        break
                    slot = self.px(60)
                    self.text(labels[index], round(gx - slot / 2), base_y + self.px(8), slot,
                              self.fs(11), fill=TEXT_MUTED, align='center', layer=4)
        else:
            count = len(series)
            bar_gap = self.px(14)
            bar_w = max(self.px(14), (bars_w - bar_gap * (count - 1)) // count)
            used = bar_w * count + bar_gap * (count - 1)
            start = bars_x + max(0, (bars_w - used) // 2)
            for index, value in enumerate(series):
                bh = max(self.px(16), int(max_bar * value))
                bx = start + index * (bar_w + bar_gap)
                self.rect(bx, base_y - bh, bar_w, bh,
                          self.accent if index % 2 == 0 else self.accent_soft,
                          layer=4, radius=self.px(6), subtype='bar')
                if labels and index < len(labels):
                    self.text(labels[index], bx, base_y + self.px(6), bar_w,
                              self.fs(11), fill=TEXT_MUTED, align='center', layer=4)

    def _list(self, section, x, y, w, h) -> None:
        self.card(x, y, w, h, layer=2)
        pad = self.px(24)
        inner_x = x + pad
        inner_w = w - pad * 2
        top = y + self.px(PANEL_TOP)
        top += self._panel_title(section.get('title') or 'Recent activity', inner_x, top, inner_w)

        items = [i for i in (section.get('items') or []) if isinstance(i, dict)]
        if not items:
            return
        row_h = self.px(LIST_ROW)
        capacity = max(1, int((y + h - self.px(PANEL_BOTTOM) - top) // row_h))
        avatar = self.px(30)

        for index, item in enumerate(items[:capacity]):
            ry = top + index * row_h
            self.circle(inner_x, ry + self.px(4), avatar, _mix(self.accent, '#FFFFFF', 0.72), layer=4)
            tx = inner_x + avatar + self.px(14)
            tw = inner_w - avatar - self.px(14)
            self.text(item.get('title'), tx, ry, tw, self.fs(13), weight='500')
            meta = item.get('meta') or item.get('time')
            if meta:
                self.text(meta, tx, ry + self.px(22), tw, self.fs(11), fill=TEXT_MUTED)

    def _cards(self, section, x, y, w, h) -> None:
        top = y
        if section.get('title'):
            top += self._panel_title(section['title'], x, y, w)

        items = [i for i in (section.get('items') or []) if isinstance(i, dict)]
        if not items:
            return
        columns = max(1, min(int(section.get('columns') or 3), 4))
        gap = self.sp(16)
        rows = max(1, -(-len(items) // columns))
        card_w = (w - gap * (columns - 1)) // columns
        avail = (y + h) - top
        card_h = max(self.px(96), (avail - gap * (rows - 1)) // rows)
        pad = self.px(18)

        for index, item in enumerate(items[:rows * columns]):
            col = index % columns
            row = index // columns
            cw = card_w if col < columns - 1 else w - (card_w + gap) * (columns - 1)
            cx = x + col * (card_w + gap)
            cy = top + row * (card_h + gap)
            self.card(cx, cy, cw, card_h, layer=2)
            self.rect(cx + pad, cy + pad, self.px(36), self.px(36),
                      _mix(self.accent, '#FFFFFF', 0.8), layer=3, radius=self.px(8))
            inner = cw - pad * 2
            self.text(item.get('title'), cx + pad, cy + pad + self.px(48), inner,
                      self.fs(15), weight='600')
            self.text(item.get('body'), cx + pad, cy + pad + self.px(72), inner,
                      self.fs(12), fill=TEXT_SECONDARY)

    def _table(self, section, x, y, w, h) -> None:
        self.card(x, y, w, h, layer=2)
        pad = self.px(24)
        inner_x = x + pad
        inner_w = w - pad * 2
        top = y + self.px(PANEL_TOP)
        top += self._panel_title(section.get('title') or 'Records', inner_x, top, inner_w)

        columns = [str(c) for c in (section.get('columns') or [])][:5]
        rows = [r for r in (section.get('rows') or []) if isinstance(r, list)]
        if not columns:
            return
        col_w = inner_w // len(columns)

        header_h = self.px(TABLE_HEAD)
        self.rect(inner_x, top, inner_w, header_h, TRACK, layer=3, radius=self.px(6))
        for index, name in enumerate(columns):
            self.text(name, inner_x + index * col_w + self.px(10), top + self.px(9),
                      col_w - self.px(16), self.fs(12), fill=TEXT_SECONDARY, weight='600', layer=4)

        row_h = self.px(TABLE_ROW)
        body_top = top + header_h + self.px(TABLE_HEAD_GAP)
        capacity = max(1, int((y + h - self.px(PANEL_BOTTOM) - body_top) // row_h))
        for r_index, row in enumerate(rows[:capacity]):
            ry = body_top + r_index * row_h
            if r_index:
                self.rect(inner_x, ry, inner_w, 1, BORDER, layer=3)
            for c_index in range(len(columns)):
                value = row[c_index] if c_index < len(row) else ''
                self.text(value, inner_x + c_index * col_w + self.px(10), ry + self.px(12),
                          col_w - self.px(16), self.fs(12),
                          fill=TEXT_PRIMARY if c_index == 0 else TEXT_SECONDARY, layer=4)

    def _form(self, section, x, y, w, h) -> None:
        form_w = min(w, self.sp(520))
        fx = x + (w - form_w) // 2
        self.card(fx, y, form_w, h, layer=2)
        pad = self.px(FORM_PAD)
        inner_x = fx + pad
        inner_w = form_w - pad * 2
        top = y + self.px(26)

        title = section.get('title') or 'Sign up'
        self.text(title, inner_x, top, inner_w, self.fs(22), weight='bold')
        top += self.px(FORM_TITLE)

        fields = section.get('fields') or []
        normalized: List[Dict[str, str]] = []
        for field in fields:
            if isinstance(field, dict):
                normalized.append({
                    'label': str(field.get('label') or 'Field'),
                    'placeholder': str(field.get('placeholder') or ''),
                })
            elif isinstance(field, str):
                normalized.append({'label': field, 'placeholder': ''})
        if not normalized:
            normalized = [{'label': 'Email', 'placeholder': 'you@example.com'},
                          {'label': 'Password', 'placeholder': '••••••••'}]

        field_h = self.px(42)
        block = self.px(FORM_BLOCK)
        submit_reserve = self.px(FORM_SUBMIT)
        capacity = max(1, int((y + h - pad - submit_reserve - top) // block))

        for field in normalized[:capacity]:
            self.text(field['label'], inner_x, top, inner_w, self.fs(12),
                      fill=TEXT_SECONDARY, weight='500')
            self.input(field['placeholder'], inner_x, top + self.px(20), inner_w, field_h)
            top += block

        self.button(section.get('submit') or 'Continue', inner_x,
                    y + h - pad - field_h, inner_w, field_h)

    def _hero(self, section, x, y, w, h) -> None:
        text_w = int(w * 0.54)
        mid = y + h // 2

        title = section.get('title') or 'Build something great'
        title_size = self.fs(40)
        body_size = self.fs(16)

        self.text(title, x, mid - self.px(60), text_w, title_size, weight='bold')
        self.text(section.get('body'), x, mid - self.px(6), text_w, body_size,
                  fill=TEXT_SECONDARY)

        btn_w = self.sp(180)
        btn_h = self.px(48)
        self.button(section.get('cta') or 'Get started', x, mid + self.px(32), btn_w, btn_h)

        art_x = x + text_w + self.sp(32)
        art_w = w - text_w - self.sp(32)
        if art_w > self.px(120):
            art_h = min(h - self.px(16), int(h * 0.86))
            art_y = y + (h - art_h) // 2
            self.rect(art_x, art_y, art_w, art_h, _mix(self.accent, '#FFFFFF', 0.82),
                      layer=2, radius=self.px(16))
            badge = min(art_w, art_h) // 3
            self.rect(art_x + (art_w - badge) // 2, art_y + (art_h - badge) // 2,
                      badge, badge, self.accent_soft, layer=3, radius=self.px(12))

    def _text_block(self, section, x, y, w, h) -> None:
        top = y
        if section.get('title'):
            self.text(section['title'], x, top, w, self.fs(22), weight='bold')
            top += self.px(38)
        body = section.get('body')
        if body:
            self.text(body, x, top, w, self.fs(14), fill=TEXT_SECONDARY)

    def _media(self, section, x, y, w, h) -> None:
        top = y
        if section.get('title'):
            top += self._panel_title(section['title'], x, y, w)
        self.components.append({
            'type': 'image',
            'subtype': 'media',
            'content': str(section.get('title') or 'Image'),
            'position': {'x': int(x), 'y': int(top)},
            'size': {'width': int(w), 'height': max(self.px(80), (y + h) - top)},
            'style': {'fill': _mix(self.accent, '#FFFFFF', 0.86), 'borderRadius': self.px(12)},
            'layer': 2,
        })

    # ---- chrome ----------------------------------------------------------

    def _sidebar(self, spec, width: int) -> None:
        self.rect(0, 0, width, self.h, SURFACE, layer=1, stroke=BORDER,
                  stroke_width=1, subtype='sidebar')
        pad = self.px(24)
        inner = width - pad * 2
        self.text(spec['brand'], pad, self.px(26), inner, self.fs(19),
                  fill=self.accent, weight='bold', layer=5)

        nav_y = self.px(90)
        step = self.px(44)
        for index, item in enumerate(spec['nav']):
            active = index == 0
            if active:
                self.rect(self.px(12), nav_y - self.px(8), width - self.px(24), step - self.px(6),
                          _mix(self.accent, '#FFFFFF', 0.9), layer=2, radius=self.px(8))
            self.text(item, pad, nav_y, inner, self.fs(14),
                      fill=self.accent if active else TEXT_SECONDARY,
                      weight='600' if active else 'normal', layer=5)
            nav_y += step

    def _topbar(self, spec, left: int, height: int) -> None:
        self.rect(left, 0, self.w - left, height, SURFACE, layer=1, stroke=BORDER,
                  stroke_width=1, subtype='topbar')
        pad = self.px(24)
        title_w = self.sp(360)
        self.text(spec['page_title'], left + pad, (height - self.fs(18)) // 2,
                  title_w, self.fs(18), weight='600', layer=5)

        avatar = self.px(34)
        a2 = self.w - pad - avatar
        a1 = a2 - self.px(12) - avatar
        search_w = self.sp(240)
        search_x = a1 - self.px(20) - search_w
        if search_x > left + pad + title_w + self.px(20):
            search_h = self.px(36)
            search_y = (height - search_h) // 2
            self.rect(search_x, search_y, search_w, search_h, TRACK, layer=2,
                      radius=self.px(8), stroke=BORDER, stroke_width=1)
            self.text('Search…', search_x + self.px(12), search_y + self.px(9),
                      search_w - self.px(24), self.fs(13), fill=TEXT_MUTED, layer=5)
        self.circle(a1, (height - avatar) // 2, avatar, TEXT_PRIMARY, layer=5)
        self.circle(a2, (height - avatar) // 2, avatar, self.accent, layer=5)

    # ---- fitting ---------------------------------------------------------

    def min_height(self, section: Dict[str, Any]) -> int:
        return self.sp(MIN_HEIGHT.get(section.get('type', 'text'), 120))

    def max_height(self, section: Dict[str, Any]) -> int:
        """Ceiling on how much space a section can usefully absorb.

        Content-bound sections (a 3-row list, a 4-row table) cannot fill extra
        height - they would just render a tall panel of whitespace - so only
        genuinely elastic sections are allowed to stretch.
        """
        stype = section.get('type', 'text')
        if stype in ('chart', 'media'):
            return self.sp(620)
        if stype == 'hero':
            return self.sp(440)
        if stype == 'stat_row':
            return self.sp(148)
        if stype == 'text':
            return self.sp(240)
        if stype == 'cards':
            items = section.get('items') or []
            columns = max(1, int(section.get('columns') or 3))
            rows = max(1, -(-len(items) // columns))
            # A card holds an icon, a title and one line of body; letting it grow
            # much past that just renders a tall box of whitespace.
            return self.sp(TITLE_BLOCK + rows * 172)
        # list / table / form are bound by how many rows they actually have.
        return self.natural_height(section)

    def _fit_sections(self, sections: List[Dict[str, Any]], available: int,
                      gap: int) -> Tuple[List[Dict[str, Any]], List[int]]:
        """Choose how many sections to show and how tall each one is.

        Order of preference: show everything at natural height, else compress
        toward per-type minimums, and only drop trailing sections when even the
        compressed stack cannot fit.
        """
        count = len(sections)
        while count > 1:
            candidates = sections[:count]
            gaps = gap * (count - 1)
            floor = sum(self.min_height(s) for s in candidates) + gaps
            if floor <= available:
                break
            count -= 1

        kept = sections[:max(1, count)]
        gaps = gap * (len(kept) - 1)
        heights = [self.natural_height(s) for s in kept]
        budget = available - gaps
        total = sum(heights)

        if total > budget:
            heights = self._compress(kept, heights, total - budget)
            remaining = sum(heights) - budget
            if remaining > 0:
                heights[-1] = max(self.px(72), heights[-1] - remaining)
        elif total < budget:
            heights = self._distribute(kept, heights, budget - total)

        return kept, heights

    def _compress(self, kept: List[Dict[str, Any]], heights: List[int],
                  deficit: int) -> List[int]:
        """Reclaim vertical space, draining elastic sections before row-based
        ones so no list item, table row or form field is silently dropped."""
        floors = [self.min_height(s) for s in kept]
        tiers = (
            [i for i, s in enumerate(kept) if s.get('type') in SAFE_COMPRESS],
            [i for i, s in enumerate(kept) if s.get('type') not in SAFE_COMPRESS],
        )

        for tier in tiers:
            if deficit <= 0:
                break
            slack = {i: max(0, heights[i] - floors[i]) for i in tier}
            donors = [i for i in tier if slack[i] > 0]
            pool = sum(slack.values())
            if not donors or pool <= 0:
                continue
            take = min(deficit, pool)
            consumed = 0
            for position, index in enumerate(donors):
                if position == len(donors) - 1:
                    cut = min(slack[index], take - consumed)
                else:
                    cut = min(slack[index], int(take * slack[index] / pool))
                heights[index] -= cut
                consumed += cut
            deficit -= consumed

        return heights

    def _distribute(self, kept: List[Dict[str, Any]], heights: List[int],
                    leftover: int) -> List[int]:
        """Water-fill leftover space into flexible sections, respecting caps."""
        caps = [self.max_height(s) for s in kept]
        targets = [i for i, s in enumerate(kept) if s.get('type') in FLEXIBLE]
        targets = targets or list(range(len(kept)))

        # Repeat because clamping one section frees its share for the others.
        for _ in range(4):
            open_targets = [i for i in targets if heights[i] < caps[i]]
            if leftover <= 0 or not open_targets:
                break
            weight_total = sum(heights[i] for i in open_targets) or 1
            granted = 0
            for position, index in enumerate(open_targets):
                if position == len(open_targets) - 1:
                    share = leftover - granted
                else:
                    share = int(leftover * heights[index] / weight_total)
                room = caps[index] - heights[index]
                share = max(0, min(share, room))
                heights[index] += share
                granted += share
            leftover -= granted
            if granted == 0:
                break

        return heights

    # ---- composition -----------------------------------------------------

    def compose(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        shell = spec['shell']
        self.rect(0, 0, self.w, self.h, PAGE_BG, layer=0, subtype='background')

        rail_w = 0
        topbar_h = 0
        if shell == 'sidebar':
            rail_w = max(self.sp(200), min(self.sp(260), int(self.w * 0.16)))
            self._sidebar(spec, rail_w)
        if shell in ('sidebar', 'topbar'):
            topbar_h = self.px(68)
            self._topbar(spec, rail_w, topbar_h)

        pad_x = self.sp(24)
        pad_y = self.sp(24)
        content_x = rail_w + pad_x
        content_w = self.w - content_x - pad_x
        content_y = topbar_h + pad_y
        content_h = self.h - content_y - pad_y

        if shell == 'plain':
            # Landing/auth pages read better with a wider gutter and no chrome.
            gutter = max(pad_x, int(self.w * 0.06))
            content_x = gutter
            content_w = self.w - gutter * 2
            content_y = pad_y * 2
            content_h = self.h - content_y - pad_y * 2

        sections = spec['sections']
        gap = self.sp(28)
        kept, kept_heights = self._fit_sections(sections, content_h, gap)

        cursor = content_y
        if shell == 'plain':
            # Landing and auth pages read as intentional when centered; app
            # shells stay top-aligned like a real dashboard.
            slack = content_h - (sum(kept_heights) + gap * (len(kept) - 1))
            if slack > gap:
                cursor += slack // 2
        for section, height in zip(kept, kept_heights):
            self.render_section(section, content_x, cursor, content_w, height)
            cursor += height + gap

        return {
            'components': self.components,
            'layout': {'type': f'ui_{shell}', 'sections': [s.get('type') for s in kept]},
            'metadata': {
                'category': 'ui_ux',
                'layout_mode': 'ui_shell',
                'shell': shell,
                'page_background': PAGE_BG,
                'accent': self.accent,
                'canvas_width': self.w,
                'canvas_height': self.h,
                'section_types': [s.get('type') for s in kept],
                'sections_rendered': len(kept),
                'sections_requested': len(sections),
            },
        }


def normalize_spec(raw: Any, prompt: str = '') -> Dict[str, Any]:
    """Coerce whatever the LLM returned into a spec the engine can flow."""
    raw = raw if isinstance(raw, dict) else {}

    shell = str(raw.get('shell') or '').strip().lower()
    if shell not in ('sidebar', 'topbar', 'plain'):
        shell = 'sidebar'

    brand = str(raw.get('brand') or '').strip() or 'Untitled'
    page_title = str(raw.get('page_title') or raw.get('title') or '').strip() or 'Overview'

    nav = [str(n).strip() for n in (raw.get('nav') or []) if str(n).strip()]
    if shell == 'sidebar' and len(nav) < 3:
        nav = (nav + ['Overview', 'Reports', 'Team', 'Settings'])[:5]
    nav = nav[:7]

    accent = _hex_ok(raw.get('accent'), DEFAULT_ACCENT)

    sections: List[Dict[str, Any]] = []
    for entry in (raw.get('sections') or []):
        if not isinstance(entry, dict):
            continue
        stype = str(entry.get('type') or '').strip().lower()
        if stype in ('stats', 'kpi', 'kpis', 'metrics', 'stat_row'):
            stype = 'stat_row'
        elif stype in ('chart', 'graph', 'charts'):
            stype = 'chart'
        elif stype in ('list', 'feed', 'activity', 'timeline'):
            stype = 'list'
        elif stype in ('cards', 'features', 'grid'):
            stype = 'cards'
        elif stype in ('table', 'rows'):
            stype = 'table'
        elif stype in ('form', 'fields', 'inputs'):
            stype = 'form'
        elif stype in ('hero', 'banner'):
            stype = 'hero'
        elif stype in ('media', 'image', 'gallery'):
            stype = 'media'
        elif stype in ('text', 'copy', 'paragraph'):
            stype = 'text'
        else:
            continue
        entry = dict(entry)
        entry['type'] = stype
        sections.append(entry)

    if not sections:
        sections = _default_sections(prompt)

    return {
        'shell': shell,
        'brand': brand,
        'page_title': page_title,
        'nav': nav,
        'accent': accent,
        'sections': sections[:6],
    }


def _default_sections(prompt: str) -> List[Dict[str, Any]]:
    """Reasonable structure when the model gives us nothing usable."""
    lowered = (prompt or '').lower()
    if any(k in lowered for k in ('form', 'sign up', 'signup', 'register', 'login')):
        return [{
            'type': 'form',
            'title': 'Create your account',
            'fields': [
                {'label': 'Full name', 'placeholder': 'Jane Doe'},
                {'label': 'Email', 'placeholder': 'you@example.com'},
                {'label': 'Password', 'placeholder': '••••••••'},
            ],
            'submit': 'Create account',
        }]
    if any(k in lowered for k in ('landing', 'hero', 'marketing', 'pricing')):
        return [
            {'type': 'hero', 'title': 'Ship faster', 'body': 'Everything you need in one place.',
             'cta': 'Get started'},
            {'type': 'cards', 'title': 'Features', 'columns': 3, 'items': [
                {'title': 'Fast', 'body': 'Built for speed.'},
                {'title': 'Simple', 'body': 'Clear by default.'},
                {'title': 'Secure', 'body': 'Safe from day one.'},
            ]},
        ]
    return [
        {'type': 'stat_row', 'items': [
            {'label': 'Total', 'value': '128', 'trend': '+8%'},
            {'label': 'Active', 'value': '42', 'trend': '+3%'},
            {'label': 'Members', 'value': '16', 'trend': '+2'},
            {'label': 'Completion', 'value': '85%', 'trend': '+5%'},
        ]},
        {'type': 'chart', 'title': 'Progress over time', 'chart': 'bar',
         'series': [0.4, 0.72, 0.55, 0.95, 0.48, 0.82, 0.6],
         'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']},
        {'type': 'list', 'title': 'Recent activity', 'items': [
            {'title': 'New record created', 'meta': '2m ago'},
            {'title': 'Report generated', 'meta': '1h ago'},
            {'title': 'Settings updated', 'meta': 'Yesterday'},
        ]},
    ]


def compose_layout(raw_spec: Any, canvas_width: int, canvas_height: int,
                   prompt: str = '', accent_override: Optional[str] = None) -> Dict[str, Any]:
    """Normalize an LLM spec and flow it into exact geometry."""
    spec = normalize_spec(raw_spec, prompt)
    accent = _hex_ok(accent_override, spec['accent']) if accent_override else spec['accent']
    engine = LayoutEngine(canvas_width, canvas_height, accent)
    return engine.compose(spec)
