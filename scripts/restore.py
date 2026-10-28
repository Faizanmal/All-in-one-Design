#!/usr/bin/env python3
"""
Restore PostgreSQL dump created by scripts/backup.py.

Usage:
    python scripts/restore.py backups/database_backup_YYYYMMDD_HHMMSS.sql.gz --yes
"""

from __future__ import annotations

import argparse
import gzip
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def main() -> int:
    load_dotenv(ROOT / ".env")
    parser = argparse.ArgumentParser(description="Restore DB backup into compose db service")
    parser.add_argument("dump", type=Path, help="Path to .sql or .sql.gz dump")
    parser.add_argument("--compose-file", default=os.getenv("COMPOSE_FILE", "docker-compose.yml"))
    parser.add_argument("--yes", action="store_true", help="Skip confirmation")
    args = parser.parse_args()

    dump = args.dump if args.dump.is_absolute() else ROOT / args.dump
    if not dump.exists():
        print(f"File not found: {dump}", file=sys.stderr)
        return 1

    if not args.yes:
        confirm = input(f"This will overwrite database contents from {dump.name}. Type YES: ")
        if confirm.strip() != "YES":
            print("Aborted.")
            return 1

    db_name = os.getenv("DB_NAME", "aidesign")
    db_user = os.getenv("DB_USER", "postgres")
    compose = ["docker", "compose", "-f", str(ROOT / args.compose_file)]
    psql = compose + ["exec", "-T", "db", "psql", "-U", db_user, "-d", db_name]

    if dump.name.endswith(".gz"):
        with gzip.open(dump, "rb") as gz:
            data = gz.read()
        proc = subprocess.run(psql, input=data, check=False)
    else:
        with dump.open("rb") as fh:
            proc = subprocess.run(psql, stdin=fh, check=False)
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
