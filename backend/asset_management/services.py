"""
Enhanced Asset Management Services
"""
from typing import Dict, List, Any
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Q
from django.conf import settings
import requests


import logging

logger = logging.getLogger('asset_management')


class AIAssetAnalyzer:
    """AI-powered asset analysis using Groq or OpenAI Vision API"""

    def __init__(self):
        self.openai_api_key = getattr(settings, 'OPENAI_API_KEY', '')
        self.groq_api_key = getattr(settings, 'GROQ_API_KEY', '')

    def analyze_image(self, image_url: str) -> Dict:
        """Analyze an image using OpenAI Vision API or Groq."""
        result: Dict[str, Any] = {
            'tags': [],
            'description': '',
            'colors': [],
            'objects': [],
            'text': '',
        }

        if self.openai_api_key:
            try:
                response = requests.post(
                    'https://api.openai.com/v1/chat/completions',
                    headers={'Authorization': f'Bearer {self.openai_api_key}'},
                    json={
                        'model': 'gpt-4o-mini',
                        'messages': [
                            {
                                'role': 'user',
                                'content': [
                                    {
                                        'type': 'text',
                                        'text': (
                                            'Analyze this image. Return a JSON object with: '
                                            '"tags" (list of descriptive tags), '
                                            '"description" (one-sentence description), '
                                            '"colors" (list of dominant hex colors), '
                                            '"objects" (list of detected objects), '
                                            '"text" (any text visible in the image). '
                                            'Return ONLY valid JSON, no markdown.'
                                        ),
                                    },
                                    {'type': 'image_url', 'image_url': {'url': image_url}},
                                ],
                            }
                        ],
                        'max_tokens': 500,
                    },
                    timeout=30,
                )
                response.raise_for_status()
                content = response.json()['choices'][0]['message']['content']
                import json as _json
                parsed = _json.loads(content)
                result.update({k: v for k, v in parsed.items() if k in result})
                return result
            except Exception:
                logger.exception('OpenAI Vision analysis failed, falling back')

        # Fallback: use Groq text model to generate tags from URL/filename
        if self.groq_api_key:
            try:
                filename = image_url.rsplit('/', 1)[-1] if '/' in image_url else image_url
                response = requests.post(
                    'https://api.groq.com/openai/v1/chat/completions',
                    headers={'Authorization': f'Bearer {self.groq_api_key}'},
                    json={
                        'model': 'llama-3.3-70b-versatile',
                        'messages': [
                            {
                                'role': 'user',
                                'content': (
                                    f'Based on the filename "{filename}", suggest '
                                    'descriptive tags and a short description for this '
                                    'image asset. Return JSON: {{"tags": [...], "description": "..."}}.'
                                    ' Return ONLY valid JSON.'
                                ),
                            }
                        ],
                        'max_tokens': 200,
                    },
                    timeout=15,
                )
                response.raise_for_status()
                content = response.json()['choices'][0]['message']['content']
                import json as _json
                parsed = _json.loads(content)
                result['tags'] = parsed.get('tags', [])
                result['description'] = parsed.get('description', '')
                return result
            except Exception:
                logger.exception('Groq asset analysis failed')

        # If no AI service configured, return basic metadata
        result['tags'] = ['unanalyzed']
        result['description'] = 'AI analysis unavailable — configure OPENAI_API_KEY or GROQ_API_KEY'
        return result

    def extract_colors(self, image_url: str) -> List[str]:
        """Extract dominant colors from an image using Pillow."""
        try:
            from PIL import Image
            from io import BytesIO
            from collections import Counter

            resp = requests.get(image_url, timeout=10)
            resp.raise_for_status()
            img = Image.open(BytesIO(resp.content)).convert('RGB')
            img = img.resize((100, 100))  # Downsample for speed
            pixels = list(img.getdata())
            # Get top 5 most common colors
            common = Counter(pixels).most_common(5)
            return [f'#{r:02x}{g:02x}{b:02x}' for (r, g, b), _ in common]
        except Exception:
            logger.exception('Color extraction failed')
            return []

    def generate_embedding(self, text: str) -> List[float]:
        """Generate vector embedding for semantic search using OpenAI."""
        if not self.openai_api_key:
            logger.warning('OPENAI_API_KEY not set — embeddings unavailable')
            return []
        try:
            response = requests.post(
                'https://api.openai.com/v1/embeddings',
                headers={'Authorization': f'Bearer {self.openai_api_key}'},
                json={'model': 'text-embedding-3-small', 'input': text},
                timeout=15,
            )
            response.raise_for_status()
            return response.json()['data'][0]['embedding']
        except Exception:
            logger.exception('Embedding generation failed')
            return []
    
    def search_by_description(self, query: str, assets) -> List:
        """Search assets by natural language description"""
        # In production, use vector similarity search
        
        # Simple text search fallback
        return assets.filter(
            Q(name__icontains=query) |
            Q(ai_description__icontains=query) |
            Q(ai_tags__icontains=query)
        )


