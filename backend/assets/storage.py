"""
AWS S3 Storage Configuration and Utilities
"""
import os
import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from typing import Optional
import uuid


class S3StorageService:
    """Service for handling file uploads to AWS S3"""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
        )
        self.bucket_name = os.getenv('AWS_STORAGE_BUCKET_NAME', 'ai-design-assets')
    
    def upload_file(self, file_obj, folder: str = 'uploads', filename: Optional[str] = None) -> Optional[str]:
        """
        Upload file to S3 bucket
        
        Args:
            file_obj: File object to upload
            folder: S3 folder path
            filename: Optional custom filename
            
        Returns:
            URL of uploaded file or None if failed
        """
        if filename is None:
            # Generate unique filename
            ext = file_obj.name.split('.')[-1] if '.' in file_obj.name else ''
            filename = f"{uuid.uuid4()}.{ext}" if ext else str(uuid.uuid4())
        
        s3_key = f"{folder}/{filename}"
        
        try:
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                s3_key,
                ExtraArgs={'ACL': 'public-read'}
            )
            
            # Generate URL
            url = f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"
            return url
            
        except ClientError as e:
            print(f"S3 upload error: {e}")
            return None
    
    def upload_image(self, file_obj, filename: Optional[str] = None) -> Optional[str]:
        """Upload image to S3"""
        return self.upload_file(file_obj, folder='images', filename=filename)
    
    def upload_asset(self, file_obj, asset_type: str, filename: Optional[str] = None) -> Optional[str]:
        """Upload design asset to S3"""
        folder = f"assets/{asset_type}"
        return self.upload_file(file_obj, folder=folder, filename=filename)
    
    def upload_export(self, file_obj, project_id: int, format: str) -> Optional[str]:
        """Upload exported design file"""
        folder = f"exports/{project_id}"
        timestamp = uuid.uuid4().hex[:8]
        filename = f"export_{timestamp}.{format}"
        return self.upload_file(file_obj, folder=folder, filename=filename)
    
    def delete_file(self, s3_url: str) -> bool:
        """
        Delete file from S3
        
        Args:
            s3_url: Full S3 URL of the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract key from URL
            key = s3_url.split(f"{self.bucket_name}.s3.amazonaws.com/")[-1]
            
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return True
            
        except ClientError as e:
            print(f"S3 delete error: {e}")
            return False
    
    def generate_presigned_url(self, s3_key: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate a presigned URL for temporary access
        
        Args:
            s3_key: S3 object key
            expiration: URL expiration time in seconds (default 1 hour)
            
        Returns:
            Presigned URL or None if failed
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            return url
            
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return None
    
    def list_files(self, prefix: str = '') -> list:
        """
        List files in S3 bucket with given prefix
        
        Args:
            prefix: S3 key prefix to filter results
            
        Returns:
            List of file keys
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                return []
            
            return [obj['Key'] for obj in response['Contents']]
            
        except ClientError as e:
            print(f"Error listing files: {e}")
            return []
    
    def get_file_url(self, s3_key: str) -> str:
        """Get public URL for S3 object"""
        return f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"


# Alternative: Local File Storage (for development)
class LocalStorageService:
    """Local file storage for development"""
    
    def __init__(self):
        self.storage_dir = os.path.join(settings.BASE_DIR, 'media')
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def upload_file(self, file_obj, folder: str = 'uploads', filename: Optional[str] = None) -> Optional[str]:
        """Save file locally"""
        if filename is None:
            ext = file_obj.name.split('.')[-1] if '.' in file_obj.name else ''
            filename = f"{uuid.uuid4()}.{ext}" if ext else str(uuid.uuid4())
        
        folder_path = os.path.join(self.storage_dir, folder)
        os.makedirs(folder_path, exist_ok=True)
        
        file_path = os.path.join(folder_path, filename)
        
        try:
            with open(file_path, 'wb+') as destination:
                for chunk in file_obj.chunks():
                    destination.write(chunk)
            
            # Return relative URL
            return f"/media/{folder}/{filename}"
            
        except Exception as e:
            print(f"Local storage error: {e}")
            return None
    
    def upload_image(self, file_obj, filename: Optional[str] = None) -> Optional[str]:
        """Upload image locally"""
        return self.upload_file(file_obj, folder='images', filename=filename)
    
    def upload_asset(self, file_obj, asset_type: str, filename: Optional[str] = None) -> Optional[str]:
        """Upload asset locally"""
        folder = f"assets/{asset_type}"
        return self.upload_file(file_obj, folder=folder, filename=filename)
    
    def upload_export(self, file_obj, project_id: int, format: str) -> Optional[str]:
        """Upload export locally"""
        folder = f"exports/{project_id}"
        timestamp = uuid.uuid4().hex[:8]
        filename = f"export_{timestamp}.{format}"
        return self.upload_file(file_obj, folder=folder, filename=filename)
    
    def delete_file(self, file_url: str) -> bool:
        """Delete local file"""
        try:
            file_path = os.path.join(settings.BASE_DIR, file_url.lstrip('/'))
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Delete error: {e}")
            return False


# Factory function to get storage service based on settings
def get_storage_service():
    """Get appropriate storage service based on configuration"""
    use_s3 = os.getenv('USE_S3_STORAGE', 'False').lower() == 'true'
    
    if use_s3:
        return S3StorageService()
    else:
        return LocalStorageService()
