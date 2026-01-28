"""
Automated Backup System with Integrity Verification
Implements comprehensive backup strategy:
- Automated daily backups
- Versioned backups with retention
- Integrity verification using checksums
- Off-site storage support (S3)
- Quick restore mechanisms
"""
import os
import gzip
import shutil
import hashlib
import json
import subprocess
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.core.management import call_command
from django.core.mail import send_mail
from celery import shared_task

logger = logging.getLogger('backup')


class BackupConfig:
    """Backup configuration"""
    
    # Backup retention settings
    DAILY_RETENTION_DAYS = 7
    WEEKLY_RETENTION_WEEKS = 4
    MONTHLY_RETENTION_MONTHS = 12
    
    # Backup locations
    LOCAL_BACKUP_DIR = os.path.join(settings.BASE_DIR, 'backups')
    
    # S3 settings (if enabled)
    USE_S3_BACKUP = getattr(settings, 'USE_S3_BACKUP', False)
    S3_BACKUP_BUCKET = getattr(settings, 'S3_BACKUP_BUCKET', '')
    S3_BACKUP_PREFIX = getattr(settings, 'S3_BACKUP_PREFIX', 'backups/')
    
    # Notification settings
    NOTIFY_ON_SUCCESS = getattr(settings, 'BACKUP_NOTIFY_SUCCESS', False)
    NOTIFY_ON_FAILURE = getattr(settings, 'BACKUP_NOTIFY_FAILURE', True)
    NOTIFICATION_EMAIL = getattr(settings, 'BACKUP_NOTIFICATION_EMAIL', '')


