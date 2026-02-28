"""
Stock Assets Service - Integrates Unsplash, Pexels, and Pixabay APIs
Provides a unified interface for searching and importing stock photos,
videos, and illustrations into designs.
"""
import os
import logging
import hashlib
from typing import Optional
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger('ai_services')

UNSPLASH_BASE = 'https://api.unsplash.com'
PEXELS_BASE = 'https://api.pexels.com/v1'
PEXELS_VIDEO_BASE = 'https://api.pexels.com/videos'
PIXABAY_BASE = 'https://pixabay.com/api'


class StockAssetService:
    """Unified service for searching stock asset providers."""

    def __init__(self):
        self.unsplash_key = os.getenv('UNSPLASH_ACCESS_KEY', '')
        self.pexels_key = os.getenv('PEXELS_API_KEY', '')
        self.pixabay_key = os.getenv('PIXABAY_API_KEY', '')

    # ------------------------------------------------------------------
    # Public search
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        provider: str = 'all',
        media_type: str = 'photo',
        page: int = 1,
        per_page: int = 20,
        orientation: Optional[str] = None,
        color: Optional[str] = None,
    ) -> dict:
        """
        Search stock assets across providers.

        Args:
            query: Search keywords
            provider: 'unsplash', 'pexels', 'pixabay', or 'all'
            media_type: 'photo', 'video', 'illustration', 'vector'
            page: Page number
            per_page: Results per page (max 30)
            orientation: 'landscape', 'portrait', 'squarish'
            color: Color filter (hex or name)

        Returns:
            Dict with 'results' list and 'total' count.
        """
        cache_key = self._cache_key(query, provider, media_type, page, per_page, orientation, color)
        cached = cache.get(cache_key)
        if cached:
            return cached

        per_page = min(per_page, 30)
        results: list[dict] = []
        total = 0

        providers = self._resolve_providers(provider)

        for prov in providers:
            try:
                if prov == 'unsplash' and self.unsplash_key:
                    data = self._search_unsplash(query, media_type, page, per_page, orientation, color)
                elif prov == 'pexels' and self.pexels_key:
                    data = self._search_pexels(query, media_type, page, per_page, orientation, color)
                elif prov == 'pixabay' and self.pixabay_key:
                    data = self._search_pixabay(query, media_type, page, per_page, orientation, color)
                else:
                    continue

                results.extend(data.get('results', []))
                total += data.get('total', 0)
            except Exception as exc:
                logger.warning('Stock search failed for %s: %s', prov, exc)

        response = {'results': results, 'total': total, 'page': page, 'per_page': per_page}
        cache.set(cache_key, response, timeout=600)  # Cache 10 min
        return response

    def get_download_url(self, provider: str, asset_id: str) -> Optional[str]:
        """Get the actual download URL for a stock asset (triggers download tracking where required)."""
        try:
            if provider == 'unsplash':
                return self._unsplash_download(asset_id)
            elif provider == 'pexels':
                return self._pexels_download(asset_id)
            elif provider == 'pixabay':
                return self._pixabay_download(asset_id)
        except Exception as exc:
            logger.error('Download URL fetch failed for %s/%s: %s', provider, asset_id, exc)
        return None

    # ------------------------------------------------------------------
    # Unsplash
    # ------------------------------------------------------------------

    def _search_unsplash(self, query, media_type, page, per_page, orientation, color):
        params = {'query': query, 'page': page, 'per_page': per_page}
        if orientation:
            params['orientation'] = orientation
        if color:
            params['color'] = color

        resp = requests.get(
            f'{UNSPLASH_BASE}/search/photos',
            params=params,
            headers={'Authorization': f'Client-ID {self.unsplash_key}'},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

        return {
            'results': [self._normalize_unsplash(item) for item in data.get('results', [])],
            'total': data.get('total', 0),
        }

    def _normalize_unsplash(self, item: dict) -> dict:
        urls = item.get('urls', {})
        user = item.get('user', {})
        return {
            'id': item['id'],
            'provider': 'unsplash',
            'type': 'photo',
            'title': item.get('description') or item.get('alt_description') or '',
            'thumbnail': urls.get('thumb', ''),
            'preview': urls.get('small', ''),
            'full': urls.get('full', ''),
            'download_url': urls.get('regular', ''),
            'width': item.get('width', 0),
            'height': item.get('height', 0),
            'author': user.get('name', ''),
            'author_url': user.get('links', {}).get('html', ''),
            'license': 'Unsplash License',
            'tags': [t.get('title', '') for t in item.get('tags', [])[:5]],
            'color': item.get('color', ''),
        }

    def _unsplash_download(self, asset_id: str) -> str:
        # Trigger download endpoint per Unsplash guidelines
        resp = requests.get(
            f'{UNSPLASH_BASE}/photos/{asset_id}/download',
            headers={'Authorization': f'Client-ID {self.unsplash_key}'},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json().get('url', '')

    # ------------------------------------------------------------------
    # Pexels
    # ------------------------------------------------------------------

    def _search_pexels(self, query, media_type, page, per_page, orientation, color):
        headers = {'Authorization': self.pexels_key}
        params = {'query': query, 'page': page, 'per_page': per_page}
        if orientation:
            params['orientation'] = orientation
        if color:
            params['color'] = color

        if media_type == 'video':
            url = f'{PEXELS_VIDEO_BASE}/search'
        else:
            url = f'{PEXELS_BASE}/search'

        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if media_type == 'video':
            items = [self._normalize_pexels_video(v) for v in data.get('videos', [])]
        else:
            items = [self._normalize_pexels(p) for p in data.get('photos', [])]

        return {'results': items, 'total': data.get('total_results', 0)}

    def _normalize_pexels(self, item: dict) -> dict:
        src = item.get('src', {})
        return {
            'id': str(item['id']),
            'provider': 'pexels',
            'type': 'photo',
            'title': item.get('alt', ''),
            'thumbnail': src.get('tiny', ''),
            'preview': src.get('medium', ''),
            'full': src.get('original', ''),
            'download_url': src.get('large2x', src.get('original', '')),
            'width': item.get('width', 0),
            'height': item.get('height', 0),
            'author': item.get('photographer', ''),
            'author_url': item.get('photographer_url', ''),
            'license': 'Pexels License',
            'tags': [],
            'color': item.get('avg_color', ''),
        }

    def _normalize_pexels_video(self, item: dict) -> dict:
        files = item.get('video_files', [])
        best = max(files, key=lambda f: f.get('width', 0)) if files else {}
        pic = item.get('video_pictures', [])
        thumb = pic[0].get('picture', '') if pic else ''
        return {
            'id': str(item['id']),
            'provider': 'pexels',
            'type': 'video',
            'title': item.get('url', '').split('/')[-2].replace('-', ' ') if item.get('url') else '',
            'thumbnail': thumb,
            'preview': thumb,
            'full': best.get('link', ''),
            'download_url': best.get('link', ''),
            'width': item.get('width', 0),
            'height': item.get('height', 0),
            'duration': item.get('duration', 0),
            'author': item.get('user', {}).get('name', ''),
            'author_url': item.get('user', {}).get('url', ''),
            'license': 'Pexels License',
            'tags': [],
            'color': '',
        }

    def _pexels_download(self, asset_id: str) -> str:
        resp = requests.get(
            f'{PEXELS_BASE}/photos/{asset_id}',
            headers={'Authorization': self.pexels_key},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json().get('src', {}).get('original', '')

    # ------------------------------------------------------------------
    # Pixabay
    # ------------------------------------------------------------------

    def _search_pixabay(self, query, media_type, page, per_page, orientation, color):
        params = {
            'key': self.pixabay_key,
            'q': query,
            'page': page,
            'per_page': per_page,
            'safesearch': 'true',
        }
        if orientation:
            params['orientation'] = 'horizontal' if orientation == 'landscape' else orientation
        if color:
            params['colors'] = color

        type_map = {
            'photo': 'photo',
            'illustration': 'illustration',
            'vector': 'vector',
        }

        if media_type == 'video':
            url = f'{PIXABAY_BASE}/videos/'
        else:
            url = PIXABAY_BASE + '/'
            params['image_type'] = type_map.get(media_type, 'all')

        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if media_type == 'video':
            items = [self._normalize_pixabay_video(v) for v in data.get('hits', [])]
        else:
            items = [self._normalize_pixabay(p) for p in data.get('hits', [])]

        return {'results': items, 'total': data.get('totalHits', 0)}

    def _normalize_pixabay(self, item: dict) -> dict:
        return {
            'id': str(item['id']),
            'provider': 'pixabay',
            'type': item.get('type', 'photo'),
            'title': item.get('tags', ''),
            'thumbnail': item.get('previewURL', ''),
            'preview': item.get('webformatURL', ''),
            'full': item.get('largeImageURL', ''),
            'download_url': item.get('largeImageURL', ''),
            'width': item.get('imageWidth', 0),
            'height': item.get('imageHeight', 0),
            'author': item.get('user', ''),
            'author_url': f'https://pixabay.com/users/{item.get("user", "")}-{item.get("user_id", "")}/',
            'license': 'Pixabay License',
            'tags': [t.strip() for t in item.get('tags', '').split(',')],
            'color': '',
        }

    def _normalize_pixabay_video(self, item: dict) -> dict:
        videos = item.get('videos', {})
        large = videos.get('large', {}) or videos.get('medium', {})
        return {
            'id': str(item['id']),
            'provider': 'pixabay',
            'type': 'video',
            'title': item.get('tags', ''),
            'thumbnail': f'https://i.vimeocdn.com/video/{item.get("picture_id")}_295x166.jpg',
            'preview': f'https://i.vimeocdn.com/video/{item.get("picture_id")}_640x360.jpg',
            'full': large.get('url', ''),
            'download_url': large.get('url', ''),
            'width': large.get('width', 0),
            'height': large.get('height', 0),
            'duration': item.get('duration', 0),
            'author': item.get('user', ''),
            'author_url': f'https://pixabay.com/users/{item.get("user", "")}-{item.get("user_id", "")}/',
            'license': 'Pixabay License',
            'tags': [t.strip() for t in item.get('tags', '').split(',')],
            'color': '',
        }

    def _pixabay_download(self, asset_id: str) -> str:
        params = {'key': self.pixabay_key, 'id': asset_id}
        resp = requests.get(f'{PIXABAY_BASE}/', params=params, timeout=10)
        resp.raise_for_status()
        hits = resp.json().get('hits', [])
        if hits:
            return hits[0].get('largeImageURL', '')
        return ''

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _resolve_providers(self, provider: str) -> list[str]:
        if provider == 'all':
            return ['unsplash', 'pexels', 'pixabay']
        return [provider]

    def _cache_key(self, *args) -> str:
        raw = ':'.join(str(a) for a in args)
        return f'stock:{hashlib.md5(raw.encode()).hexdigest()}'
