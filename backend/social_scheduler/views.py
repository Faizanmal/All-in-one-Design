from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import SocialAccount, ScheduledPost
from .serializers import SocialAccountSerializer, ScheduledPostSerializer

class SocialAccountViewSet(viewsets.ModelViewSet):
    serializer_class = SocialAccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SocialAccount.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ScheduledPostViewSet(viewsets.ModelViewSet):
    serializer_class = ScheduledPostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ScheduledPost.objects.filter(user=self.request.user).order_by('scheduled_time')

    def perform_create(self, serializer):
        # We save the new scheduled post
        serializer.save(user=self.request.user, status='scheduled')
