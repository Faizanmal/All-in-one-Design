#!/usr/bin/env python3
"""
Database and Media Backup Script for AI Design Tool

This script creates backups of the PostgreSQL database and media files,
with support for local storage, S3, and automated scheduling.

Usage:
    python backup.py --type [database|media|full] --destination [local|s3]
    
Examples:
    python backup.py --type full --destination local
    python backup.py --type database --destination s3
    python backup.py --schedule daily
"""

import os
import sys
import argparse
import subprocess
import datetime
import logging
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional

# Add Django settings
sys.path.append('/path/to/backend')  # Adjust path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

import django
django.setup()

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/aidesigntool/backup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class BackupManager:
    """Handles backup operations for AI Design Tool"""
    
    def __init__(self, destination: str = 'local'):
        self.destination = destination
        self.timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_dir = Path('/tmp/aidesigntool_backups')
        self.backup_dir.mkdir(exist_ok=True)
        
        # Configuration
        self.config = {
            'database': {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': os.getenv('DB_PORT', '5432'),
                'name': os.getenv('DB_NAME', 'aidesigntool'),
                'user': os.getenv('DB_USER', 'postgres'),
                'password': os.getenv('DB_PASSWORD', ''),
            },
            's3': {
                'bucket': os.getenv('BACKUP_S3_BUCKET', ''),
                'region': os.getenv('BACKUP_S3_REGION', 'us-east-1'),
                'access_key': os.getenv('AWS_ACCESS_KEY_ID', ''),
                'secret_key': os.getenv('AWS_SECRET_ACCESS_KEY', ''),
            },
            'retention': {
                'daily': 30,    # Keep 30 daily backups
                'weekly': 12,   # Keep 12 weekly backups
                'monthly': 12,  # Keep 12 monthly backups
            }
        }
    
    def backup_database(self) -> str:
        """Create database backup using pg_dump"""
        logger.info("Starting database backup...")
        
        backup_filename = f"database_backup_{self.timestamp}.sql"
        backup_path = self.backup_dir / backup_filename
        
        try:
            # Create pg_dump command
            cmd = [
                'pg_dump',
                '-h', self.config['database']['host'],
                '-p', self.config['database']['port'],
                '-U', self.config['database']['user'],
                '-d', self.config['database']['name'],
                '-f', str(backup_path),
                '--verbose',
                '--no-owner',
                '--no-privileges'
            ]
            
            # Set password via environment
            env = os.environ.copy()
            env['PGPASSWORD'] = self.config['database']['password']
            
            # Execute backup
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info(f"Database backup completed: {backup_path}")
            logger.info(f"Backup size: {backup_path.stat().st_size / 1024 / 1024:.2f} MB")
            
            return str(backup_path)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Database backup failed: {e}")
            logger.error(f"stdout: {e.stdout}")
            logger.error(f"stderr: {e.stderr}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during database backup: {e}")
            raise
    
    def backup_media(self) -> str:
        """Create media files backup"""
        logger.info("Starting media backup...")
        
        media_root = Path(settings.MEDIA_ROOT)
        if not media_root.exists():
            logger.warning(f"Media directory does not exist: {media_root}")
            return ""
        
        backup_filename = f"media_backup_{self.timestamp}.tar.gz"
        backup_path = self.backup_dir / backup_filename
        
        try:
            # Create compressed archive
            cmd = [
                'tar',
                '-czf', str(backup_path),
                '-C', str(media_root.parent),
                media_root.name
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info(f"Media backup completed: {backup_path}")
            logger.info(f"Backup size: {backup_path.stat().st_size / 1024 / 1024:.2f} MB")
            
            return str(backup_path)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Media backup failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during media backup: {e}")
            raise
    
    def upload_to_s3(self, file_path: str) -> bool:
        """Upload backup file to S3"""
        if not self.config['s3']['bucket']:
            logger.error("S3 bucket not configured")
            return False
        
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            s3_client = boto3.client(
                's3',
                region_name=self.config['s3']['region'],
                aws_access_key_id=self.config['s3']['access_key'],
                aws_secret_access_key=self.config['s3']['secret_key']
            )
            
            file_name = Path(file_path).name
            s3_key = f"backups/{datetime.datetime.now().year}/{datetime.datetime.now().month:02d}/{file_name}"
            
            logger.info(f"Uploading {file_path} to s3://{self.config['s3']['bucket']}/{s3_key}")
            
            s3_client.upload_file(
                file_path,
                self.config['s3']['bucket'],
                s3_key,
                ExtraArgs={
                    'ServerSideEncryption': 'AES256',
                    'StorageClass': 'STANDARD_IA'
                }
            )
            
            logger.info(f"Successfully uploaded to S3: {s3_key}")
            return True
            
        except ImportError:
            logger.error("boto3 not installed. Install with: pip install boto3")
            return False
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during S3 upload: {e}")
            return False
    
    def cleanup_old_backups(self) -> None:
        """Remove old backup files based on retention policy"""
        logger.info("Cleaning up old backups...")
        
        try:
            # Local cleanup
            backup_files = list(self.backup_dir.glob('*backup_*.sql')) + \
                          list(self.backup_dir.glob('*backup_*.tar.gz'))
            
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Keep only the specified number of backups
            max_local_backups = self.config['retention']['daily']
            if len(backup_files) > max_local_backups:
                for old_backup in backup_files[max_local_backups:]:
                    logger.info(f"Removing old backup: {old_backup}")
                    old_backup.unlink()
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def create_backup_manifest(self, backups: List[str]) -> str:
        """Create backup manifest with metadata"""
        manifest = {
            'timestamp': self.timestamp,
            'date': datetime.datetime.now().isoformat(),
            'version': '2.0.0',
            'backups': [],
            'environment': {
                'python_version': sys.version,
                'django_version': django.get_version(),
                'database': self.config['database']['name'],
            }
        }
        
        for backup_path in backups:
            if backup_path:
                file_path = Path(backup_path)
                manifest['backups'].append({
                    'type': 'database' if file_path.suffix == '.sql' else 'media',
                    'filename': file_path.name,
                    'size': file_path.stat().st_size,
                    'path': str(file_path)
                })
        
        manifest_path = self.backup_dir / f"backup_manifest_{self.timestamp}.json"
        with manifest_path.open('w') as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"Backup manifest created: {manifest_path}")
        return str(manifest_path)
    
    def run_full_backup(self) -> Dict[str, str]:
        """Run complete backup process"""
        logger.info(f"Starting full backup process with destination: {self.destination}")
        
        backups = []
        
        try:
            # Database backup
            db_backup = self.backup_database()
            if db_backup:
                backups.append(db_backup)
            
            # Media backup
            media_backup = self.backup_media()
            if media_backup:
                backups.append(media_backup)
            
            # Create manifest
            manifest = self.create_backup_manifest(backups)
            backups.append(manifest)
            
            # Upload to S3 if configured
            if self.destination == 's3':
                for backup_path in backups:
                    self.upload_to_s3(backup_path)
            
            # Cleanup old backups
            self.cleanup_old_backups()
            
            logger.info("Backup process completed successfully")
            
            return {
                'status': 'success',
                'timestamp': self.timestamp,
                'backups': backups,
                'destination': self.destination
            }
            
        except Exception as e:
            logger.error(f"Backup process failed: {e}")
            return {
                'status': 'failed',
                'timestamp': self.timestamp,
                'error': str(e),
                'destination': self.destination
            }


