"""
Component Variants & Properties System

Production-ready component variant system implementing Figma-like
component properties with multiple states, sizes, and styles.
"""
from django.db import models
from django.contrib.auth.models import User
import uuid


class ComponentSet(models.Model):
    """
    A set of related component variants. 
    This is the master component that contains all variants.
    Similar to Figma's Component Set.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='component_sets'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='component_sets'
    )
    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='component_sets'
    )
    
    # Basic info
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Icon/thumbnail for component library
    thumbnail = models.ImageField(upload_to='component_sets/', null=True, blank=True)
    icon = models.CharField(max_length=100, blank=True)  # Lucide icon name
    
    # Categorization
    category = models.CharField(max_length=100, blank=True)
    tags = models.JSONField(default=list)
    
    # Publishing status
    is_published = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    
    # Design system link
    design_system = models.ForeignKey(
        'design_systems.DesignSystem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='component_sets'
    )
    
    # Default variant
    default_variant = models.ForeignKey(
        'ComponentVariant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+'
    )
    
    # Usage tracking
    use_count = models.IntegerField(default=0)
    instance_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Component Set'
        verbose_name_plural = 'Component Sets'
    
    def __str__(self):
        return self.name
    
    def get_variant_count(self):
        """Calculate total number of variant combinations."""
        properties = self.properties.all()
        count = 1
        for prop in properties:
            if prop.property_type in ['variant', 'boolean']:
                count *= prop.options.count() or 2
        return count


class ComponentProperty(models.Model):
    """
    Defines a property that can vary across component variants.
    Examples: Size, State, Style, Theme
    """
    
    PROPERTY_TYPES = [
        ('variant', 'Variant'),       # Discrete options (size: sm, md, lg)
        ('boolean', 'Boolean'),        # True/False (disabled, loading)
        ('text', 'Text'),             # Editable text content
        ('instance_swap', 'Instance Swap'),  # Swappable nested component
        ('number', 'Number'),          # Numeric value (opacity, scale)
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    component_set = models.ForeignKey(
        ComponentSet,
        on_delete=models.CASCADE,
        related_name='properties'
    )
    
    # Property definition
    name = models.CharField(max_length=100)  # e.g., "Size", "State", "Style"
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    
    # Default value (stored as JSON for flexibility)
    default_value = models.JSONField(default=dict)
    
    # Description for documentation
    description = models.TextField(blank=True)
    
    # Order in the properties panel
    order = models.IntegerField(default=0)
    
    # Visibility
    is_hidden = models.BooleanField(default=False)
    
    # For number type
    min_value = models.FloatField(null=True, blank=True)
    max_value = models.FloatField(null=True, blank=True)
    step = models.FloatField(null=True, blank=True)
    
    # For text type
    placeholder = models.CharField(max_length=255, blank=True)
    max_length = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Component Property'
        verbose_name_plural = 'Component Properties'
        unique_together = ['component_set', 'name']
    
    def __str__(self):
        return f"{self.component_set.name}.{self.name}"


class PropertyOption(models.Model):
    """
    Options for variant-type properties.
    Example: For Size property: "Small", "Medium", "Large"
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(
        ComponentProperty,
        on_delete=models.CASCADE,
        related_name='options'
    )
    
    # Option value and display name
    value = models.CharField(max_length=100)  # Internal value: "sm", "md", "lg"
    label = models.CharField(max_length=100)  # Display name: "Small", "Medium"
    
    # Visual representation
    icon = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=50, blank=True)
    
    # Order
    order = models.IntegerField(default=0)
    
    # Is this the default option
    is_default = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Property Option'
        verbose_name_plural = 'Property Options'
    
    def __str__(self):
        return f"{self.property.name}: {self.label}"


