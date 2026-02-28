"""
AI Service Background Tasks
"""
from celery import shared_task
from django.contrib.auth.models import User
import logging

logger = logging.getLogger('ai_services')


@shared_task(bind=True, max_retries=3)
def generate_layout_async(self, user_id, prompt, design_type):
    """
    Generate layout asynchronously
    This allows long-running AI generations without blocking the API
    """
    try:
        from ai_services.services import AIDesignService
        
        user = User.objects.get(id=user_id)
        service = AIDesignService()
        
        result = service.generate_layout_from_prompt(
            prompt=prompt,
            design_type=design_type,
            user=user
        )
        
        logger.info(f'Async layout generated for user {user.username}')
        return result
        
    except Exception as exc:
        logger.error(f'Failed to generate layout: {exc}')
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def generate_image_async(self, user_id, prompt, size='1024x1024'):
    """Generate image asynchronously using DALL-E"""
    try:
        from ai_services.services import AIImageService
        
        user = User.objects.get(id=user_id)
        service = AIImageService()
        
        result = service.generate_image(prompt, size)
        
        logger.info(f'Async image generated for user {user.username}')
        return result
        
    except Exception as exc:
        logger.error(f'Failed to generate image: {exc}')
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True)
def optimize_ai_prompts(self):
    """Analyze and optimize AI prompt templates based on success rates"""
    try:
        from ai_services.models import AIGenerationRequest, AIPromptTemplate
        
        # Analyze successful vs failed requests
        for template in AIPromptTemplate.objects.filter(is_active=True):
            requests = AIGenerationRequest.objects.filter(
                prompt__icontains=template.name[:20]  # Simple matching
            )
            
            total = requests.count()
            if total > 10:  # Only optimize templates with sufficient data
                success_rate = requests.filter(status='completed').count() / total
                
                # Update success rate
                template.metadata['success_rate'] = round(success_rate, 2)
                template.metadata['total_uses'] = total
                template.save()
        
        logger.info('AI prompt optimization completed')
        return {'status': 'success'}
        
    except Exception as exc:
        logger.error(f'Failed to optimize prompts: {exc}')
        return {'status': 'error', 'message': str(exc)}


@shared_task(bind=True, max_retries=2)
def batch_process_ai_requests(self, request_ids):
    """
    Process multiple AI requests in batch
    Useful for template generation or bulk operations
    """
    try:
        from ai_services.models import AIGenerationRequest
        from ai_services.services import AIDesignService
        
        service = AIDesignService()
        results = []
        
        for request_id in request_ids:
            try:
                request = AIGenerationRequest.objects.get(id=request_id)
                
                if request.request_type == 'layout':
                    service.generate_layout_from_prompt(
                        prompt=request.prompt,
                        design_type=request.parameters.get('design_type', 'ui_ux'),
                        user=request.user
                    )
                    results.append({'id': request_id, 'status': 'success'})
                    
            except Exception as e:
                logger.error(f'Failed to process request {request_id}: {e}')
                results.append({'id': request_id, 'status': 'error', 'error': str(e)})
        
        return {'status': 'success', 'results': results}
        
    except Exception as exc:
        logger.error(f'Batch processing failed: {exc}')
        raise self.retry(exc=exc, countdown=120)
