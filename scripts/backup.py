#!/usr/bin/env python3
"""
Host-side backup for Docker Compose production/dev stacks.

Runs against compose services (db + backend media volume). Does not require
Django on the host.

Usage (from repo root):
    python scripts/backup.py --type full
    python scripts/backup.py --type database
    python scripts/backup.py --type media
    python scripts/backup.py --type full --compose-file docker-compose.yml

Backups land in ./backups/ (gitignored). Optional S3 upload when AWS_* + bucket set.
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BACKUP_DIR = ROOT / "backups"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("backup")


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def compose_base(compose_file: str) -> list[str]:
    return ["docker", "compose", "-f", compose_file]


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    logger.info("Running: %s", " ".join(cmd))
    return subprocess.run(cmd, check=True, **kwargs)


def backup_database(compose_file: str, backup_dir: Path, stamp: str) -> Path:
    db_name = os.getenv("DB_NAME", "aidesign")
    db_user = os.getenv("DB_USER", "postgres")
    out = backup_dir / f"database_backup_{stamp}.sql.gz"
    cmd = compose_base(compose_file) + [
        "exec",
        "-T",
        "db",
        "sh",
        "-c",
        f'pg_dump -U "{db_user}" -d "{db_name}" --no-owner --no-privileges | gzip -c',
    ]
    with out.open("wb") as fh:
        run(cmd, stdout=fh)
    logger.info("Database backup: %s (%.2f MB)", out, out.stat().st_size / 1024 / 1024)
    return out


def backup_media(compose_file: str, backup_dir: Path, stamp: str) -> Path | None:
    out = backup_dir / f"media_backup_{stamp}.tar.gz"
    cmd = compose_base(compose_file) + [
        "exec",
        "-T",
        "backend",
        "sh",
        "-c",
        "if [ -d /app/media ]; then tar -czf - -C /app media; else exit 0; fi",
    ]
    with out.open("wb") as fh:
        run(cmd, stdout=fh)
    if out.stat().st_size == 0:
        logger.warning("Media volume empty or missing; skipping archive")
        out.unlink(missing_ok=True)
        return None
    logger.info("Media backup: %s (%.2f MB)", out, out.stat().st_size / 1024 / 1024)
    return out


def write_manifest(backup_dir: Path, stamp: str, files: list[Path]) -> Path:
    manifest = {
        "timestamp": stamp,
        "date": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "files": [
            {"name": p.name, "size": p.stat().st_size, "path": str(p)}
            for p in files
            if p
        ],
    }
    path = backup_dir / f"backup_manifest_{stamp}.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return path


def upload_s3(file_path: Path) -> bool:
    bucket = os.getenv("S3_BACKUP_BUCKET") or os.getenv("BACKUP_S3_BUCKET")
    if not bucket:
        logger.error("S3_BACKUP_BUCKET not set")
        return False
    try:
        import boto3
    except ImportError:
        logger.error("boto3 required for S3 uploads: pip install boto3")
        return False
    region = os.getenv("S3_BACKUP_REGION") or os.getenv("BACKUP_S3_REGION", "us-east-1")
    key = f"backups/{datetime.datetime.now().year}/{datetime.datetime.now().month:02d}/{file_path.name}"
    client = boto3.client("s3", region_name=region)
    client.upload_file(
        str(file_path),
        bucket,
        key,
        ExtraArgs={"ServerSideEncryption": "AES256", "StorageClass": "STANDARD_IA"},
    )
    logger.info("Uploaded s3://%s/%s", bucket, key)
    return True


def cleanup(backup_dir: Path, keep: int) -> None:
    files = sorted(
        list(backup_dir.glob("database_backup_*.sql.gz"))
        + list(backup_dir.glob("media_backup_*.tar.gz")),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for old in files[keep:]:
        logger.info("Removing old backup %s", old)
        old.unlink(missing_ok=True)


def main() -> int:
    load_dotenv(ROOT / ".env")
    parser = argparse.ArgumentParser(description="AI Design Tool Docker backup")
    parser.add_argument("--type", choices=["database", "media", "full"], default="full")
    parser.add_argument("--destination", choices=["local", "s3"], default="local")
    parser.add_argument(
        "--compose-file",
        default=os.getenv("COMPOSE_FILE", "docker-compose.yml"),
        help="Compose file relative to repo root",
    )
    parser.add_argument(
        "--backup-dir",
        default=str(DEFAULT_BACKUP_DIR),
        help="Local backup directory",
    )
    parser.add_argument("--keep", type=int, default=int(os.getenv("BACKUP_RETENTION_DAILY", "30")))
    args = parser.parse_args()

    backup_dir = Path(args.backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    created: list[Path] = []

    try:
        if args.type in ("database", "full"):
            created.append(backup_database(args.compose_file, backup_dir, stamp))
        if args.type in ("media", "full"):
            media = backup_media(args.compose_file, backup_dir, stamp)
            if media:
                created.append(media)
        created.append(write_manifest(backup_dir, stamp, created))

        if args.destination == "s3":
            for path in created:
                upload_s3(path)

        cleanup(backup_dir, args.keep)
        logger.info("Backup completed (%d file(s))", len(created))
        return 0
    except subprocess.CalledProcessError as exc:
        logger.error("Backup command failed: %s", exc)
        return 1
    except Exception as exc:
        logger.error("Backup failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
