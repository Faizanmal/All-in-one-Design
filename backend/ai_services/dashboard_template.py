"""
Fixed full-canvas dashboard template.

LLM supplies copy only; geometry is always deterministic so layouts
cannot collapse into a tiny island on an empty canvas.
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple


def extract_dashboard_content(result: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize LLM content JSON or legacy component lists into dashboard copy."""
    brand = str(result.get('brand') or '').strip()
    page_title = str(result.get('page_title') or result.get('title') or '').strip()
    nav_items = result.get('nav_items') or result.get('nav') or []
    if not isinstance(nav_items, list):
        nav_items = []
    nav_items = [str(x).strip() for x in nav_items if str(x).strip()]

    kpis = result.get('kpis') or result.get('metrics') or []
    if not isinstance(kpis, list):
        kpis = []
    normalized_kpis: List[Dict[str, str]] = []
    for item in kpis:
        if isinstance(item, dict):
            normalized_kpis.append({
                'label': str(item.get('label') or item.get('name') or 'Metric').strip(),
                'value': str(item.get('value') or item.get('metric') or '0').strip(),
                'trend': str(item.get('trend') or item.get('delta') or '').strip(),
            })

    activities = result.get('activities') or result.get('activity') or []
    if not isinstance(activities, list):
        activities = []
    normalized_acts: List[Dict[str, str]] = []
    for item in activities:
        if isinstance(item, dict):
            normalized_acts.append({
                'title': str(item.get('title') or item.get('text') or item.get('content') or '').strip(),
                'time': str(item.get('time') or item.get('ago') or '').strip(),
            })
        elif isinstance(item, str) and item.strip():
            normalized_acts.append({'title': item.strip(), 'time': ''})

    chart_title = str(result.get('chart_title') or 'Weekly Progress').strip()
    accent = str(result.get('accent') or result.get('primary') or '#2563EB').strip()
    if not accent.startswith('#') or len(accent) not in (4, 7):
        accent = '#2563EB'

    if not brand or not normalized_kpis:
        texts: List[str] = []
        for c in result.get('components') or []:
            if not isinstance(c, dict):
                continue
            if (c.get('type') or '').lower() not in ('text', 'header', 'footer'):
                continue
            content = str(c.get('content') or '').strip()
            if content:
                texts.append(content)
        if not brand and texts:
            brand = texts[0][:40]
        if not nav_items:
            nav_items = [t for t in texts[1:6] if len(t) < 24]
        if not normalized_kpis:
            normalized_kpis = [
                {'label': 'Active Projects', 'value': '12', 'trend': '+8%'},
                {'label': 'Tasks Due', 'value': '25', 'trend': '-3%'},
                {'label': 'Team Members', 'value': '10', 'trend': '+2'},
                {'label': 'Completion Rate', 'value': '85%', 'trend': '+5%'},
            ]

    if not brand:
        brand = 'FlowTrack'
    if not page_title:
        page_title = 'Overview'
    if len(nav_items) < 4:
        nav_items = (nav_items + ['Overview', 'Projects', 'Team', 'Reports', 'Settings'])[:5]
    if nav_items and nav_items[0].lower() not in ('overview', 'dashboard', 'home'):
        for i, item in enumerate(nav_items):
            if item.lower() in ('overview', 'dashboard', 'home'):
                nav_items.insert(0, nav_items.pop(i))
                break
        else:
            nav_items = ['Overview'] + nav_items
    while len(normalized_kpis) < 4:
        normalized_kpis.append({'label': 'Metric', 'value': '—', 'trend': ''})
    normalized_kpis = normalized_kpis[:4]
    if len(normalized_acts) < 4:
        normalized_acts = (normalized_acts + [
            {'title': 'New activity recorded', 'time': 'just now'},
            {'title': 'Project status updated', 'time': '10m ago'},
            {'title': 'Comment added on task', 'time': '1h ago'},
            {'title': 'Weekly report ready', 'time': 'Yesterday'},
        ])[:5]

    return {
        'brand': brand,
        'nav_items': nav_items[:6],
        'page_title': page_title,
        'kpis': normalized_kpis,
        'chart_title': chart_title or 'Weekly Progress',
        'activities': normalized_acts[:5],
        'accent': accent,
    }


