"""
Data Binding Views
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
import time

from .models import (
    DataSource, DataVariable, DataBinding, DataCollection,
    RepeatingElement, DataTransform, DataSyncLog
)
from .serializers import (
    DataSourceSerializer, DataSourceListSerializer,
    DataVariableSerializer, DataBindingSerializer,
    DataCollectionSerializer, RepeatingElementSerializer,
    DataTransformSerializer, DataSyncLogSerializer,
    TestConnectionSerializer,
    BindElementsRequestSerializer, TransformPreviewSerializer
)
from .services import DataFetcher, DataTransformer, SchemaInferrer


class DataSourceViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DataSource.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DataSourceListSerializer
        return DataSourceSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def fetch(self, request, pk=None):
        """Fetch data from source."""
        data_source = self.get_object()
        
        start_time = time.time()
        
        try:
            result = DataFetcher.fetch(data_source)
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Cache data
            data_source.cached_data = result
            data_source.last_fetched = timezone.now()
            data_source.last_error = ''
            data_source.save()
            
            # Infer schema
            if result.get('data'):
                data_source.schema = SchemaInferrer.infer_schema(result['data'])
                data_source.save()
            
            # Log sync
            DataSyncLog.objects.create(
                data_source=data_source,
                status='success',
                records_fetched=result.get('count', 0),
                duration_ms=duration_ms
            )
            
            return Response(result)
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            
            data_source.last_error = str(e)
            data_source.save()
            
            DataSyncLog.objects.create(
                data_source=data_source,
                status='failed',
                duration_ms=duration_ms,
                error_message=str(e)
            )
            
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def schema(self, request, pk=None):
        """Get inferred schema."""
        data_source = self.get_object()
        return Response(data_source.schema)
    
    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """Preview cached data."""
        data_source = self.get_object()
        limit = int(request.query_params.get('limit', 10))
        
        if not data_source.cached_data:
            return Response({'error': 'No cached data. Fetch first.'}, status=status.HTTP_404_NOT_FOUND)
        
        data = data_source.cached_data.get('data', [])[:limit]
        return Response({
            'data': data,
            'total_count': data_source.cached_data.get('count', 0),
            'last_fetched': data_source.last_fetched
        })
    
    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """Get sync logs."""
        data_source = self.get_object()
        logs = data_source.sync_logs.all()[:20]
        return Response(DataSyncLogSerializer(logs, many=True).data)


class TestConnectionView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Test connection to data source."""
        serializer = TestConnectionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Create temporary data source for testing
        from .models import DataSource
        temp_source = DataSource(
            source_type=data['source_type'],
            url=data.get('url', ''),
            auth_type=data['auth_type'],
            auth_config=data['auth_config'],
            headers=data['headers'],
            method=data['method']
        )
        
        try:
            result = DataFetcher.fetch(temp_source)
            return Response({
                'success': True,
                'record_count': result.get('count', 0),
                'sample': result.get('data', [])[:3]
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class DataVariableViewSet(viewsets.ModelViewSet):
    serializer_class = DataVariableSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = DataVariable.objects.filter(project__user=self.request.user)
        
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def refresh(self, request, pk=None):
        """Refresh variable value from data source."""
        variable = self.get_object()
        
        if not variable.data_source:
            return Response({'error': 'No data source configured'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get current data
        cached = variable.data_source.cached_data
        if not cached:
            return Response({'error': 'Data source not fetched'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get value
        data = cached.get('data', [])
        if data and variable.field_path:
            value = data[0].get(variable.field_path.split('.')[0], '')
            variable.current_value = str(value)
            variable.save()
        
        return Response(DataVariableSerializer(variable).data)


class DataBindingViewSet(viewsets.ModelViewSet):
    serializer_class = DataBindingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = DataBinding.objects.filter(project__user=self.request.user)
        
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        element_id = self.request.query_params.get('element')
        if element_id:
            queryset = queryset.filter(element_id=element_id)
        
        return queryset


class DataCollectionViewSet(viewsets.ModelViewSet):
    serializer_class = DataCollectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DataCollection.objects.filter(project__user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """Get filtered and sorted collection data."""
        collection = self.get_object()
        
        if not collection.data_source.cached_data:
            return Response({'error': 'Data source not fetched'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = collection.data_source.cached_data.get('data', [])
        
        # Apply sorting
        if collection.sort_field:
            reverse = collection.sort_direction == 'desc'
            data = sorted(data, key=lambda x: x.get(collection.sort_field, ''), reverse=reverse)
        
        # Apply pagination
        page = int(request.query_params.get('page', 1))
        start = (page - 1) * collection.page_size
        end = start + collection.page_size
        
        return Response({
            'data': data[start:end],
            'total': len(data),
            'page': page,
            'page_size': collection.page_size
        })


class RepeatingElementViewSet(viewsets.ModelViewSet):
    serializer_class = RepeatingElementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return RepeatingElement.objects.filter(project__user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def render(self, request, pk=None):
        """Render repeating elements with data."""
        element = self.get_object()
        collection = element.collection
        
        if not collection.data_source.cached_data:
            return Response({'error': 'Data source not fetched'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = collection.data_source.cached_data.get('data', [])
        
        rendered = []
        for i, item in enumerate(data[:collection.page_size]):
            rendered.append({
                'index': i,
                'data': item,
                'position': {
                    'x': 0 if element.direction == 'vertical' else i * (100 + element.gap),
                    'y': i * (100 + element.gap) if element.direction == 'vertical' else 0
                }
            })
        
        return Response({'elements': rendered})


class DataTransformViewSet(viewsets.ModelViewSet):
    serializer_class = DataTransformSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DataTransform.objects.filter(user=self.request.user)


class TransformPreviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Preview transformation result."""
        serializer = TransformPreviewSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        result = DataTransformer.transform(
            data['value'],
            data['transform_type'],
            data['config']
        )
        
        return Response({'result': result})


class BindElementsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Bind multiple elements at once."""
        serializer = BindElementsRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        created = []
        
        for binding_data in data['bindings']:
            binding = DataBinding.objects.create(
                project_id=data['project_id'],
                variable_id=binding_data['variable_id'],
                element_id=binding_data['element_id'],
                element_name=binding_data.get('element_name', ''),
                binding_type=binding_data['binding_type'],
                property_name=binding_data.get('property_name', ''),
                template=binding_data.get('template', '')
            )
            created.append(binding)
        
        return Response(
            DataBindingSerializer(created, many=True).data,
            status=status.HTTP_201_CREATED
        )
