"""
Unit tests for projects models.
"""
import pytest
from django.contrib.auth.models import User
from projects.models import Project, DesignComponent, ProjectVersion, ExportTemplate


@pytest.mark.unit
class TestProjectModel:
    """Tests for Project model."""

    def test_create_project(self, user):
        project = Project.objects.create(
            user=user,
            name='My Design',
            description='Test project',
            project_type='graphic',
        )
        assert project.name == 'My Design'
        assert project.user == user
        assert project.project_type == 'graphic'

    def test_project_default_canvas(self, user):
        project = Project.objects.create(user=user, name='Test')
        assert project.canvas_width is not None
        assert project.canvas_height is not None

    def test_project_str(self, user):
        project = Project.objects.create(user=user, name='Test Project')
        assert str(project) == 'Test Project' or 'Test Project' in str(project)

    def test_project_types(self, user):
        for ptype in ['graphic', 'ui_ux', 'logo']:
            proj = Project.objects.create(
                user=user, name=f'{ptype} project', project_type=ptype
            )
            assert proj.project_type == ptype

    def test_project_collaborators(self, user, user2):
        project = Project.objects.create(user=user, name='Collab Test')
        project.collaborators.add(user2)
        assert user2 in project.collaborators.all()

    def test_project_json_fields(self, user):
        project = Project.objects.create(
            user=user,
            name='JSON Test',
            design_data={'layers': []},
            color_palette=['#FF0000', '#00FF00'],
            suggested_fonts=['Arial', 'Helvetica'],
        )
        project.refresh_from_db()
        assert project.design_data == {'layers': []}
        assert '#FF0000' in project.color_palette

    def test_project_is_public_default(self, user):
        project = Project.objects.create(user=user, name='Public Test')
        assert project.is_public is False


@pytest.mark.unit
class TestDesignComponent:
    """Tests for DesignComponent model."""

    def test_create_component(self, user):
        project = Project.objects.create(user=user, name='Test')
        component = DesignComponent.objects.create(
            project=project,
            component_type='text',
            properties={'text': 'Hello', 'fontSize': 24},
            z_index=1,
        )
        assert component.component_type == 'text'
        assert component.z_index == 1

    def test_component_ai_generated(self, user):
        project = Project.objects.create(user=user, name='AI Test')
        component = DesignComponent.objects.create(
            project=project,
            component_type='image',
            ai_generated=True,
            ai_prompt='Generate a logo',
        )
        assert component.ai_generated is True
        assert component.ai_prompt == 'Generate a logo'

    def test_multiple_components(self, user):
        project = Project.objects.create(user=user, name='Multi')
        for i in range(5):
            DesignComponent.objects.create(
                project=project,
                component_type='shape',
                z_index=i,
            )
        assert project.designcomponent_set.count() == 5


@pytest.mark.unit
class TestProjectVersion:
    """Tests for ProjectVersion model."""

    def test_create_version(self, user):
        project = Project.objects.create(user=user, name='Versioned')
        version = ProjectVersion.objects.create(
            project=project,
            version_number=1,
            design_data={'state': 'initial'},
            created_by=user,
        )
        assert version.version_number == 1
        assert version.created_by == user

    def test_multiple_versions(self, user):
        project = Project.objects.create(user=user, name='V Test')
        for i in range(3):
            ProjectVersion.objects.create(
                project=project,
                version_number=i + 1,
                design_data={'v': i + 1},
                created_by=user,
            )
        assert project.projectversion_set.count() == 3


@pytest.mark.unit
class TestExportTemplate:
    """Tests for ExportTemplate model."""

    def test_create_export_template(self, user):
        template = ExportTemplate.objects.create(
            user=user,
            name='High Res PNG',
            format='png',
            quality=100,
            width=1920,
            height=1080,
            scale=2,
        )
        assert template.format == 'png'
        assert template.quality == 100

    def test_export_template_is_public(self, user):
        template = ExportTemplate.objects.create(
            user=user, name='Public Template', format='svg', is_public=True
        )
        assert template.is_public is True
