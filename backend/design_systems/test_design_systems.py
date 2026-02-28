"""
Tests for design_systems models and views.
"""
import pytest
from django.contrib.auth.models import User
from rest_framework import status
from design_systems.models import (
    DesignSystem, DesignToken, ComponentDefinition,
    ComponentVariant, StyleGuide, DocumentationPage,
)


@pytest.fixture
def design_system(user):
    return DesignSystem.objects.create(
        user=user,
        name='My Design System',
        description='Comprehensive design system',
        version='1.0.0',
    )


@pytest.fixture
def design_token(design_system):
    return DesignToken.objects.create(
        design_system=design_system,
        name='primary-color',
        category='colors',
        token_type='color',
        value={'hex': '#3B82F6'},
        description='Primary brand color',
        group='brand',
    )


@pytest.fixture
def component_def(design_system):
    return ComponentDefinition.objects.create(
        design_system=design_system,
        name='Button',
        description='Primary action button',
        category='actions',
        status='approved',
    )


@pytest.mark.unit
class TestDesignSystem:
    """Tests for DesignSystem model."""

    def test_create_system(self, design_system):
        assert design_system.name == 'My Design System'
        assert design_system.version == '1.0.0'

    def test_system_str(self, design_system):
        assert 'My Design System' in str(design_system)

    def test_public_system(self, user):
        ds = DesignSystem.objects.create(
            user=user, name='Public System', is_public=True
        )
        assert ds.is_public is True

    def test_system_with_team(self, user):
        from teams.models import Team
        team = Team.objects.create(name='DS Team', slug='ds-team', owner=user)
        ds = DesignSystem.objects.create(
            user=user, name='Team System', team=team
        )
        assert ds.team == team


@pytest.mark.unit
class TestDesignToken:
    """Tests for DesignToken model."""

    def test_create_token(self, design_token):
        assert design_token.name == 'primary-color'
        assert design_token.token_type == 'color'

    def test_token_types(self, design_system):
        types = ['color', 'typography', 'spacing', 'sizing',
                 'border-radius', 'shadow', 'opacity']
        for t in types:
            token = DesignToken.objects.create(
                design_system=design_system,
                name=f'token-{t}', category='test',
                token_type=t, value={'v': '10px'},
            )
            assert token.token_type == t

    def test_token_reference(self, design_system, design_token):
        ref_token = DesignToken.objects.create(
            design_system=design_system,
            name='button-bg', category='components',
            token_type='color', value={},
            reference=design_token,
        )
        assert ref_token.reference == design_token

    def test_deprecated_token(self, design_system, design_token):
        new_token = DesignToken.objects.create(
            design_system=design_system,
            name='primary-v2', category='colors',
            token_type='color', value={'hex': '#2563EB'},
        )
        design_token.is_deprecated = True
        design_token.replacement = new_token
        design_token.save()
        design_token.refresh_from_db()
        assert design_token.is_deprecated is True
        assert design_token.replacement == new_token


@pytest.mark.unit
class TestComponentDefinition:
    """Tests for ComponentDefinition model."""

    def test_create_component(self, component_def):
        assert component_def.name == 'Button'
        assert component_def.status == 'approved'

    def test_component_statuses(self, design_system):
        for s in ['draft', 'review', 'approved', 'deprecated']:
            comp = ComponentDefinition.objects.create(
                design_system=design_system,
                name=f'{s} component', status=s,
            )
            assert comp.status == s

    def test_component_variant(self, component_def):
        variant = ComponentVariant.objects.create(
            component=component_def,
            name='Primary',
            description='Primary button variant',
            props={'variant': 'primary'},
            order=0,
        )
        assert variant.component == component_def
        assert variant.name == 'Primary'


@pytest.mark.unit
class TestStyleGuide:
    """Tests for StyleGuide model."""

    def test_create_style_guide(self, design_system):
        guide = StyleGuide.objects.create(
            design_system=design_system,
            brand_overview='Our brand represents innovation',
            brand_values=['Innovation', 'Simplicity', 'Trust'],
            tone_of_voice='Professional yet approachable',
        )
        assert guide.brand_overview is not None
        assert 'Innovation' in guide.brand_values


