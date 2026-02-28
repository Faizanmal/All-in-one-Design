"""
Tests for assets models and views.
"""
import pytest
from django.contrib.auth.models import User
from rest_framework import status
from assets.models import (
    Asset, ColorPalette, FontFamily, AssetVersion,
    AssetComment, AssetCollection
)
from projects.models import Project


@pytest.fixture
def project(user):
    return Project.objects.create(user=user, name='Asset Test')


@pytest.fixture
def asset(user, project):
    return Asset.objects.create(
        user=user,
        project=project,
        name='test-image.png',
        asset_type='image',
        file_url='https://example.com/test.png',
        file_size=1024,
        mime_type='image/png',
        width=800,
        height=600,
    )


@pytest.fixture
def color_palette(user):
    return ColorPalette.objects.create(
        name='Ocean',
        colors=['#1E3A5F', '#5B8DB8', '#B0D4E8'],
        description='Ocean-inspired palette',
        is_public=True,
        created_by=user,
    )


@pytest.fixture
def font(db):
    return FontFamily.objects.create(
        name='Inter',
        font_family='Inter',
        category='sans-serif',
        is_google_font=True,
    )


@pytest.mark.unit
class TestAssetModel:
    """Tests for Asset model."""

    def test_create_asset(self, asset):
        assert asset.name == 'test-image.png'
        assert asset.asset_type == 'image'

    def test_asset_types(self, user):
        for at in ['image', 'icon', 'font', 'video', 'audio', 'svg']:
            a = Asset.objects.create(
                user=user, name=f'test.{at}', asset_type=at,
                file_url=f'https://example.com/test.{at}',
            )
            assert a.asset_type == at

    def test_ai_generated_asset(self, user):
        asset = Asset.objects.create(
            user=user, name='ai-gen.png', asset_type='image',
            file_url='https://example.com/ai.png',
            ai_generated=True, ai_prompt='Generate a logo',
        )
        assert asset.ai_generated is True

    def test_asset_tags(self, user):
        asset = Asset.objects.create(
            user=user, name='tagged.png', asset_type='image',
            file_url='https://example.com/tag.png',
            tags=['logo', 'brand', 'minimal'],
        )
        assert 'logo' in asset.tags


@pytest.mark.unit
class TestColorPalette:
    """Tests for ColorPalette model."""

    def test_create_palette(self, color_palette):
        assert color_palette.name == 'Ocean'
        assert len(color_palette.colors) == 3

    def test_public_palette(self, color_palette):
        assert color_palette.is_public is True

    def test_ai_generated_palette(self, user):
        palette = ColorPalette.objects.create(
            name='AI Colors', colors=['#FF0000'],
            ai_generated=True, created_by=user,
        )
        assert palette.ai_generated is True


@pytest.mark.unit
class TestFontFamily:
    """Tests for FontFamily model."""

    def test_create_font(self, font):
        assert font.name == 'Inter'
        assert font.is_google_font is True

    def test_font_categories(self, db):
        for cat in ['serif', 'sans-serif', 'monospace', 'display', 'handwriting']:
            f = FontFamily.objects.create(
                name=f'Font {cat}', font_family=f'Font{cat}',
                category=cat,
            )
            assert f.category == cat


@pytest.mark.unit
class TestAssetVersion:
    """Tests for AssetVersion model."""

    def test_create_version(self, asset, user):
        version = AssetVersion.objects.create(
            asset=asset, version_number=2,
            file_url='https://example.com/v2.png',
            file_size=2048, change_description='Updated',
            created_by=user,
        )
        assert version.version_number == 2


@pytest.mark.unit
class TestAssetCollection:
    """Tests for AssetCollection model."""

    def test_create_collection(self, user, asset):
        collection = AssetCollection.objects.create(
            name='Brand Assets', user=user, is_public=False,
        )
        collection.assets.add(asset)
        assert collection.assets.count() == 1

    def test_nested_collections(self, user):
        parent = AssetCollection.objects.create(name='Parent', user=user)
        child = AssetCollection.objects.create(
            name='Child', user=user, parent_collection=parent
        )
        assert child.parent_collection == parent


@pytest.mark.api
class TestAssetViewSet:
    """Tests for Asset API."""

    def test_list_assets(self, auth_client, asset):
        response = auth_client.get('/api/v1/assets/')
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_asset(self, auth_client, asset):
        response = auth_client.get(f'/api/v1/assets/{asset.id}/')
        assert response.status_code in [200, 301]

    def test_delete_asset(self, auth_client, asset):
        response = auth_client.delete(f'/api/v1/assets/{asset.id}/delete/')
        assert response.status_code in [200, 204, 301]

    def test_assets_unauthenticated(self, api_client, db):
        response = api_client.get('/api/v1/assets/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.api
class TestColorPaletteViewSet:
    """Tests for ColorPalette API."""

    def test_list_palettes(self, auth_client, color_palette):
        response = auth_client.get('/api/v1/assets/palettes/')
        assert response.status_code == status.HTTP_200_OK

    def test_create_palette(self, auth_client, user):
        payload = {
            'name': 'Sunset',
            'colors': ['#FF6B6B', '#FFA07A', '#FFD700'],
            'description': 'Warm colors',
        }
        response = auth_client.post(
            '/api/v1/assets/palettes/', payload, format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.api
class TestFontFamilyViewSet:
    """Tests for FontFamily API."""

    def test_list_fonts(self, auth_client, font):
        response = auth_client.get('/api/v1/assets/fonts/')
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_font(self, auth_client, font):
        response = auth_client.get(f'/api/v1/assets/fonts/{font.id}/')
        assert response.status_code == status.HTTP_200_OK
