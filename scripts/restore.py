#!/usr/bin/env python3
"""
Database and Media Restore Script for AI Design Tool

This script restores backups created by the backup script,
with support for local storage and S3.

Usage:
    python restore.py --backup-path /path/to/backup.sql --type database
    python restore.py --backup-manifest /path/to/manifest.json --type full
    
Examples:
    python restore.py --backup-path /tmp/database_backup_20241231_120000.sql --type database
    python restore.py --s3-key backups/2024/12/backup_manifest_20241231_120000.json --type full
"""

import os
import sys
import argparse
import subprocess
import json
import logging
import tempfile
import datetime
import shutil
from pathlib import Path
from typing import Optional

# Add Django settings
sys.path.append('/path/to/backend')  # Adjust path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

import django
django.setup()

from django.conf import settings  # noqa: E402

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RestoreManager:
    """Handles restore operations for AI Design Tool"""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.mkdtemp())
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
            }
        }
    
    def restore_database(self, backup_path: str, drop_existing: bool = False) -> bool:
        """Restore database from backup file"""
        logger.info(f"Starting database restore from: {backup_path}")
        
        if not Path(backup_path).exists():
            logger.error(f"Backup file not found: {backup_path}")
            return False
        
        try:
            # Optionally drop and recreate database
            if drop_existing:
                logger.warning("Dropping existing database...")
                self._drop_database()
                self._create_database()
            
            # Restore from SQL dump
            cmd = [
                'psql',
                '-h', self.config['database']['host'],
                '-p', self.config['database']['port'],
                '-U', self.config['database']['user'],
                '-d', self.config['database']['name'],
                '-f', backup_path,
                '--quiet'
            ]
            
            env = os.environ.copy()
            env['PGPASSWORD'] = self.config['database']['password']
            
            _result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info("Database restore completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Database restore failed: {e}")
            logger.error(f"stderr: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during database restore: {e}")
            return False
    
    def restore_media(self, backup_path: str) -> bool:
        """Restore media files from backup archive"""
        logger.info(f"Starting media restore from: {backup_path}")
        
        if not Path(backup_path).exists():
            logger.error(f"Backup file not found: {backup_path}")
            return False
        
        media_root = Path(settings.MEDIA_ROOT)
        
        try:
            # Backup existing media if it exists
            if media_root.exists():
                backup_existing = f"{media_root}_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
                logger.info(f"Backing up existing media to: {backup_existing}")
                shutil.move(str(media_root), backup_existing)
            
            # Create media directory
            media_root.parent.mkdir(parents=True, exist_ok=True)
            
            # Extract archive
            cmd = [
                'tar',
                '-xzf', backup_path,
                '-C', str(media_root.parent)
            ]
            
            _result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info("Media restore completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Media restore failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during media restore: {e}")
            return False
    
    def download_from_s3(self, s3_key: str) -> Optional[str]:
        """Download backup file from S3"""
        if not self.config['s3']['bucket']:
            logger.error("S3 bucket not configured")
            return None
        
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            s3_client = boto3.client(
                's3',
                region_name=self.config['s3']['region'],
                aws_access_key_id=self.config['s3']['access_key'],
                aws_secret_access_key=self.config['s3']['secret_key']
            )
            
            # Download to temporary file
            local_path = self.temp_dir / Path(s3_key).name
            
            logger.info(f"Downloading s3://{self.config['s3']['bucket']}/{s3_key} to {local_path}")
            
            s3_client.download_file(
                self.config['s3']['bucket'],
                s3_key,
                str(local_path)
            )
            
            logger.info(f"Successfully downloaded from S3: {local_path}")
            return str(local_path)
            
        except ImportError:
            logger.error("boto3 not installed. Install with: pip install boto3")
            return None
        except ClientError as e:
            logger.error(f"S3 download failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during S3 download: {e}")
            return None
    
    def restore_from_manifest(self, manifest_path: str, drop_existing: bool = False) -> bool:
        """Restore from backup manifest"""
        logger.info(f"Starting restore from manifest: {manifest_path}")
        
        try:
            # Load manifest
            if manifest_path.startswith('s3://'):
                # Download from S3
                s3_key = manifest_path.replace('s3://', '').split('/', 1)[1]
                manifest_path = self.download_from_s3(s3_key)
                if not manifest_path:
                    return False
            
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            logger.info(f"Manifest loaded - Date: {manifest['date']}, Version: {manifest['version']}")
            
            # Restore each backup
            success = True
            
            for backup in manifest['backups']:
                backup_type = backup['type']
                backup_file = backup['filename']
                
                # Find backup file (try same directory as manifest first)
                manifest_dir = Path(manifest_path).parent
                backup_path = manifest_dir / backup_file
                
                if not backup_path.exists():
                    # Try original path from manifest
                    backup_path = Path(backup['path'])
                
                if not backup_path.exists():
                    logger.error(f"Backup file not found: {backup_file}")
                    success = False
                    continue
                
                # Restore based on type
                if backup_type == 'database':
                    if not self.restore_database(str(backup_path), drop_existing):
                        success = False
                elif backup_type == 'media':
                    if not self.restore_media(str(backup_path)):
                        success = False
            
            if success:
                logger.info("Full restore completed successfully")
            else:
                logger.error("Some restores failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Restore from manifest failed: {e}")
            return False
    
    def _drop_database(self) -> None:
        """Drop the database (dangerous!)"""
        cmd = [
            'dropdb',
            '-h', self.config['database']['host'],
            '-p', self.config['database']['port'],
            '-U', self.config['database']['user'],
            '--if-exists',
            self.config['database']['name']
        ]
        
        env = os.environ.copy()
        env['PGPASSWORD'] = self.config['database']['password']
        
        subprocess.run(cmd, env=env, check=True)
    
    def _create_database(self) -> None:
        """Create a new database"""
        cmd = [
            'createdb',
            '-h', self.config['database']['host'],
            '-p', self.config['database']['port'],
            '-U', self.config['database']['user'],
            self.config['database']['name']
        ]
        
        env = os.environ.copy()
        env['PGPASSWORD'] = self.config['database']['password']
        
        subprocess.run(cmd, env=env, check=True)