class ComponentVariant(models.Model):
    """
    A specific variant of a component with particular property values.
    Example: Button with Size=Large, Style=Primary, State=Hover
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    component_set = models.ForeignKey(
        ComponentSet,
        on_delete=models.CASCADE,
        related_name='variants'
    )
    
    # Variant identification
    name = models.CharField(max_length=255)  # Auto-generated: "Size=Large, Style=Primary"
    
    # Property values for this variant (stores property_id -> value mapping)
    property_values = models.JSONField(default=dict)
    # Example: {"size": "lg", "style": "primary", "disabled": false}
    
    # The actual design data for this variant
    design_data = models.JSONField(default=dict)
    # Stores position, size, children, styles, etc.
    
    # Canvas position within the component set view
    position_x = models.FloatField(default=0)
    position_y = models.FloatField(default=0)
    width = models.FloatField(default=100)
    height = models.FloatField(default=100)
    
    # Preview
    thumbnail = models.ImageField(upload_to='variant_thumbnails/', null=True, blank=True)
    
    # Is this the base/master variant
    is_base = models.BooleanField(default=False)
    
    # For internal tracking
    variant_key = models.CharField(max_length=500, blank=True)  # Unique key from properties
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Component Variant'
        verbose_name_plural = 'Component Variants'
    
    def __str__(self):
        return f"{self.component_set.name} - {self.name}"
    
    def generate_name(self):
        """Generate variant name from property values."""
        parts = []
        for prop_name, value in self.property_values.items():
            parts.append(f"{prop_name}={value}")
        return ", ".join(parts) if parts else "Default"
    
    def generate_variant_key(self):
        """Generate unique key from sorted property values."""
        sorted_items = sorted(self.property_values.items())
        return "|".join(f"{k}:{v}" for k, v in sorted_items)
    
    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.generate_name()
        self.variant_key = self.generate_variant_key()
        super().save(*args, **kwargs)


class VariantOverride(models.Model):
    """
    Stores specific overrides for variant properties compared to base.
    Enables efficient storage by only storing differences.
    """
    
    OVERRIDE_TYPES = [
        ('style', 'Style Override'),
        ('layout', 'Layout Override'),
        ('content', 'Content Override'),
        ('visibility', 'Visibility Override'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    variant = models.ForeignKey(
        ComponentVariant,
        on_delete=models.CASCADE,
        related_name='overrides'
    )
    
    # Target element within the variant
    target_path = models.CharField(max_length=500)  # e.g., "root.label", "root.icon"
    
    # Override type
    override_type = models.CharField(max_length=20, choices=OVERRIDE_TYPES)
    
    # The overridden property and value
    property_name = models.CharField(max_length=100)
    original_value = models.JSONField(null=True, blank=True)
    override_value = models.JSONField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Variant Override'
        verbose_name_plural = 'Variant Overrides'
    
    def __str__(self):
        return f"{self.variant.name} - {self.target_path}.{self.property_name}"


class ComponentInstance(models.Model):
    """
    An instance of a component variant placed in a design.
    Tracks overrides and maintains link to the source component.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='component_instances'
    )
    component_set = models.ForeignKey(
        ComponentSet,
        on_delete=models.CASCADE,
        related_name='instances'
    )
    variant = models.ForeignKey(
        ComponentVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='instances'
    )
    design_component = models.OneToOneField(
        'projects.DesignComponent',
        on_delete=models.CASCADE,
        related_name='component_instance_config',
        null=True,
        blank=True
    )
    
    # Instance-specific property overrides
    property_overrides = models.JSONField(default=dict)
    
    # Instance-specific style overrides
    style_overrides = models.JSONField(default=dict)
    
    # Content overrides (text, images)
    content_overrides = models.JSONField(default=dict)
    
    # Position and size on canvas
    position_x = models.FloatField(default=0)
    position_y = models.FloatField(default=0)
    width = models.FloatField(null=True, blank=True)  # null = use component size
    height = models.FloatField(null=True, blank=True)
    rotation = models.FloatField(default=0)
    
    # Scaling
    scale_x = models.FloatField(default=1.0)
    scale_y = models.FloatField(default=1.0)
    
    # Visibility and locking
    visible = models.BooleanField(default=True)
    locked = models.BooleanField(default=False)
    
    # Detached from component (makes it independent)
    is_detached = models.BooleanField(default=False)
    
    # Sync status
    is_synced = models.BooleanField(default=True)
    last_synced = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Component Instance'
        verbose_name_plural = 'Component Instances'
    
    def __str__(self):
        variant_name = self.variant.name if self.variant else "Default"
        return f"{self.component_set.name} instance ({variant_name})"
    
    def get_effective_properties(self):
        """Get properties with instance overrides applied."""
        if not self.variant:
            return self.property_overrides
        
        props = self.variant.property_values.copy()
        props.update(self.property_overrides)
        return props
    
    def detach(self):
        """Detach this instance from its component, making it independent."""
        self.is_detached = True
        self.is_synced = False
        self.save(update_fields=['is_detached', 'is_synced'])
    
    def sync_with_component(self):
        """Sync this instance with the latest component changes."""
        if self.is_detached:
            return False
        
        from django.utils import timezone
        self.is_synced = True
        self.last_synced = timezone.now()
        self.save(update_fields=['is_synced', 'last_synced'])
        return True