@pytest.mark.unit
class TestDocumentationPage:
    """Tests for DocumentationPage model."""

    def test_create_doc_page(self, design_system):
        page = DocumentationPage.objects.create(
            design_system=design_system,
            title='Getting Started',
            slug='getting-started',
            content='# Getting Started\n\nWelcome!',
            is_published=True,
        )
        assert page.title == 'Getting Started'

    def test_nested_pages(self, design_system):
        parent = DocumentationPage.objects.create(
            design_system=design_system,
            title='Components', slug='components',
        )
        child = DocumentationPage.objects.create(
            design_system=design_system,
            title='Buttons', slug='buttons',
            parent=parent, order=0,
        )
        assert child.parent == parent


@pytest.mark.api
class TestDesignSystemAPI:
    """Tests for DesignSystem API endpoints."""

    def test_list_systems(self, auth_client, design_system):
        response = auth_client.get('/api/v1/design-systems/systems/')
        assert response.status_code == status.HTTP_200_OK

    def test_create_system(self, auth_client, user):
        payload = {
            'name': 'New System',
            'description': 'Created via API',
            'version': '1.0.0',
        }
        response = auth_client.post(
            '/api/v1/design-systems/systems/', payload
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_retrieve_system(self, auth_client, design_system):
        response = auth_client.get(
            f'/api/v1/design-systems/systems/{design_system.id}/'
        )
        assert response.status_code == status.HTTP_200_OK

    def test_update_system(self, auth_client, design_system):
        payload = {'name': 'Updated System'}
        response = auth_client.patch(
            f'/api/v1/design-systems/systems/{design_system.id}/', payload
        )
        assert response.status_code == status.HTTP_200_OK

    def test_delete_system(self, auth_client, design_system):
        response = auth_client.delete(
            f'/api/v1/design-systems/systems/{design_system.id}/'
        )
        assert response.status_code in [200, 204]

    def test_duplicate_system(self, auth_client, design_system):
        response = auth_client.post(
            f'/api/v1/design-systems/systems/{design_system.id}/duplicate/'
        )
        assert response.status_code in [200, 201]

    def test_export_tokens_css(self, auth_client, design_system, design_token):
        response = auth_client.get(
            f'/api/v1/design-systems/systems/{design_system.id}/export_tokens/',
            {'format': 'css'}
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.api
class TestDesignTokenAPI:
    """Tests for DesignToken API within design systems."""

    def test_list_tokens(self, auth_client, design_system, design_token):
        response = auth_client.get(
            f'/api/v1/design-systems/systems/{design_system.id}/tokens/'
        )
        assert response.status_code == status.HTTP_200_OK

    def test_create_token(self, auth_client, design_system):
        payload = {
            'name': 'secondary-color',
            'category': 'colors',
            'token_type': 'color',
            'value': {'hex': '#10B981'},
        }
        response = auth_client.post(
            f'/api/v1/design-systems/systems/{design_system.id}/tokens/',
            payload, format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.api
class TestComponentDefinitionAPI:
    """Tests for ComponentDefinition API."""

    def test_list_components(self, auth_client, design_system, component_def):
        response = auth_client.get(
            f'/api/v1/design-systems/systems/{design_system.id}/components/'
        )
        assert response.status_code == status.HTTP_200_OK

    def test_create_component(self, auth_client, design_system):
        payload = {
            'name': 'Input Field',
            'description': 'Text input component',
            'category': 'forms',
        }
        response = auth_client.post(
            f'/api/v1/design-systems/systems/{design_system.id}/components/',
            payload,
        )
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.api
class TestTokenCategories:
    """Tests for token categories endpoint."""

    def test_get_categories(self, auth_client, db):
        response = auth_client.get('/api/v1/design-systems/token-categories/')
        assert response.status_code == status.HTTP_200_OK

    def test_design_system_unauthenticated(self, api_client, db):
        response = api_client.get('/api/v1/design-systems/systems/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
