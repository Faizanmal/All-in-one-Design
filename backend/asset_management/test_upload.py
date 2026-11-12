from unittest.mock import Mock, patch

from django.core.files.uploadedfile import SimpleUploadedFile

from asset_management.models import AssetFolder, EnhancedAsset


def test_upload_creates_real_managed_asset(auth_client, user):
    storage = Mock()
    storage.upload_asset.return_value = 'https://assets.example.com/notes.txt'
    with patch('assets.storage.get_storage_service', return_value=storage):
        response = auth_client.post('/api/v1/asset-management/items/upload/', {
            'file': SimpleUploadedFile('notes.txt', b'hello', content_type='text/plain'),
            'asset_type': 'document',
        }, format='multipart')
    assert response.status_code == 201
    asset = EnhancedAsset.objects.get(id=response.data['id'])
    assert asset.user == user
    assert asset.file_size == 5
    assert response.data['file_url'] == 'https://assets.example.com/notes.txt'
    stats = auth_client.get('/api/v1/analytics/dashboard/').data
    assert stats['assets']['total'] == 1
    assert stats['assets']['storage_bytes'] == 5


def test_upload_rejects_another_users_folder(auth_client, user2):
    folder = AssetFolder.objects.create(user=user2, name='Private')
    with patch('assets.storage.get_storage_service') as storage:
        response = auth_client.post('/api/v1/asset-management/items/upload/', {
            'file': SimpleUploadedFile('notes.txt', b'hello'),
            'asset_type': 'document', 'folder': folder.id,
        }, format='multipart')
    assert response.status_code == 400
    storage.assert_not_called()


def test_upload_storage_failure_is_not_reported_as_success(auth_client):
    storage = Mock()
    storage.upload_asset.return_value = None
    with patch('assets.storage.get_storage_service', return_value=storage):
        response = auth_client.post('/api/v1/asset-management/items/upload/', {
            'file': SimpleUploadedFile('notes.txt', b'hello'), 'asset_type': 'document',
        }, format='multipart')
    assert response.status_code == 503
    assert EnhancedAsset.objects.count() == 0
