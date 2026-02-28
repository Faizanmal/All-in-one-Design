"""
Tests for templates models.
"""
import pytest
from django.contrib.auth.models import User
from templates.models import Template, TemplateComponent


@pytest.mark.unit
class TestTemplateModel:
    """Tests for Template model."""

    def test_create_template(self, user):
        template = Template.objects.create(
            name='Social Media Post',
            description='Instagram post template',
            category='social_media',
            design_data={'layers': [{'type': 'text', 'content': 'Hello'}]},
            width=1080,
            height=1080,
            created_by=user,
        )
        assert template.name == 'Social Media Post'
        assert template.category == 'social_media'

    def test_template_categories(self, user):
        categories = [
            'social_media', 'presentation', 'poster', 'flyer',
            'ui_kit', 'mobile_app', 'web_design', 'logo',
            'business_card', 'infographic',
        ]
        for cat in categories:
            t = Template.objects.create(
                name=f'{cat} template', category=cat, created_by=user,
            )
            assert t.category == cat

    def test_template_premium(self, user):
        template = Template.objects.create(
            name='Premium', category='poster', is_premium=True, created_by=user
        )
        assert template.is_premium is True

    def test_template_public(self, user):
        template = Template.objects.create(
            name='Public', category='poster', is_public=True, created_by=user
        )
        assert template.is_public is True

    def test_template_ai_generated(self, user):
        template = Template.objects.create(
            name='AI Generated', category='logo',
            ai_generated=True, ai_prompt='Create a modern logo',
            created_by=user,
        )
        assert template.ai_generated is True

    def test_template_use_count(self, user):
        template = Template.objects.create(
            name='Popular', category='poster', use_count=100, created_by=user
        )
        assert template.use_count == 100

    def test_template_tags(self, user):
        template = Template.objects.create(
            name='Tagged', category='poster',
            tags=['design', 'modern', 'minimal'],
            created_by=user,
        )
        assert 'design' in template.tags

    def test_template_color_palette(self, user):
        template = Template.objects.create(
            name='Colorful', category='poster',
            color_palette=['#FF0000', '#00FF00', '#0000FF'],
            created_by=user,
        )
        assert len(template.color_palette) == 3


@pytest.mark.unit
class TestTemplateComponent:
    """Tests for TemplateComponent model."""

    def test_create_component(self, db):
        component = TemplateComponent.objects.create(
            name='Hero Section',
            component_type='hero',
            design_data={'layout': 'centered'},
            is_public=True,
        )
        assert component.name == 'Hero Section'
        assert component.is_public is True

    def test_component_types(self, db):
        types = ['header', 'footer', 'sidebar', 'card', 'button',
                 'form', 'navigation', 'hero']
        for ct in types:
            comp = TemplateComponent.objects.create(
                name=f'{ct} component', component_type=ct
            )
            assert comp.component_type == ct