class BackupManager:
    """
    Manages database and file backups with verification
    """
    
    def __init__(self):
        self.config = BackupConfig()
        self._ensure_backup_dir()
    
    def _ensure_backup_dir(self):
        """Ensure backup directory exists"""
        os.makedirs(self.config.LOCAL_BACKUP_DIR, exist_ok=True)
    
    def create_backup(self, backup_type: str = 'full') -> Dict[str, Any]:
        """
        Create a complete backup
        
        Args:
            backup_type: 'full', 'database', or 'media'
        
        Returns:
            Backup metadata dictionary
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_id = f"backup_{backup_type}_{timestamp}"
        
        metadata = {
            'backup_id': backup_id,
            'backup_type': backup_type,
            'timestamp': timestamp,
            'created_at': datetime.now().isoformat(),
            'files': [],
            'checksums': {},
            'status': 'in_progress',
        }
        
        try:
            if backup_type in ('full', 'database'):
                db_backup = self._backup_database(backup_id)
                metadata['files'].append(db_backup)
                metadata['checksums'][db_backup] = self._calculate_checksum(db_backup)
            
            if backup_type in ('full', 'media'):
                media_backup = self._backup_media(backup_id)
                if media_backup:
                    metadata['files'].append(media_backup)
                    metadata['checksums'][media_backup] = self._calculate_checksum(media_backup)
            
            # Save metadata
            metadata_file = self._save_metadata(metadata)
            metadata['metadata_file'] = metadata_file
            metadata['status'] = 'completed'
            
            # Verify backup integrity
            if not self._verify_backup(metadata):
                metadata['status'] = 'verification_failed'
                raise BackupError("Backup verification failed")
            
            # Upload to S3 if configured
            if self.config.USE_S3_BACKUP:
                self._upload_to_s3(metadata)
            
            logger.info(f"Backup completed successfully: {backup_id}")
            
            # Send notification
            if self.config.NOTIFY_ON_SUCCESS:
                self._send_notification('Backup Successful', metadata)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            metadata['status'] = 'failed'
            metadata['error'] = str(e)
            
            if self.config.NOTIFY_ON_FAILURE:
                self._send_notification('Backup Failed', metadata, is_error=True)
            
            raise BackupError(f"Backup failed: {e}") from e
    
    def _backup_database(self, backup_id: str) -> str:
        """
        Backup the database
        """
        db_settings = settings.DATABASES['default']
        db_engine = db_settings['ENGINE']
        
        backup_file = os.path.join(
            self.config.LOCAL_BACKUP_DIR,
            f"{backup_id}_database.sql.gz"
        )
        
        if 'sqlite3' in db_engine:
            # SQLite backup
            return self._backup_sqlite(db_settings['NAME'], backup_file)
        elif 'postgresql' in db_engine:
            # PostgreSQL backup
            return self._backup_postgresql(db_settings, backup_file)
        elif 'mysql' in db_engine:
            # MySQL backup
            return self._backup_mysql(db_settings, backup_file)
        else:
            # Use Django dumpdata as fallback
            return self._backup_django_dump(backup_id)
    
    def _backup_sqlite(self, db_path: str, backup_file: str) -> str:
        """Backup SQLite database"""
        temp_backup = backup_file.replace('.gz', '')
        
        # Use SQLite backup API
        import sqlite3
        source = sqlite3.connect(db_path)
        dest = sqlite3.connect(temp_backup)
        source.backup(dest)
        dest.close()
        source.close()
        
        # Compress
        with open(temp_backup, 'rb') as f_in:
            with gzip.open(backup_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        os.remove(temp_backup)
        
        logger.info(f"SQLite backup created: {backup_file}")
        return backup_file
    
    def _backup_postgresql(self, db_settings: dict, backup_file: str) -> str:
        """Backup PostgreSQL database"""
        env = os.environ.copy()
        env['PGPASSWORD'] = db_settings.get('PASSWORD', '')
        
        cmd = [
            'pg_dump',
            '-h', db_settings.get('HOST', 'localhost'),
            '-p', str(db_settings.get('PORT', 5432)),
            '-U', db_settings.get('USER', 'postgres'),
            '-d', db_settings.get('NAME', 'postgres'),
            '-F', 'c',  # Custom format (compressed)
        ]
        
        with open(backup_file.replace('.sql.gz', '.dump'), 'wb') as f:
            subprocess.run(cmd, stdout=f, env=env, check=True)
        
        # Rename to expected format
        actual_file = backup_file.replace('.sql.gz', '.dump')
        logger.info(f"PostgreSQL backup created: {actual_file}")
        return actual_file
    
    def _backup_mysql(self, db_settings: dict, backup_file: str) -> str:
        """Backup MySQL database"""
        cmd = [
            'mysqldump',
            '-h', db_settings.get('HOST', 'localhost'),
            '-P', str(db_settings.get('PORT', 3306)),
            '-u', db_settings.get('USER', 'root'),
            f"-p{db_settings.get('PASSWORD', '')}",
            '--single-transaction',
            '--routines',
            '--triggers',
            db_settings.get('NAME', 'mysql'),
        ]
        
        with gzip.open(backup_file, 'wt') as f:
            subprocess.run(cmd, stdout=f, check=True)
        
        logger.info(f"MySQL backup created: {backup_file}")
        return backup_file
    
    def _backup_django_dump(self, backup_id: str) -> str:
        """Fallback: Use Django's dumpdata command"""
        backup_file = os.path.join(
            self.config.LOCAL_BACKUP_DIR,
            f"{backup_id}_django_dump.json.gz"
        )
        
        # Dump data to JSON
        from io import StringIO
        output = StringIO()
        call_command('dumpdata', '--natural-foreign', '--natural-primary',
                    stdout=output, exclude=['contenttypes', 'auth.permission'])
        
        # Compress and save
        with gzip.open(backup_file, 'wt') as f:
            f.write(output.getvalue())
        
        logger.info(f"Django dump backup created: {backup_file}")
        return backup_file
    
    def _backup_media(self, backup_id: str) -> Optional[str]:
        """Backup media files"""
        media_root = getattr(settings, 'MEDIA_ROOT', None)
        
        if not media_root or not os.path.exists(media_root):
            logger.info("No media directory to backup")
            return None
        
        backup_file = os.path.join(
            self.config.LOCAL_BACKUP_DIR,
            f"{backup_id}_media.tar.gz"
        )
        
        # Create tar.gz archive
        shutil.make_archive(
            backup_file.replace('.tar.gz', ''),
            'gztar',
            root_dir=os.path.dirname(media_root),
            base_dir=os.path.basename(media_root)
        )
        
        logger.info(f"Media backup created: {backup_file}")
        return backup_file
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA-256 checksum of a file"""
        sha256_hash = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b''):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def _verify_backup(self, metadata: Dict[str, Any]) -> bool:
        """Verify backup integrity using checksums"""
        for file_path, expected_checksum in metadata['checksums'].items():
            if not os.path.exists(file_path):
                logger.error(f"Backup file missing: {file_path}")
                return False
            
            actual_checksum = self._calculate_checksum(file_path)
            if actual_checksum != expected_checksum:
                logger.error(f"Checksum mismatch for {file_path}")
                return False
        
        logger.info("Backup verification passed")
        return True
    
    def _save_metadata(self, metadata: Dict[str, Any]) -> str:
        """Save backup metadata to JSON file"""
        metadata_file = os.path.join(
            self.config.LOCAL_BACKUP_DIR,
            f"{metadata['backup_id']}_metadata.json"
        )
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        return metadata_file
    
    def _upload_to_s3(self, metadata: Dict[str, Any]):
        """Upload backup files to S3"""
        try:
            import boto3
            
            s3_client = boto3.client('s3')
            bucket = self.config.S3_BACKUP_BUCKET
            prefix = self.config.S3_BACKUP_PREFIX
            
            for file_path in metadata['files'] + [metadata.get('metadata_file', '')]:
                if file_path and os.path.exists(file_path):
                    key = f"{prefix}{os.path.basename(file_path)}"
                    s3_client.upload_file(file_path, bucket, key)
                    logger.info(f"Uploaded to S3: {key}")
            
        except Exception as e:
            logger.error(f"S3 upload failed: {e}")
            raise
    
    def _send_notification(self, subject: str, metadata: Dict[str, Any], is_error: bool = False):
        """Send backup notification email"""
        if not self.config.NOTIFICATION_EMAIL:
            return
        
        try:
            message = f"""
