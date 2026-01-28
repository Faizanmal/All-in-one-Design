from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
import secrets

from .models import (
    Agency, AgencyMember, Client, ClientPortal, ClientFeedback,
    APIKey, AgencyBilling, AgencyInvoice, BrandLibrary
)
from .serializers import (
    AgencySerializer, AgencyCreateSerializer, AgencyMemberSerializer,
    ClientSerializer, ClientPortalSerializer, ClientFeedbackSerializer,
    APIKeySerializer, AgencyBillingSerializer, AgencyInvoiceSerializer,
    BrandLibrarySerializer
)


class AgencyViewSet(viewsets.ModelViewSet):
    """ViewSet for managing agencies"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Get agencies owned by user or where user is a member
        return Agency.objects.filter(
            models.Q(owner=self.request.user) | 
            models.Q(members__user=self.request.user)
        ).distinct()
    
    def get_serializer_class(self):
        if self.action in ['create']:
            return AgencyCreateSerializer
        return AgencySerializer
    
    def perform_create(self, serializer):
        agency = serializer.save(owner=self.request.user)
        # Create billing record
        AgencyBilling.objects.create(agency=agency)
        # Add owner as admin member
        AgencyMember.objects.create(
            agency=agency,
            user=self.request.user,
            role='admin'
        )
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get agency members"""
        agency = self.get_object()
        members = agency.members.all()
        return Response(AgencyMemberSerializer(members, many=True).data)
    
    @action(detail=True, methods=['post'])
    def invite_member(self, request, pk=None):
        """Invite a new team member"""
        agency = self.get_object()
        
        # In production, send invitation email
        return Response({
            'status': 'Invitation sent',
            'email': request.data.get('email'),
            'role': request.data.get('role', 'designer')
        })
    
    @action(detail=True, methods=['post'])
    def verify_domain(self, request, pk=None):
        """Verify custom domain"""
        agency = self.get_object()
        
        # In production, verify DNS records
        agency.domain_verified = True
        agency.save()
        
        return Response({'status': 'Domain verified', 'domain': agency.custom_domain})
    
    @action(detail=True, methods=['get'])
    def dashboard(self, request, pk=None):
        """Get agency dashboard data"""
        agency = self.get_object()
        
        return Response({
            'clients': agency.clients.count(),
            'members': agency.members.count(),
            'active_projects': 0,  # Calculate from projects
            'pending_feedback': ClientFeedback.objects.filter(
                client__agency=agency, 
                is_resolved=False
            ).count(),
            'revenue_this_month': 0,  # Calculate from invoices
        })


class ClientViewSet(viewsets.ModelViewSet):
    """ViewSet for managing clients"""
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        agency_id = self.kwargs.get('agency_pk')
        return Client.objects.filter(agency_id=agency_id)
    
    def perform_create(self, serializer):
        agency_id = self.kwargs.get('agency_pk')
        agency = get_object_or_404(Agency, id=agency_id)
        client = serializer.save(agency=agency)
        
        # Create client portal
        ClientPortal.objects.create(client=client)
    
    @action(detail=True, methods=['post'])
    def generate_portal_link(self, request, agency_pk=None, pk=None):
        """Generate new portal access link"""
        client = self.get_object()
        
        if not hasattr(client, 'portal'):
            ClientPortal.objects.create(client=client)
        
        # Regenerate token
        client.portal.access_token = secrets.token_urlsafe(32)
        client.portal.save()
        
        return Response({
            'portal_url': f"/client-portal/{client.portal.access_token}",
            'token': client.portal.access_token
        })
    
    @action(detail=True, methods=['get'])
    def feedback(self, request, agency_pk=None, pk=None):
        """Get client feedback"""
        client = self.get_object()
        feedback = client.feedback.all()
        return Response(ClientFeedbackSerializer(feedback, many=True).data)


class ClientPortalViewSet(viewsets.ModelViewSet):
    """ViewSet for client portal settings"""
    serializer_class = ClientPortalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        agency_id = self.kwargs.get('agency_pk')
        return ClientPortal.objects.filter(client__agency_id=agency_id)


class ClientFeedbackViewSet(viewsets.ModelViewSet):
    """ViewSet for client feedback"""
    serializer_class = ClientFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        agency_id = self.kwargs.get('agency_pk')
        return ClientFeedback.objects.filter(client__agency_id=agency_id)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, agency_pk=None, pk=None):
        """Mark feedback as resolved"""
        feedback = self.get_object()
        feedback.is_resolved = True
        feedback.resolved_by = request.user
        feedback.resolved_at = timezone.now()
        feedback.save()
        return Response({'status': 'resolved'})