def main():
    """Main restore script entry point"""
    parser = argparse.ArgumentParser(
        description='AI Design Tool Restore Script',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python restore.py --backup-path /tmp/database_backup.sql --type database
    python restore.py --backup-manifest /tmp/manifest.json --type full
    python restore.py --s3-key backups/2024/12/manifest.json --type full
        """
    )
    
    parser.add_argument(
        '--backup-path',
        help='Path to backup file (for single file restore)'
    )
    
    parser.add_argument(
        '--backup-manifest',
        help='Path to backup manifest file (for full restore)'
    )
    
    parser.add_argument(
        '--s3-key',
        help='S3 key for backup file/manifest'
    )
    
    parser.add_argument(
        '--type',
        choices=['database', 'media', 'full'],
        required=True,
        help='Type of restore to perform'
    )
    
    parser.add_argument(
        '--drop-existing',
        action='store_true',
        help='Drop existing database before restore (DANGEROUS!)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without actually doing it'
    )
    
    args = parser.parse_args()
    
    if args.drop_existing:
        response = input("This will DROP the existing database. Are you sure? (type 'yes'): ")
        if response.lower() != 'yes':
            logger.info("Restore cancelled by user")
            return
    
    if args.dry_run:
        logger.info(f"DRY RUN: Would restore {args.type} from {args.backup_path or args.backup_manifest or args.s3_key}")
        return
    
    try:
        restore_manager = RestoreManager()
        
        if args.type == 'full':
            if args.backup_manifest:
                success = restore_manager.restore_from_manifest(args.backup_manifest, args.drop_existing)
            elif args.s3_key:
                success = restore_manager.restore_from_manifest(f"s3://{args.s3_key}", args.drop_existing)
            else:
                logger.error("Full restore requires --backup-manifest or --s3-key")
                sys.exit(1)
        else:
            if args.s3_key:
                backup_path = restore_manager.download_from_s3(args.s3_key)
                if not backup_path:
                    sys.exit(1)
            else:
                backup_path = args.backup_path
            
            if not backup_path:
                logger.error(f"{args.type} restore requires --backup-path or --s3-key")
                sys.exit(1)
            
            if args.type == 'database':
                success = restore_manager.restore_database(backup_path, args.drop_existing)
            elif args.type == 'media':
                success = restore_manager.restore_media(backup_path)
        
        if success:
            logger.info("Restore completed successfully")
            sys.exit(0)
        else:
            logger.error("Restore failed")
            sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("Restore interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Restore script failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