def _trend_color(trend: str) -> str:
    t = str(trend or '')
    if t.startswith('+'):
        return '#16A34A'
    if t.startswith('-'):
        return '#DC2626'
    return '#2563EB'


def compose_fixed_dashboard(result: Dict[str, Any], canvas_width: int, canvas_height: int) -> Dict[str, Any]:
    """
    Build a full-canvas dashboard on strict vertical bands with improved scaling.

    Bands (fractions of canvas height, 1920×1080 reference):
      0–64px     topbar
      KPI band   exclusive — no chart geometry allowed here
      gap        40px clear
      panels     chart | activity — bars clipped to plot box only
    """
    w = max(320, int(canvas_width))
    h = max(240, int(canvas_height))
    sx = w / 1920.0
    sy = h / 1080.0
    scale = max(sx, sy)  # Use max scale for better sizing

    def X(v: float) -> int:
        return int(round(v * sx))

    def Y(v: float) -> int:
        return int(round(v * sy))

    def F(v: float) -> int:
        return max(12, int(round(v * scale)))

    def clamp_box(x: int, y: int, bw: int, bh: int) -> Tuple[int, int, int, int]:
        """Keep position stable; shrink size if needed (never pull y upward into other zones)."""
        x = max(0, int(x))
        y = max(0, int(y))
        bw = max(8, int(bw))
        bh = max(8, int(bh))
        if x + bw > w:
            bw = max(8, w - x)
        if y + bh > h:
            bh = max(8, h - y)
        return x, y, bw, bh

    content = extract_dashboard_content(result or {})
    accent = content['accent']

    # --- Strict bands (design px → canvas) with improved spacing ---
    sidebar_w = X(240)
    topbar_h = Y(64)
    page_pad = Y(24)  # vertical padding uses sy
    page_pad_x = X(24)
    gap_base = X(16)  # Store base gap value
    gap = max(X(12), gap_base)  # Ensure minimum gap
    kpi_h = Y(120)  # Slightly increased for better content fit
    kpi_count = 4
    band_gap = Y(48)  # Increased clear air between KPI row and panels

    main_x = sidebar_w + page_pad_x
    main_right = w - page_pad_x
    main_w = max(X(500), main_right - main_x)
    kpi_y = topbar_h + page_pad

    # Distribute KPI cards with better spacing
    kpi_inner = main_w - gap * (kpi_count - 1)
    kpi_w = max(X(140), kpi_inner // kpi_count)

    kpi_bottom = kpi_y + kpi_h
    panel_y = kpi_bottom + band_gap
    panel_h = max(Y(280), h - panel_y - page_pad)
    if panel_h < Y(240):
        # Prefer shrinking KPI band over letting panels collide upward
        panel_h = max(Y(240), panel_h)
        panel_y = max(kpi_bottom + Y(20), h - page_pad - panel_h)

    chart_w = max(int(main_w * 0.58), X(400)) - gap // 2
    list_w = max(X(240), main_w - chart_w - gap)
    chart_w = main_w - list_w - gap
    list_x = main_x + chart_w + gap

    # Absolute ceiling for any chart geometry — must stay below KPI band
    chart_y_min = panel_y + Y(8)

    components: List[Dict[str, Any]] = []

    def add_rect(subtype, x, y, width, height, fill, layer=1, radius=0, stroke='#E2E8F0', sw=1):
        x, y, width, height = clamp_box(int(x), int(y), int(width), int(height))
        style: Dict[str, Any] = {
            'fill': fill,
            'opacity': 1,
            'borderRadius': radius,
        }
        if fill == '#F1F5F9' or sw <= 0 or not stroke:
            style['strokeWidth'] = 0
        else:
            style['stroke'] = stroke
            style['strokeWidth'] = sw
        components.append({
            'type': 'rectangle',
            'subtype': subtype,
            'content': '',
            'position': {'x': x, 'y': y},
            'size': {'width': width, 'height': height},
            'style': style,
            'layer': layer,
        })

    def add_text(text, x, y, width, height, size, fill='#0F172A', weight='normal', layer=4):
        x, y, width, height = clamp_box(int(x), int(y), int(width), int(height))
        components.append({
            'type': 'text',
            'content': str(text),
            'position': {'x': x, 'y': y},
            'size': {'width': width, 'height': height},
            'style': {
                'fill': fill,
                'fontSize': size,
                'fontFamily': 'Inter, Arial, sans-serif',
                'fontWeight': weight,
                'textAlign': 'left',
                'opacity': 1,
            },
            'layer': layer,
        })

    def add_circle(x, y, diameter, fill, layer=4):
        diameter = max(8, int(diameter))
        x, y, _, _ = clamp_box(int(x), int(y), diameter, diameter)
        components.append({
            'type': 'circle',
            'subtype': 'circle',
            'content': '',
            'position': {'x': x, 'y': y},
            'size': {'width': diameter, 'height': diameter},
            'style': {'fill': fill, 'strokeWidth': 0, 'opacity': 1},
            'layer': layer,
        })

    # -------------------------------------------------------------------------
    # Chrome
    # -------------------------------------------------------------------------
    add_rect('background', 0, 0, w, h, '#F1F5F9', layer=0, stroke='', sw=0)
    add_rect('sidebar', 0, 0, sidebar_w, h, '#FFFFFF', layer=1, stroke='#E2E8F0', sw=1)
    add_rect('topbar', sidebar_w, 0, w - sidebar_w, topbar_h, '#FFFFFF', layer=1, stroke='#E2E8F0', sw=1)

    add_text(content['brand'], X(24), Y(22), sidebar_w - X(40), Y(32), F(20), accent, 'bold', 5)
    nav_y = Y(88)
    for i, item in enumerate(content['nav_items'][:6]):
        active = i == 0
        add_text(
            item,
            X(24),
            nav_y + i * Y(44),
            sidebar_w - X(40),
            Y(28),
            F(14),
            accent if active else '#475569',
            '600' if active else 'normal',
            5,
        )

    title_max_w = X(420)
    add_text(content['page_title'], sidebar_w + X(24), Y(18), title_max_w, Y(32), F(18), '#0F172A', '600', 5)

    avatar_size = Y(36)
    avatar2_x = w - page_pad_x - avatar_size - X(8)
    avatar1_x = avatar2_x - X(12) - avatar_size
    search_w = X(220)
    search_x = avatar1_x - X(16) - search_w
    search_x = max(search_x, sidebar_w + X(24) + title_max_w + X(20))
    search_h = Y(40)
    search_y = max(0, (topbar_h - search_h) // 2)
    add_rect('input_bg', search_x, search_y, search_w, search_h, '#F8FAFC', layer=2, radius=8)
    add_text('Search…', search_x + X(12), search_y + Y(8), search_w - X(24), Y(24), F(13), '#94A3B8', 'normal', 5)
    add_circle(avatar1_x, (topbar_h - avatar_size) // 2, avatar_size, '#0F172A', 5)
    add_circle(avatar2_x, (topbar_h - avatar_size) // 2, avatar_size, accent, 5)

    # -------------------------------------------------------------------------
    # KPI row — exclusive band (layers above chart) with improved styling
    # -------------------------------------------------------------------------
    for i, kpi in enumerate(content['kpis']):
        if i < kpi_count - 1:
            this_w = kpi_w
        else:
            this_w = main_right - (main_x + i * (kpi_w + gap))
        kx = main_x + i * (kpi_w + gap)
        add_rect('kpi_card', kx, kpi_y, this_w, kpi_h, '#FFFFFF', layer=20, radius=12)
        
        # Add subtle shadow effect via stroke
        pad_x = X(20)
        # Label with better spacing
        add_text(kpi['label'], kx + pad_x, kpi_y + Y(16), this_w - pad_x * 2, Y(18), F(13), '#64748B', 'normal', 21)
        # Value with better prominence
        add_text(kpi['value'], kx + pad_x, kpi_y + Y(42), this_w - pad_x * 2, Y(40), F(32), '#0F172A', 'bold', 21)
        # Trend indicator
        trend = kpi.get('trend') or ''
        if trend:
            add_text(
                trend,
                kx + pad_x,
                kpi_y + Y(88),
                this_w - pad_x * 2,
                Y(20),
                F(13),
                _trend_color(trend),
                '600',
                21,
            )

    # -------------------------------------------------------------------------
    # Bottom panels — always below KPI band
    # -------------------------------------------------------------------------
    add_rect('chart_panel', main_x, panel_y, chart_w, panel_h, '#FFFFFF', layer=3, radius=12)
    add_rect('activity_panel', list_x, panel_y, list_w, panel_h, '#FFFFFF', layer=3, radius=12)

    chart_pad = X(24)
    add_text(
        content['chart_title'],
        main_x + chart_pad,
        panel_y + Y(18),
        chart_w - chart_pad * 2,
        Y(26),
        F(16),
        '#0F172A',
        '600',
        5,
    )

    # Plot box — bars fill most of this area (readable, not sparse)
    plot_top = max(chart_y_min, panel_y + Y(60))
    plot_bottom = panel_y + panel_h - Y(36)
    plot_h = max(Y(160), plot_bottom - plot_top)

    # Subtle plot track so the chart region reads clearly
    add_rect(
        'chart_plot',
        main_x + chart_pad,
        plot_top,
        chart_w - chart_pad * 2,
        plot_h,
        '#F8FAFC',
        layer=3,
        radius=8,
        stroke='#E2E8F0',
        sw=1,
    )

    max_bar_h = int(plot_h * 0.82)
    bar_count = 7
    bar_gap = max(X(12), int(X(16) * 0.8))
    bar_area_w = chart_w - chart_pad * 2 - X(32)
    bar_w = max(X(32), (bar_area_w - bar_gap * (bar_count - 1)) // bar_count)
    used_w = bar_count * bar_w + (bar_count - 1) * bar_gap
    bars_x = main_x + chart_pad + X(16) + max(0, (bar_area_w - used_w) // 2)

    ratios = [0.38, 0.72, 0.55, 0.95, 0.48, 0.82, 0.42]
    bar_colors = [accent, '#60A5FA', accent, '#3B82F6', accent, '#60A5FA', accent]
    for i, ratio in enumerate(ratios):
        bh = max(Y(24), int(max_bar_h * ratio))
        bh = min(bh, max_bar_h)
        by = plot_bottom - bh
        if by < plot_top + Y(8):
            by = plot_top + Y(8)
            bh = max(Y(24), plot_bottom - by)
        # Absolute guard vs KPI band
        if by < kpi_bottom + Y(12):
            by = kpi_bottom + Y(12)
            bh = max(Y(24), plot_bottom - by)
        add_rect(
            'chart_bar',
            bars_x + i * (bar_w + bar_gap),
            by,
            bar_w,
            bh,
            bar_colors[i % len(bar_colors)],
            layer=4,
            radius=6,
            stroke='',
            sw=0,
        )

    list_pad = X(24)
    add_text(
        'Recent activity',
        list_x + list_pad,
        panel_y + Y(18),
        list_w - list_pad * 2,
        Y(26),
        F(16),
        '#0F172A',
        '600',
        5,
    )

    row_h = Y(72)
    row_start = panel_y + Y(60)
    avatar_d = Y(32)
    max_rows = max(2, (panel_y + panel_h - Y(20) - row_start) // row_h)

    for i, act in enumerate(content['activities'][:max_rows]):
        cy = row_start + i * row_h
        add_circle(list_x + list_pad, cy + Y(8), avatar_d, '#CBD5E1', 5)
        text_x = list_x + list_pad + avatar_d + X(16)
        text_w = list_w - list_pad * 2 - avatar_d - X(16)
        add_text(act['title'], text_x, cy + Y(2), text_w, Y(24), F(13), '#0F172A', '500', 5)
        if act.get('time'):
            add_text(act['time'], text_x, cy + Y(28), text_w, Y(20), F(11), '#94A3B8', 'normal', 5)

    return {
        'components': components,
        'layout': {'type': 'ui_dashboard_fixed'},
        'metadata': {
            'category': 'ui_ux',
            'layout_mode': 'ui_shell',
            'layout_version': 5,
            'page_background': '#F1F5F9',
            'canvas_width': w,
            'canvas_height': h,
            'kpi_bottom': kpi_bottom,
        },
    }