class APIKeyViewSet(viewsets.ModelViewSet):
    """ViewSet for API key management"""
    serializer_class = APIKeySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        agency_id = self.kwargs.get('agency_pk')
        return APIKey.objects.filter(agency_id=agency_id)
    
    def perform_create(self, serializer):
        agency_id = self.kwargs.get('agency_pk')
        agency = get_object_or_404(Agency, id=agency_id)
        
        # Generate secret
        secret = secrets.token_urlsafe(32)
        
        serializer.save(
            agency=agency,
            secret=make_password(secret)
        )
        
        # Return the secret once (it won't be stored in plain text)
        return Response({
            **serializer.data,
            'secret': secret  # Show once, then hash
        })
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, agency_pk=None, pk=None):
        """Revoke an API key"""
        api_key = self.get_object()
        api_key.is_active = False
        api_key.save()
        return Response({'status': 'revoked'})
    
    @action(detail=True, methods=['post'])
    def regenerate(self, request, agency_pk=None, pk=None):
        """Regenerate API key secret"""
        api_key = self.get_object()
        new_secret = secrets.token_urlsafe(32)
        api_key.secret = make_password(new_secret)
        api_key.save()
        
        return Response({
            'key': api_key.key,
            'secret': new_secret  # Show once
        })


class AgencyBillingViewSet(viewsets.ModelViewSet):
    """ViewSet for agency billing"""
    serializer_class = AgencyBillingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        agency_id = self.kwargs.get('agency_pk')
        return AgencyBilling.objects.filter(agency_id=agency_id)


class AgencyInvoiceViewSet(viewsets.ModelViewSet):
    """ViewSet for agency invoices"""
    serializer_class = AgencyInvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        agency_id = self.kwargs.get('agency_pk')
        return AgencyInvoice.objects.filter(agency_id=agency_id)
    
    def perform_create(self, serializer):
        agency_id = self.kwargs.get('agency_pk')
        agency = get_object_or_404(Agency, id=agency_id)
        
        # Generate invoice number
        last_invoice = AgencyInvoice.objects.filter(agency=agency).order_by('-created_at').first()
        if last_invoice:
            last_num = int(last_invoice.invoice_number.split('-')[-1])
            invoice_number = f"INV-{last_num + 1:04d}"
        else:
            invoice_number = "INV-0001"
        
        serializer.save(agency=agency, invoice_number=invoice_number)
    
    @action(detail=True, methods=['post'])
    def send(self, request, agency_pk=None, pk=None):
        """Send invoice to client"""
        invoice = self.get_object()
        invoice.status = 'sent'
        invoice.save()
        
        # In production, send email
        return Response({'status': 'sent'})
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, agency_pk=None, pk=None):
        """Mark invoice as paid"""
        invoice = self.get_object()
        invoice.status = 'paid'
        invoice.paid_date = timezone.now().date()
        invoice.save()
        return Response({'status': 'paid'})


class BrandLibraryViewSet(viewsets.ModelViewSet):
    """ViewSet for brand libraries"""
    serializer_class = BrandLibrarySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        agency_id = self.kwargs.get('agency_pk')
        return BrandLibrary.objects.filter(agency_id=agency_id)
    
    def perform_create(self, serializer):
        agency_id = self.kwargs.get('agency_pk')
        agency = get_object_or_404(Agency, id=agency_id)
        serializer.save(agency=agency)


# Client Portal Public Access
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def client_portal_access(request, token):
    """Access client portal with token"""
    portal = get_object_or_404(ClientPortal, access_token=token, is_active=True)
    
    # Update access stats
    portal.last_accessed = timezone.now()
    portal.access_count += 1
    portal.save()
    
    # Get visible projects
    projects = portal.visible_projects.all()
    
    return Response({
        'client': ClientSerializer(portal.client).data,
        'welcome_message': portal.welcome_message,
        'projects': [{'id': str(p.id), 'name': p.name} for p in projects],
        'allow_comments': portal.allow_comments,
        'allow_approvals': portal.allow_approvals,
    })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def submit_client_feedback(request, token):
    """Submit feedback through client portal"""
    portal = get_object_or_404(ClientPortal, access_token=token, is_active=True)
    
    if not portal.allow_comments:
        return Response({'error': 'Comments disabled'}, status=status.HTTP_403_FORBIDDEN)
    
    feedback = ClientFeedback.objects.create(
        client=portal.client,
        project_id=request.data.get('project_id'),
        feedback_type=request.data.get('type', 'comment'),
        content=request.data.get('content'),
        position_x=request.data.get('position_x'),
        position_y=request.data.get('position_y'),
        page_number=request.data.get('page_number', 1),
    )
    
    return Response(ClientFeedbackSerializer(feedback).data)


# Need to import models for Q
from django.db import models
