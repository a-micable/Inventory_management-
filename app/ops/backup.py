"""Database backup utilities."""

from __future__ import annotations

import logging
import subprocess
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


def generate_backup_filename(prefix: str = "inventory") -> str:
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_backup_{ts}.sql"


def run_pg_dump(
    *,
    host: str,
    port: int,
    user: str,
    database: str,
    output_path: Path,
    password: str | None = None,
) -> bool:
    env = {"PGPASSWORD": password} if password else {}
    cmd = [
        "pg_dump",
        "-h", host,
        "-p", str(port),
        "-U", user,
        "-d", database,
        "-f", str(output_path),
        "--no-owner",
        "--no-acl",
    ]
    try:
        subprocess.run(cmd, env=env, check=True, capture_output=True)
        logger.info("Backup created: %s", output_path)
        return True
    except subprocess.CalledProcessError as exc:
        logger.error("Backup failed: %s", exc.stderr.decode() if exc.stderr else exc)
        return False