class InteractiveState(models.Model):
    """
    Defines interactive states for components (hover, pressed, focus, etc.)
    """
    
    STATE_TYPES = [
        ('default', 'Default'),
        ('hover', 'Hover'),
        ('pressed', 'Pressed'),
        ('focus', 'Focus'),
        ('focus_visible', 'Focus Visible'),
        ('active', 'Active'),
        ('disabled', 'Disabled'),
        ('loading', 'Loading'),
        ('error', 'Error'),
        ('success', 'Success'),
        ('selected', 'Selected'),
        ('checked', 'Checked'),
        ('indeterminate', 'Indeterminate'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    variant = models.ForeignKey(
        ComponentVariant,
        on_delete=models.CASCADE,
        related_name='interactive_states'
    )
    
    # State definition
    state_type = models.CharField(max_length=20, choices=STATE_TYPES)
    name = models.CharField(max_length=100)
    
    # State trigger
    trigger = models.CharField(max_length=50, default='hover')  # CSS pseudo-class
    
    # Style changes for this state
    style_changes = models.JSONField(default=dict)
    # Example: {"backgroundColor": "#0066cc", "transform": "scale(1.02)"}
    
    # Transition settings
    transition_duration = models.IntegerField(default=150)  # ms
    transition_easing = models.CharField(max_length=50, default='ease-out')
    transition_properties = models.JSONField(default=list)
    # Example: ["background-color", "transform", "box-shadow"]
    
    # Order (for chained states)
    order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Interactive State'
        verbose_name_plural = 'Interactive States'
        unique_together = ['variant', 'state_type']
    
    def __str__(self):
        return f"{self.variant.name} - {self.get_state_type_display()}"


class ComponentSlot(models.Model):
    """
    Defines slots within a component that can accept child components.
    Similar to Vue/Web Components slots.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    component_set = models.ForeignKey(
        ComponentSet,
        on_delete=models.CASCADE,
        related_name='slots'
    )
    
    # Slot identification
    name = models.CharField(max_length=100)  # e.g., "icon", "content", "footer"
    
    # Description
    description = models.TextField(blank=True)
    
    # Allowed component types
    allowed_types = models.JSONField(default=list)
    # Example: ["Icon", "Badge", "Avatar"]
    
    # Default content
    default_content = models.JSONField(null=True, blank=True)
    
    # Constraints
    min_items = models.IntegerField(default=0)
    max_items = models.IntegerField(null=True, blank=True)
    
    # Is this slot required
    required = models.BooleanField(default=False)
    
    # Order in the component
    order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Component Slot'
        verbose_name_plural = 'Component Slots'
        unique_together = ['component_set', 'name']
    
    def __str__(self):
        return f"{self.component_set.name} - {self.name} slot"
