"""
Data Binding Models

Connect designs to external data sources: CSV, JSON, APIs, databases.
"""

from django.db import models
from django.conf import settings
import uuid


class DataSource(models.Model):
    """External data source connection."""
    
    SOURCE_TYPES = [
        ('csv', 'CSV File'),
        ('json', 'JSON File'),
        ('rest_api', 'REST API'),
        ('graphql', 'GraphQL API'),
        ('database', 'Database'),
        ('google_sheets', 'Google Sheets'),
        ('airtable', 'Airtable'),
        ('firebase', 'Firebase'),
        ('supabase', 'Supabase'),
        ('notion', 'Notion'),
    ]
    
    AUTH_TYPES = [
        ('none', 'No Authentication'),
        ('api_key', 'API Key'),
        ('bearer', 'Bearer Token'),
        ('basic', 'Basic Auth'),
        ('oauth2', 'OAuth 2.0'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='data_sources')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='data_sources', null=True, blank=True)
    
    name = models.CharField(max_length=255)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    
    # Connection details
    url = models.URLField(blank=True)
    file = models.FileField(upload_to='data_sources/', null=True, blank=True)
    
    # Authentication
    auth_type = models.CharField(max_length=20, choices=AUTH_TYPES, default='none')
    auth_config = models.JSONField(default=dict, blank=True)  # Encrypted in production
    
    # API configuration
    method = models.CharField(max_length=10, default='GET')
    headers = models.JSONField(default=dict, blank=True)
    query_params = models.JSONField(default=dict, blank=True)
    body_template = models.TextField(blank=True)
    
    # Response parsing
    data_path = models.CharField(max_length=255, blank=True, help_text='JSONPath to data array')
    
    # Schema
    schema = models.JSONField(default=dict, blank=True)
    
    # Caching
    cache_duration = models.IntegerField(default=300, help_text='Cache duration in seconds')
    last_fetched = models.DateTimeField(null=True, blank=True)
    cached_data = models.JSONField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_error = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.source_type})"


class DataVariable(models.Model):
    """Variable bound to data source field."""
    
    VARIABLE_TYPES = [
        ('string', 'Text'),
        ('number', 'Number'),
        ('boolean', 'Boolean'),
        ('date', 'Date'),
        ('datetime', 'DateTime'),
        ('image', 'Image URL'),
        ('url', 'URL'),
        ('color', 'Color'),
        ('json', 'JSON Object'),
        ('array', 'Array'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='data_variables')
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, related_name='variables', null=True, blank=True)
    
    name = models.CharField(max_length=100)
    variable_type = models.CharField(max_length=20, choices=VARIABLE_TYPES, default='string')
    
    # Binding
    field_path = models.CharField(max_length=255, blank=True, help_text='Path to field in data source')
    
    # Default value
    default_value = models.TextField(blank=True)
    
    # Transformation
    transform = models.TextField(blank=True, help_text='JavaScript transform function')
    format_string = models.CharField(max_length=255, blank=True)
    
    # Current value (for preview)
    current_value = models.TextField(blank=True)
    
    # Metadata
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        unique_together = ['project', 'name']
    
    def __str__(self):
        return self.name


class DataBinding(models.Model):
    """Binding between element property and data variable."""
    
    BINDING_TYPES = [
        ('text', 'Text Content'),
        ('src', 'Image Source'),
        ('href', 'Link URL'),
        ('fill', 'Fill Color'),
        ('stroke', 'Stroke Color'),
        ('opacity', 'Opacity'),
        ('visibility', 'Visibility'),
        ('width', 'Width'),
        ('height', 'Height'),
        ('style', 'CSS Style'),
        ('class', 'CSS Class'),
        ('data', 'Data Attribute'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='data_bindings')
    variable = models.ForeignKey(DataVariable, on_delete=models.CASCADE, related_name='bindings')
    
    # Element identification
    element_id = models.CharField(max_length=100)
    element_name = models.CharField(max_length=255, blank=True)
    
    # Binding
    binding_type = models.CharField(max_length=20, choices=BINDING_TYPES)
    property_name = models.CharField(max_length=100, blank=True)  # For data-* or custom props
    
    # Conditional binding
    condition = models.TextField(blank=True, help_text='JavaScript condition')
    true_value = models.TextField(blank=True)
    false_value = models.TextField(blank=True)
    
    # Template string (for complex bindings)
    template = models.TextField(blank=True, help_text='Template with {{variable}} placeholders')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['element_id', 'binding_type']


class DataCollection(models.Model):
    """Collection of data for list/repeating elements."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='data_collections')
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, related_name='collections')
    
    name = models.CharField(max_length=255)
    
    # Filtering
    filter_expression = models.TextField(blank=True)
    
    # Sorting
    sort_field = models.CharField(max_length=100, blank=True)
    sort_direction = models.CharField(max_length=4, choices=[('asc', 'Ascending'), ('desc', 'Descending')], default='asc')
    
    # Pagination
    page_size = models.IntegerField(default=10)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']


class RepeatingElement(models.Model):
    """Element that repeats for each item in a collection."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='repeating_elements')
    collection = models.ForeignKey(DataCollection, on_delete=models.CASCADE, related_name='repeating_elements')
    
    # Element reference
    element_id = models.CharField(max_length=100)
    template_element = models.TextField(help_text='JSON template of the element')
    
    # Layout
    direction = models.CharField(max_length=10, choices=[('horizontal', 'Horizontal'), ('vertical', 'Vertical'), ('grid', 'Grid')], default='vertical')
    gap = models.FloatField(default=10)
    columns = models.IntegerField(default=1)
    
    # Alternating styles
    alternate_styles = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)


class DataTransform(models.Model):
    """Reusable data transformation."""
    
    TRANSFORM_TYPES = [
        ('format_date', 'Format Date'),
        ('format_number', 'Format Number'),
        ('format_currency', 'Format Currency'),
        ('truncate', 'Truncate Text'),
        ('uppercase', 'Uppercase'),
        ('lowercase', 'Lowercase'),
        ('capitalize', 'Capitalize'),
        ('replace', 'Find & Replace'),
        ('custom', 'Custom JavaScript'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='data_transforms')
    
    name = models.CharField(max_length=100)
    transform_type = models.CharField(max_length=20, choices=TRANSFORM_TYPES)
    
    # Configuration
    config = models.JSONField(default=dict)
    # Examples:
    # format_date: {"format": "MMM DD, YYYY"}
    # format_number: {"decimals": 2, "thousands_separator": ","}
    # format_currency: {"currency": "USD", "locale": "en-US"}
    # truncate: {"max_length": 100, "suffix": "..."}
    # replace: {"find": "old", "replace": "new"}
    # custom: {"code": "return value.toUpperCase()"}
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']


class DataSyncLog(models.Model):
    """Log of data synchronization."""
    
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('partial', 'Partial'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, related_name='sync_logs')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    records_fetched = models.IntegerField(default=0)
    duration_ms = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