class CDNService:
    """Service for CDN operations"""
    
    def __init__(self, integration):
        self.integration = integration
        self.provider = integration.provider
    
    def upload(self, file_content: bytes, filename: str, options: Dict = None) -> Dict:
        """Upload file to CDN"""
        options = options or {}
        
        if self.provider == 'cloudinary':
            return self._upload_cloudinary(file_content, filename, options)
        elif self.provider == 'imgix':
            return self._upload_imgix(file_content, filename, options)
        else:
            return self._upload_generic(file_content, filename, options)
    
    def _upload_cloudinary(self, file_content: bytes, filename: str, options: Dict) -> Dict:
        """Upload to Cloudinary"""
        import base64
        
        url = f"https://api.cloudinary.com/v1_1/{self.integration.cloud_name}/image/upload"
        
        data = {
            'file': f"data:image/png;base64,{base64.b64encode(file_content).decode()}",
            'api_key': self.integration.api_key,
            'folder': options.get('folder', 'assets'),
        }
        
        # Add transformations
        if self.integration.auto_optimize:
            data['transformation'] = 'f_auto,q_auto'
        
        try:
            response = requests.post(url, data=data)
            result = response.json()
            
            return {
                'success': True,
                'url': result.get('secure_url'),
                'public_id': result.get('public_id'),
                'width': result.get('width'),
                'height': result.get('height'),
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _upload_imgix(self, file_content: bytes, filename: str, options: Dict) -> Dict:
        """Upload to Imgix source"""
        # Imgix typically requires S3 or similar as source
        # This would handle the S3 upload and return Imgix URL
        return {'success': False, 'error': 'Imgix requires S3 source configuration'}
    
    def _upload_generic(self, file_content: bytes, filename: str, options: Dict) -> Dict:
        """Generic CDN upload"""
        return {'success': False, 'error': 'Provider not fully supported'}
    
    def get_optimized_url(self, asset, transformations: Dict = None) -> str:
        """Get optimized CDN URL with transformations"""
        if not asset.cdn_url:
            return asset.file_url
        
        transformations = transformations or {}
        
        if self.provider == 'cloudinary':
            return self._get_cloudinary_url(asset, transformations)
        elif self.provider == 'imgix':
            return self._get_imgix_url(asset, transformations)
        
        return asset.cdn_url
    
    def _get_cloudinary_url(self, asset, transformations: Dict) -> str:
        """Build Cloudinary transformation URL"""
        base_url = asset.cdn_url
        
        params = []
        if transformations.get('width'):
            params.append(f"w_{transformations['width']}")
        if transformations.get('height'):
            params.append(f"h_{transformations['height']}")
        if transformations.get('quality'):
            params.append(f"q_{transformations['quality']}")
        if transformations.get('format'):
            params.append(f"f_{transformations['format']}")
        else:
            params.append('f_auto')
        
        if params:
            # Insert transformations into URL
            parts = base_url.split('/upload/')
            if len(parts) == 2:
                return f"{parts[0]}/upload/{','.join(params)}/{parts[1]}"
        
        return base_url
    
    def _get_imgix_url(self, asset, transformations: Dict) -> str:
        """Build Imgix transformation URL"""
        base_url = asset.cdn_url
        
        params = []
        if transformations.get('width'):
            params.append(f"w={transformations['width']}")
        if transformations.get('height'):
            params.append(f"h={transformations['height']}")
        if transformations.get('quality'):
            params.append(f"q={transformations['quality']}")
        if transformations.get('format'):
            params.append(f"fm={transformations['format']}")
        else:
            params.append('auto=format')
        
        if params:
            separator = '&' if '?' in base_url else '?'
            return f"{base_url}{separator}{'&'.join(params)}"
        
        return base_url


class AssetSearchService:
    """Advanced asset search service"""
    
    def __init__(self, user, team=None):
        self.user = user
        self.team = team
    
    def search(self, query: str, filters: Dict = None) -> 'QuerySet':
        """Search assets with filters"""
        from .models import EnhancedAsset
        
        filters = filters or {}
        
        # Base queryset
        queryset = EnhancedAsset.objects.filter(user=self.user, is_archived=False)
        
        if self.team:
            queryset = queryset | EnhancedAsset.objects.filter(team=self.team, is_archived=False)
        
        # Text search
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(ai_description__icontains=query) |
                Q(original_filename__icontains=query)
            )
        
        # Apply filters
        if filters.get('asset_type'):
            queryset = queryset.filter(asset_type=filters['asset_type'])
        
        if filters.get('folder_id'):
            queryset = queryset.filter(folder_id=filters['folder_id'])
        
        if filters.get('tags'):
            queryset = queryset.filter(tags__name__in=filters['tags'])
        
        if filters.get('color'):
            # Search for assets with similar colors
            queryset = queryset.filter(ai_colors__contains=filters['color'])
        
        if filters.get('min_width'):
            queryset = queryset.filter(width__gte=filters['min_width'])
        
        if filters.get('max_size'):
            queryset = queryset.filter(file_size__lte=filters['max_size'])
        
        if filters.get('date_from'):
            queryset = queryset.filter(created_at__gte=filters['date_from'])
        
        if filters.get('date_to'):
            queryset = queryset.filter(created_at__lte=filters['date_to'])
        
        if filters.get('is_favorite'):
            queryset = queryset.filter(is_favorite=True)
        
        if filters.get('unused'):
            queryset = queryset.filter(usage_count=0)
        
        return queryset.distinct()
    
    def ai_search(self, query: str) -> 'QuerySet':
        """AI-powered semantic search"""
        from .models import EnhancedAsset
        
        analyzer = AIAssetAnalyzer()
        
        # Get base queryset
        queryset = EnhancedAsset.objects.filter(user=self.user, is_archived=False)
        
        if self.team:
            queryset = queryset | EnhancedAsset.objects.filter(team=self.team, is_archived=False)
        
        # Use AI search
        return analyzer.search_by_description(query, queryset)


