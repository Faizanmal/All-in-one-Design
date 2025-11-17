from django.db import models
from django.contrib.auth.models import User


class AIGenerationRequest(models.Model):
    """Track AI generation requests for analytics and debugging"""
    REQUEST_TYPES = (
        ('layout', 'Layout Generation'),
        ('logo', 'Logo Generation'),
        ('color_palette', 'Color Palette'),
        ('text_content', 'Text Content'),
        ('image', 'Image Generation'),
        ('refinement', 'Design Refinement'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_requests')
    request_type = models.CharField(max_length=30, choices=REQUEST_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Input
    prompt = models.TextField()
    parameters = models.JSONField(default=dict)  # Additional parameters like style, colors, etc.
    
    # Output
    result = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # AI model info
    model_used = models.CharField(max_length=100, blank=True)  # e.g., 'gpt-4', 'dall-e-3'
    tokens_used = models.IntegerField(null=True, blank=True)
    
    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.request_type} - {self.status} ({self.user.username})"


class AIPromptTemplate(models.Model):
    """Pre-defined prompt templates for consistent AI generation"""
    TEMPLATE_TYPES = (
        ('layout', 'Layout Generation'),
        ('logo', 'Logo Generation'),
        ('refinement', 'Design Refinement'),
        ('content', 'Content Generation'),
    )
    
    name = models.CharField(max_length=255)
    template_type = models.CharField(max_length=30, choices=TEMPLATE_TYPES)
    
    # Prompt template with placeholders
    prompt_template = models.TextField()
    # Example: "Generate a {style} {design_type} design for {industry} with colors {colors}"
    
    # Default parameters
    default_parameters = models.JSONField(default=dict)
    
    # Metadata
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.template_type})"


class ChatConversation(models.Model):
    """Store chat conversations with AI assistant"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_conversations')
    title = models.CharField(max_length=255, default="New Conversation")
    
    # Context
    context_data = models.JSONField(default=dict, blank=True, help_text="Project or design context")
    
    # Settings
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


class ChatMessage(models.Model):
    """Individual messages in chat conversations"""
    SENDER_TYPES = (
        ('user', 'User'),
        ('assistant', 'AI Assistant'),
        ('system', 'System'),
    )
    
    conversation = models.ForeignKey(ChatConversation, on_delete=models.CASCADE, related_name='messages')
    sender_type = models.CharField(max_length=20, choices=SENDER_TYPES)
    message = models.TextField()
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True, help_text="Attachments, references, etc.")
    tokens_used = models.IntegerField(null=True, blank=True)
    model_used = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender_type}: {self.message[:50]}..."


class AIFeedback(models.Model):
    """User feedback on AI generations for improvement"""
    RATING_CHOICES = [
        (1, 'Poor'),
        (2, 'Fair'),
        (3, 'Good'),
        (4, 'Very Good'),
        (5, 'Excellent'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_feedback')
    ai_request = models.ForeignKey(AIGenerationRequest, on_delete=models.CASCADE, related_name='feedback', null=True, blank=True)
    chat_message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='feedback', null=True, blank=True)
    
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - Rating: {self.rating}"

