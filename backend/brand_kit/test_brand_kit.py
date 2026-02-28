"""
Tests for brand_kit models and views.
"""
import pytest
from django.contrib.auth.models import User
from rest_framework import status
from brand_kit.models import BrandKitEnforcement, BrandViolationLog
from design_systems.models import DesignSystem


@pytest.fixture
def design_system(user):
    return DesignSystem.objects.create(
        user=user,
        name='Brand System',
        description='Test brand design system',
    )


@pytest.fixture
def enforcement(design_system):
    return BrandKitEnforcement.objects.create(
        design_system=design_system,
        lock_color_picker=True,
        force_ai_variants=False,
        lock_typography=True,
        require_approval=False,
        log_violations=True,
    )


@pytest.mark.unit
class TestBrandKitEnforcement:
    """Tests for BrandKitEnforcement model."""

    def test_create_enforcement(self, enforcement):
        assert enforcement.lock_color_picker is True
        assert enforcement.lock_typography is True
        assert enforcement.log_violations is True

    def test_enforcement_defaults(self, design_system):
        e = BrandKitEnforcement.objects.create(design_system=design_system)
        assert e is not None

    def test_one_to_one_constraint(self, design_system, enforcement):
        with pytest.raises(Exception):
            BrandKitEnforcement.objects.create(design_system=design_system)


@pytest.mark.unit
class TestBrandViolationLog:
    """Tests for BrandViolationLog model."""

    def test_create_violation(self, enforcement, user):
        log = BrandViolationLog.objects.create(
            enforcement=enforcement,
            user=user,
            event_type='invalid_hex',
            details={'color': '#GGGGGG', 'element': 'header'},
        )
        assert log.event_type == 'invalid_hex'

    def test_violation_types(self, enforcement, user):
        for event in ['invalid_hex', 'unapproved_font', 'wrong_spacing']:
            log = BrandViolationLog.objects.create(
                enforcement=enforcement, user=user,
                event_type=event, details={},
            )
            assert log.event_type == event


@pytest.mark.api
class TestBrandKitAPI:
    """Tests for BrandKit API endpoints."""

    def test_list_enforcements(self, auth_client, enforcement):
        response = auth_client.get('/api/v1/brand-kit/enforcement/')
        assert response.status_code == status.HTTP_200_OK

    def test_list_violations(self, auth_client, enforcement, user):
        BrandViolationLog.objects.create(
            enforcement=enforcement, user=user,
            event_type='invalid_hex', details={},
        )
        response = auth_client.get('/api/v1/brand-kit/violations/')
        assert response.status_code == status.HTTP_200_OK

    def test_brand_kit_unauthenticated(self, api_client, db):
        response = api_client.get('/api/v1/brand-kit/enforcement/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
