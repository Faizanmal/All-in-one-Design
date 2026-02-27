from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import BrandKitEnforcement, BrandViolationLog
from .serializers import BrandKitEnforcementSerializer, BrandViolationLogSerializer
from design_systems.models import DesignSystem

class BrandKitEnforcementViewSet(viewsets.ModelViewSet):
    serializer_class = BrandKitEnforcementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Allow users to see enforcements for design systems they own or belong to
        return BrandKitEnforcement.objects.filter(design_system__user=self.request.user)

    def list(self, request, *args, **kwargs):
        ds_id = request.query_params.get('design_system_id')
        if ds_id:
            enforcement, created = BrandKitEnforcement.objects.get_or_create(
                design_system_id=ds_id
            )
            serializer = self.get_serializer(enforcement)
            return Response(serializer.data)
        
        return super().list(request, *args, **kwargs)

class BrandViolationLogViewSet(viewsets.ModelViewSet):
    serializer_class = BrandViolationLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BrandViolationLog.objects.filter(enforcement__design_system__user=self.request.user).order_by('-timestamp')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
