from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import PublishedSite
from .serializers import PublishedSiteSerializer
import uuid

class PublishedSiteViewSet(viewsets.ModelViewSet):
    serializer_class = PublishedSiteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PublishedSite.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        # We save and mark it as active currently, 
        # normally this would trigger a celery task to start deployment
        site = serializer.save(user=self.request.user, status='active')
        site.deployment_id = str(uuid.uuid4())
        site.published_url = f"https://{site.subdomain}.designco.site"
        site.save()
