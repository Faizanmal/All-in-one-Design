"""
Stock Asset Integration Service
Integrates with Unsplash, Pexels, and other stock asset providers
"""
import os
import httpx
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class StockAsset:
    """Unified stock asset representation"""
    id: str
    provider: str
    url: str
    thumbnail_url: str
    preview_url: str
    download_url: str
    width: int
    height: int
    description: str
    photographer: str
    photographer_url: str
    attribution: str
    tags: List[str]
    metadata: Dict


class StockAssetService:
    """Unified service for searching stock assets from multiple providers"""
    
    def __init__(self):
        self.unsplash_api_key = os.getenv('UNSPLASH_ACCESS_KEY', '')
        self.pexels_api_key = os.getenv('PEXELS_API_KEY', '')
        self.pixabay_api_key = os.getenv('PIXABAY_API_KEY', '')
    
    async def search_all(self, query: str, page: int = 1, per_page: int = 20,
                         providers: List[str] = None) -> Dict:
        """
        Search across all configured stock providers
        
        Args:
            query: Search query
            page: Page number
            per_page: Results per page
            providers: List of providers to search, defaults to all
            
        Returns:
            Dict with results from each provider
        """
        providers = providers or ['unsplash', 'pexels', 'pixabay']
        results = {
            'query': query,
            'page': page,
            'per_page': per_page,
            'results': [],
            'total': 0,
            'providers_searched': []
        }
        
        async with httpx.AsyncClient() as client:
            if 'unsplash' in providers and self.unsplash_api_key:
                unsplash_results = await self._search_unsplash(client, query, page, per_page)
                results['results'].extend(unsplash_results['items'])
                results['total'] += unsplash_results['total']
                results['providers_searched'].append('unsplash')
            
            if 'pexels' in providers and self.pexels_api_key:
                pexels_results = await self._search_pexels(client, query, page, per_page)
                results['results'].extend(pexels_results['items'])
                results['total'] += pexels_results['total']
                results['providers_searched'].append('pexels')
            
            if 'pixabay' in providers and self.pixabay_api_key:
                pixabay_results = await self._search_pixabay(client, query, page, per_page)
                results['results'].extend(pixabay_results['items'])
                results['total'] += pixabay_results['total']
                results['providers_searched'].append('pixabay')
        
        return results
    
    async def _search_unsplash(self, client: httpx.AsyncClient, query: str,
                                page: int, per_page: int) -> Dict:
        """Search Unsplash for images"""
        try:
            response = await client.get(
                'https://api.unsplash.com/search/photos',
                params={
                    'query': query,
                    'page': page,
                    'per_page': per_page,
                },
                headers={
                    'Authorization': f'Client-ID {self.unsplash_api_key}'
                }
            )
            response.raise_for_status()
            data = response.json()
            
            items = []
            for photo in data.get('results', []):
                items.append({
                    'id': f"unsplash_{photo['id']}",
                    'provider': 'unsplash',
                    'url': photo['urls']['regular'],
                    'thumbnail_url': photo['urls']['thumb'],
                    'preview_url': photo['urls']['small'],
                    'download_url': photo['urls']['full'],
                    'width': photo['width'],
                    'height': photo['height'],
                    'description': photo.get('description') or photo.get('alt_description', ''),
                    'photographer': photo['user']['name'],
                    'photographer_url': photo['user']['links']['html'],
                    'attribution': f"Photo by {photo['user']['name']} on Unsplash",
                    'tags': [tag['title'] for tag in photo.get('tags', [])],
                    'color': photo.get('color', '#FFFFFF'),
                    'metadata': {
                        'likes': photo.get('likes', 0),
                        'downloads': photo.get('downloads', 0),
                    }
                })
            
            return {
                'items': items,
                'total': data.get('total', 0)
            }
        except Exception as e:
            print(f"Unsplash search error: {e}")
            return {'items': [], 'total': 0}
    
    async def _search_pexels(self, client: httpx.AsyncClient, query: str,
                              page: int, per_page: int) -> Dict:
        """Search Pexels for images"""
        try:
            response = await client.get(
                'https://api.pexels.com/v1/search',
                params={
                    'query': query,
                    'page': page,
                    'per_page': per_page,
                },
                headers={
                    'Authorization': self.pexels_api_key
                }
            )
            response.raise_for_status()
            data = response.json()
            
            items = []
            for photo in data.get('photos', []):
                items.append({
                    'id': f"pexels_{photo['id']}",
                    'provider': 'pexels',
                    'url': photo['src']['large'],
                    'thumbnail_url': photo['src']['tiny'],
                    'preview_url': photo['src']['medium'],
                    'download_url': photo['src']['original'],
                    'width': photo['width'],
                    'height': photo['height'],
                    'description': photo.get('alt', ''),
                    'photographer': photo['photographer'],
                    'photographer_url': photo['photographer_url'],
                    'attribution': f"Photo by {photo['photographer']} on Pexels",
                    'tags': [],
                    'color': photo.get('avg_color', '#FFFFFF'),
                    'metadata': {}
                })
            
            return {
                'items': items,
                'total': data.get('total_results', 0)
            }
        except Exception as e:
            print(f"Pexels search error: {e}")
            return {'items': [], 'total': 0}
    
    async def _search_pixabay(self, client: httpx.AsyncClient, query: str,
                               page: int, per_page: int) -> Dict:
        """Search Pixabay for images"""
        try:
            response = await client.get(
                'https://pixabay.com/api/',
                params={
                    'key': self.pixabay_api_key,
                    'q': query,
                    'page': page,
                    'per_page': per_page,
                    'image_type': 'all',
                }
            )
            response.raise_for_status()
            data = response.json()
            
            items = []
            for photo in data.get('hits', []):
                items.append({
                    'id': f"pixabay_{photo['id']}",
                    'provider': 'pixabay',
                    'url': photo['largeImageURL'],
                    'thumbnail_url': photo['previewURL'],
                    'preview_url': photo['webformatURL'],
                    'download_url': photo['largeImageURL'],
                    'width': photo['imageWidth'],
                    'height': photo['imageHeight'],
                    'description': photo.get('tags', ''),
                    'photographer': photo['user'],
                    'photographer_url': f"https://pixabay.com/users/{photo['user']}-{photo['user_id']}/",
                    'attribution': f"Image by {photo['user']} from Pixabay",
                    'tags': photo.get('tags', '').split(', '),
                    'color': '#FFFFFF',
                    'metadata': {
                        'likes': photo.get('likes', 0),
                        'downloads': photo.get('downloads', 0),
                        'type': photo.get('type', 'photo'),
                    }
                })
            
            return {
                'items': items,
                'total': data.get('totalHits', 0)
            }
        except Exception as e:
            print(f"Pixabay search error: {e}")
            return {'items': [], 'total': 0}
    
    async def get_asset_details(self, provider: str, asset_id: str) -> Optional[Dict]:
        """Get detailed information about a specific asset"""
        async with httpx.AsyncClient() as client:
            if provider == 'unsplash':
                return await self._get_unsplash_details(client, asset_id)
            elif provider == 'pexels':
                return await self._get_pexels_details(client, asset_id)
        return None
    
    async def _get_unsplash_details(self, client: httpx.AsyncClient, photo_id: str) -> Optional[Dict]:
        """Get Unsplash photo details"""
        try:
            response = await client.get(
                f'https://api.unsplash.com/photos/{photo_id}',
                headers={'Authorization': f'Client-ID {self.unsplash_api_key}'}
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            return None
    
    async def _get_pexels_details(self, client: httpx.AsyncClient, photo_id: str) -> Optional[Dict]:
        """Get Pexels photo details"""
        try:
            response = await client.get(
                f'https://api.pexels.com/v1/photos/{photo_id}',
                headers={'Authorization': self.pexels_api_key}
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            return None
    
    async def download_asset(self, provider: str, download_url: str) -> bytes:
        """Download an asset from the provider"""
        async with httpx.AsyncClient() as client:
            # Track download for Unsplash
            if provider == 'unsplash':
                await client.get(
                    download_url,
                    headers={'Authorization': f'Client-ID {self.unsplash_api_key}'},
                    follow_redirects=True
                )
            
            response = await client.get(download_url, follow_redirects=True)
            response.raise_for_status()
            return response.content


# Synchronous wrapper for Django views
def search_stock_assets_sync(query: str, page: int = 1, per_page: int = 20,
                              providers: List[str] = None) -> Dict:
    """Synchronous wrapper for stock asset search"""
    import asyncio
    service = StockAssetService()
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(
        service.search_all(query, page, per_page, providers)
    )