Backup Report
=============
Backup ID: {metadata['backup_id']}
Type: {metadata['backup_type']}
Status: {metadata['status']}
Created: {metadata['created_at']}

Files:
{chr(10).join(metadata.get('files', []))}

{'Error: ' + metadata.get('error', '') if is_error else ''}
            """
            
            send_mail(
                subject=f"[{'ERROR' if is_error else 'INFO'}] {subject}",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.config.NOTIFICATION_EMAIL],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
    
    def restore_backup(self, backup_id: str) -> bool:
        """
        Restore from a backup
        
        Args:
            backup_id: The backup identifier to restore
        
        Returns:
            True if restore successful
        """
        # Load metadata
        metadata_file = os.path.join(
            self.config.LOCAL_BACKUP_DIR,
            f"{backup_id}_metadata.json"
        )
        
        if not os.path.exists(metadata_file):
            raise BackupError(f"Backup metadata not found: {backup_id}")
        
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        # Verify before restore
        if not self._verify_backup(metadata):
            raise BackupError("Backup verification failed - cannot restore corrupted backup")
        
        try:
            # Restore database
            for file_path in metadata['files']:
                if 'database' in file_path or 'django_dump' in file_path:
                    self._restore_database(file_path)
                elif 'media' in file_path:
                    self._restore_media(file_path)
            
            logger.info(f"Backup restored successfully: {backup_id}")
            return True
            
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            raise BackupError(f"Restore failed: {e}") from e
    
    def _restore_database(self, backup_file: str):
        """Restore database from backup file"""
        db_settings = settings.DATABASES['default']
        db_engine = db_settings['ENGINE']
        
        if 'sqlite3' in db_engine:
            self._restore_sqlite(db_settings['NAME'], backup_file)
        elif 'postgresql' in db_engine:
            self._restore_postgresql(db_settings, backup_file)
        elif 'mysql' in db_engine:
            self._restore_mysql(db_settings, backup_file)
        elif 'django_dump' in backup_file:
            self._restore_django_dump(backup_file)
    
    def _restore_sqlite(self, db_path: str, backup_file: str):
        """Restore SQLite database"""
        # Create backup of current database
        if os.path.exists(db_path):
            shutil.copy(db_path, f"{db_path}.pre_restore")
        
        # Decompress and restore
        temp_file = backup_file.replace('.gz', '')
        with gzip.open(backup_file, 'rb') as f_in:
            with open(temp_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        shutil.copy(temp_file, db_path)
        os.remove(temp_file)
        
        logger.info("SQLite database restored")
    
    def _restore_postgresql(self, db_settings: dict, backup_file: str):
        """Restore PostgreSQL database"""
        env = os.environ.copy()
        env['PGPASSWORD'] = db_settings.get('PASSWORD', '')
        
        cmd = [
            'pg_restore',
            '-h', db_settings.get('HOST', 'localhost'),
            '-p', str(db_settings.get('PORT', 5432)),
            '-U', db_settings.get('USER', 'postgres'),
            '-d', db_settings.get('NAME', 'postgres'),
            '-c',  # Clean (drop) before restore
            backup_file,
        ]
        
        subprocess.run(cmd, env=env, check=True)
        logger.info("PostgreSQL database restored")
    
    def _restore_mysql(self, db_settings: dict, backup_file: str):
        """Restore MySQL database"""
        cmd = [
            'mysql',
            '-h', db_settings.get('HOST', 'localhost'),
            '-P', str(db_settings.get('PORT', 3306)),
            '-u', db_settings.get('USER', 'root'),
            f"-p{db_settings.get('PASSWORD', '')}",
            db_settings.get('NAME', 'mysql'),
        ]
        
        with gzip.open(backup_file, 'rt') as f:
            subprocess.run(cmd, stdin=f, check=True)
        
        logger.info("MySQL database restored")
    
    def _restore_django_dump(self, backup_file: str):
        """Restore from Django dump"""
        with gzip.open(backup_file, 'rt') as f:
            data = f.read()
        
        # Write to temp file for loaddata
        temp_file = '/tmp/restore_dump.json'
        with open(temp_file, 'w') as f:
            f.write(data)
        
        call_command('loaddata', temp_file)
        os.remove(temp_file)
        
        logger.info("Django dump restored")
    
    def _restore_media(self, backup_file: str):
        """Restore media files"""
        media_root = getattr(settings, 'MEDIA_ROOT', None)
        
        if not media_root:
            return
        
        # Backup current media
        if os.path.exists(media_root):
            shutil.move(media_root, f"{media_root}.pre_restore")
        
        # Extract backup
        shutil.unpack_archive(
            backup_file,
            os.path.dirname(media_root)
        )
        
        logger.info("Media files restored")
    
    def cleanup_old_backups(self):
        """Remove old backups based on retention policy"""
        now = datetime.now()
        
        for filename in os.listdir(self.config.LOCAL_BACKUP_DIR):
            if not filename.endswith('_metadata.json'):
                continue
            
            file_path = os.path.join(self.config.LOCAL_BACKUP_DIR, filename)
            
            try:
                with open(file_path, 'r') as f:
                    metadata = json.load(f)
                
                created_at = datetime.fromisoformat(metadata['created_at'])
                age_days = (now - created_at).days
                
                # Determine if backup should be kept
                keep = False
                
                # Keep daily backups for DAILY_RETENTION_DAYS
                if age_days < self.config.DAILY_RETENTION_DAYS:
                    keep = True
                # Keep one weekly backup for WEEKLY_RETENTION_WEEKS
                elif age_days < self.config.WEEKLY_RETENTION_WEEKS * 7:
                    if created_at.weekday() == 0:  # Monday
                        keep = True
                # Keep one monthly backup for MONTHLY_RETENTION_MONTHS
                elif age_days < self.config.MONTHLY_RETENTION_MONTHS * 30:
                    if created_at.day == 1:  # First of month
                        keep = True
                
                if not keep:
                    # Delete backup files
                    for backup_file in metadata.get('files', []):
                        if os.path.exists(backup_file):
                            os.remove(backup_file)
                            logger.info(f"Deleted old backup: {backup_file}")
                    
                    os.remove(file_path)
                    logger.info(f"Deleted old metadata: {file_path}")
                    
            except Exception as e:
                logger.error(f"Error processing backup file {filename}: {e}")
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups"""
        backups = []
        
        for filename in os.listdir(self.config.LOCAL_BACKUP_DIR):
            if not filename.endswith('_metadata.json'):
                continue
            
            file_path = os.path.join(self.config.LOCAL_BACKUP_DIR, filename)
            
            try:
                with open(file_path, 'r') as f:
                    metadata = json.load(f)
                
                # Calculate size
                total_size = sum(
                    os.path.getsize(f) for f in metadata.get('files', [])
                    if os.path.exists(f)
                )
                
                backups.append({
                    'backup_id': metadata['backup_id'],
                    'backup_type': metadata['backup_type'],
                    'created_at': metadata['created_at'],
                    'status': metadata['status'],
                    'size_bytes': total_size,
                    'files_count': len(metadata.get('files', [])),
                })
            except Exception as e:
                logger.error(f"Error reading backup metadata {filename}: {e}")
        
        return sorted(backups, key=lambda x: x['created_at'], reverse=True)


class BackupError(Exception):
    """Custom exception for backup errors"""
    pass


# ===================== CELERY TASKS =====================

@shared_task(name='backup.create_daily_backup')
def create_daily_backup():
    """Celery task for automated daily backups"""
    manager = BackupManager()
    return manager.create_backup('full')


@shared_task(name='backup.cleanup_old_backups')
def cleanup_old_backups_task():
    """Celery task for cleaning up old backups"""
    manager = BackupManager()
    manager.cleanup_old_backups()
    return "Cleanup completed"


@shared_task(name='backup.verify_backup_integrity')
def verify_backup_integrity(backup_id: str):
    """Celery task to verify backup integrity"""
    manager = BackupManager()
    
    metadata_file = os.path.join(
        manager.config.LOCAL_BACKUP_DIR,
        f"{backup_id}_metadata.json"
    )
    
    if not os.path.exists(metadata_file):
        return {'status': 'error', 'message': 'Backup not found'}
    
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    
    is_valid = manager._verify_backup(metadata)
    
    return {
        'backup_id': backup_id,
        'status': 'valid' if is_valid else 'corrupted',
        'verified_at': datetime.now().isoformat(),
    }
