"""
Comprehensive tests for the Assets app.
Tests asset CRUD, upload, color palettes, fonts.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Asset, ColorPalette, FontFamily


class AssetModelTests(TestCase):
    """Test Asset model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='TestPass123!'
        )

    def test_create_asset(self):
        asset = Asset.objects.create(
            user=self.user,
            name='test-image.png',
            asset_type='image',
            file_url='https://cdn.example.com/test.png',
            file_size=102400,
            mime_type='image/png',
            width=800,
            height=600,
        )
        self.assertEqual(asset.name, 'test-image.png')
        self.assertEqual(asset.asset_type, 'image')
        self.assertEqual(asset.file_size, 102400)

    def test_asset_defaults(self):
        asset = Asset.objects.create(
            user=self.user,
            name='icon.svg',
            asset_type='svg',
            file_url='https://cdn.example.com/icon.svg',
            file_size=2048,
            mime_type='image/svg+xml',
        )
        self.assertFalse(asset.ai_generated)
        self.assertEqual(asset.tags, [])
        self.assertEqual(asset.ai_prompt, '')
        self.assertIsNone(asset.width)

    def test_asset_with_tags(self):
        asset = Asset.objects.create(
            user=self.user,
            name='tagged.png',
            asset_type='image',
            file_url='https://cdn.example.com/tagged.png',
            file_size=5120,
            mime_type='image/png',
            tags=['logo', 'brand', 'header'],
        )
        self.assertEqual(len(asset.tags), 3)
        self.assertIn('logo', asset.tags)

    def test_ai_generated_asset(self):
        asset = Asset.objects.create(
            user=self.user,
            name='ai-generated.png',
            asset_type='image',
            file_url='https://cdn.example.com/ai.png',
            file_size=51200,
            mime_type='image/png',
            ai_generated=True,
            ai_prompt='Generate a modern abstract background',
        )
        self.assertTrue(asset.ai_generated)
        self.assertIn('abstract', asset.ai_prompt)

    def test_asset_ordering(self):
        Asset.objects.create(
            user=self.user, name='first.png', asset_type='image',
            file_url='https://cdn.example.com/1.png', file_size=100, mime_type='image/png'
        )
        Asset.objects.create(
            user=self.user, name='second.png', asset_type='image',
            file_url='https://cdn.example.com/2.png', file_size=100, mime_type='image/png'
        )
        assets = list(Asset.objects.all())
        self.assertEqual(assets[0].name, 'second.png')  # -created_at ordering

    def test_asset_str(self):
        asset = Asset.objects.create(
            user=self.user, name='test.png', asset_type='image',
            file_url='https://cdn.example.com/t.png', file_size=100, mime_type='image/png'
        )
        self.assertEqual(str(asset), 'test.png (image)')


class ColorPaletteModelTests(TestCase):
    """Test ColorPalette model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='TestPass123!'
        )

    def test_create_palette(self):
        palette = ColorPalette.objects.create(
            name='Sunset Vibes',
            colors=['#FF6B35', '#F7C59F', '#EFEFD0', '#004E89', '#1A659E'],
            created_by=self.user,
        )
        self.assertEqual(palette.name, 'Sunset Vibes')
        self.assertEqual(len(palette.colors), 5)

    def test_ai_generated_palette(self):
        palette = ColorPalette.objects.create(
            name='AI Palette',
            colors=['#FF0000', '#00FF00'],
            ai_generated=True,
            ai_prompt='Warm autumn colors',
            created_by=self.user,
        )
        self.assertTrue(palette.ai_generated)

    def test_palette_use_count(self):
        palette = ColorPalette.objects.create(
            name='Popular', colors=['#000', '#FFF'], created_by=self.user,
        )
        self.assertEqual(palette.use_count, 0)
        palette.use_count = 42
        palette.save()
        palette.refresh_from_db()
        self.assertEqual(palette.use_count, 42)


class FontFamilyModelTests(TestCase):
    """Test FontFamily model."""

    def test_create_font(self):
        font = FontFamily.objects.create(
            name='Roboto',
            font_family='Roboto, sans-serif',
            category='sans-serif',
            is_google_font=True,
        )
        self.assertEqual(font.name, 'Roboto')
        self.assertTrue(font.is_google_font)
        self.assertFalse(font.is_premium)


class AssetAPITests(APITestCase):
    """Test Asset API endpoints."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='TestPass123!'
        )
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_list_assets(self):
        Asset.objects.create(
            user=self.user, name='test.png', asset_type='image',
            file_url='https://cdn.example.com/t.png', file_size=100, mime_type='image/png'
        )
        response = self.client.get('/api/v1/assets/assets/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_palettes(self):
        response = self.client.get('/api/v1/assets/palettes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_fonts(self):
        response = self.client.get('/api/v1/assets/fonts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized_access(self):
        self.client.credentials()
        response = self.client.get('/api/v1/assets/assets/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