class UnusedAssetDetector:
    """Detect and report unused assets"""
    
    def __init__(self, user, team=None):
        self.user = user
        self.team = team
    
    def detect(self, days_threshold: int = 90) -> Dict:
        """Detect unused assets"""
        from .models import EnhancedAsset, UnusedAssetReport
        
        threshold_date = timezone.now() - timedelta(days=days_threshold)
        
        # Base queryset
        queryset = EnhancedAsset.objects.filter(user=self.user, is_archived=False)
        
        if self.team:
            queryset = queryset | EnhancedAsset.objects.filter(team=self.team, is_archived=False)
        
        # Find unused assets
        unused = queryset.filter(
            Q(last_used__isnull=True) | Q(last_used__lt=threshold_date),
            usage_count=0
        )
        
        unused_list = list(unused.values_list('id', flat=True))
        total_size = unused.aggregate(total=Sum('file_size'))['total'] or 0
        
        # Create report
        report = UnusedAssetReport.objects.create(
            user=self.user,
            team=self.team,
            unused_assets=unused_list,
            total_unused=len(unused_list),
            total_size=total_size,
            unused_days_threshold=days_threshold,
        )
        
        return {
            'report_id': report.id,
            'total_unused': len(unused_list),
            'total_size': total_size,
            'assets': list(unused.values('id', 'name', 'file_size', 'created_at')[:100]),
        }


class BulkOperationService:
    """Handle bulk operations on assets"""
    
    def __init__(self, user):
        self.user = user
    
    def execute(self, operation: str, asset_ids: List[int], parameters: Dict = None) -> Dict:
        """Execute a bulk operation"""
        from .models import EnhancedAsset, BulkOperation
        
        parameters = parameters or {}
        
        # Create operation record
        bulk_op = BulkOperation.objects.create(
            user=self.user,
            operation=operation,
            asset_ids=asset_ids,
            total_assets=len(asset_ids),
            parameters=parameters,
            status='processing',
        )
        
        try:
            assets = EnhancedAsset.objects.filter(
                id__in=asset_ids,
                user=self.user
            )
            
            results = {'processed': [], 'failed': []}
            
            for asset in assets:
                try:
                    self._process_asset(operation, asset, parameters)
                    results['processed'].append(asset.id)
                except Exception as e:
                    results['failed'].append({'id': asset.id, 'error': str(e)})
            
            bulk_op.processed_assets = len(results['processed'])
            bulk_op.results = results
            bulk_op.status = 'completed'
            bulk_op.completed_at = timezone.now()
            bulk_op.save()
            
            return {
                'operation_id': bulk_op.id,
                'processed': len(results['processed']),
                'failed': len(results['failed']),
            }
            
        except Exception as e:
            bulk_op.status = 'failed'
            bulk_op.error_message = str(e)
            bulk_op.save()
            raise
    
    def _process_asset(self, operation: str, asset, parameters: Dict):
        """Process a single asset for bulk operation"""
        from .models import AssetFolder, AssetTag
        
        if operation == 'delete':
            asset.delete()
        
        elif operation == 'move':
            folder_id = parameters.get('folder_id')
            if folder_id:
                folder = AssetFolder.objects.get(id=folder_id, user=self.user)
                asset.folder = folder
                asset.save()
        
        elif operation == 'tag':
            tag_names = parameters.get('tags', [])
            for tag_name in tag_names:
                tag, _ = AssetTag.objects.get_or_create(
                    user=self.user,
                    name=tag_name
                )
                asset.tags.add(tag)
        
        elif operation == 'untag':
            tag_names = parameters.get('tags', [])
            asset.tags.filter(name__in=tag_names).delete()
        
        elif operation == 'archive':
            asset.is_archived = True
            asset.save()
        
        elif operation == 'unarchive':
            asset.is_archived = False
            asset.save()