def main():
    """Main backup script entry point"""
    parser = argparse.ArgumentParser(
        description='AI Design Tool Backup Script',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python backup.py --type full --destination local
    python backup.py --type database --destination s3
    python backup.py --type media --destination local
        """
    )
    
    parser.add_argument(
        '--type',
        choices=['database', 'media', 'full'],
        default='full',
        help='Type of backup to perform (default: full)'
    )
    
    parser.add_argument(
        '--destination',
        choices=['local', 's3'],
        default='local',
        help='Backup destination (default: local)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without actually doing it'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress output except for errors'
    )
    
    args = parser.parse_args()
    
    if args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    
    if args.dry_run:
        logger.info(f"DRY RUN: Would perform {args.type} backup to {args.destination}")
        return
    
    try:
        backup_manager = BackupManager(destination=args.destination)
        
        if args.type == 'database':
            result = backup_manager.backup_database()
            logger.info(f"Database backup completed: {result}")
            
        elif args.type == 'media':
            result = backup_manager.backup_media()
            logger.info(f"Media backup completed: {result}")
            
        elif args.type == 'full':
            result = backup_manager.run_full_backup()
            if result['status'] == 'success':
                logger.info("Full backup completed successfully")
                sys.exit(0)
            else:
                logger.error(f"Backup failed: {result.get('error', 'Unknown error')}")
                sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("Backup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Backup script failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
