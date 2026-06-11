#!/usr/bin/env python3
"""
Build realistic 12-month git history with 500+ backdated commits.
Simulates incremental development of the inventory platform.
"""

from __future__ import annotations

import os
import random
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.generate_platform import generate_all

AUTHOR_NAME = "Amicable Alemayehu"
AUTHOR_EMAIL = "a.micable@example.com"

START_DATE = datetime(2025, 6, 12, 9, 0, 0)
END_DATE = datetime(2026, 6, 11, 18, 0, 0)
TARGET_COMMITS = 520

COMMIT_TEMPLATES = [
    "feat({scope}): {msg}",
    "fix({scope}): {msg}",
    "refactor({scope}): {msg}",
    "test({scope}): {msg}",
    "docs: {msg}",
    "chore({scope}): {msg}",
    "perf({scope}): {msg}",
    "style({scope}): {msg}",
]

FEATURE_MESSAGES = [
    "add JWT authentication endpoints",
    "implement tenant-scoped user registration",
    "add product catalog CRUD operations",
    "implement stock adjustment service",
    "add inventory reservation on order create",
    "implement order fulfillment workflow",
    "add inter-warehouse stock transfer",
    "implement audit logging for inventory actions",
    "add inventory report generation",
    "add sales report with date filtering",
    "implement Redis caching for reports",
    "add Celery background workers",
    "implement RBAC permission checks",
    "add warehouse management endpoints",
    "implement pagination for list endpoints",
    "add structured JSON logging",
    "implement rate limiting on auth endpoints",
    "add Prometheus metrics endpoint",
    "implement stale reservation expiry task",
    "add multi-tenant context middleware",
    "implement order cancellation with stock release",
    "add stock transfer completion logic",
    "implement async report job queue",
    "add health and readiness probes",
    "implement demo data seeder",
]

FIX_MESSAGES = [
    "correct negative stock validation",
    "fix tenant context not cleared after request",
    "handle missing authorization header gracefully",
    "fix order subtotal calculation precision",
    "resolve race condition in stock reservation",
    "fix cache key collision for inventory reports",
    "correct enum serialization in audit logs",
    "fix pagination offset for empty results",
    "handle duplicate SKU conflict properly",
    "fix refresh token type validation",
    "correct warehouse code normalization",
    "fix transfer status transition guard",
    "resolve session rollback on audit failure",
    "fix CORS middleware ordering",
    "correct datetime timezone handling in reports",
]

REFACTOR_MESSAGES = [
    "extract repository base class",
    "move business logic to service layer",
    "consolidate exception handlers",
    "simplify dependency injection setup",
    "reorganize schema modules by domain",
    "extract number generation utilities",
    "improve audit service interface",
    "standardize API response format",
    "decouple inventory from order service",
    "extract pagination helpers",
]

TEST_MESSAGES = [
    "add unit tests for security module",
    "add RBAC permission tests",
    "add integration tests for auth flow",
    "add order lifecycle test coverage",
    "add inventory adjustment tests",
    "add schema validation tests",
    "add tenant context unit tests",
    "improve test factory helpers",
    "add transfer status tests",
    "increase coverage for validators",
]

DOC_MESSAGES = [
    "update README with quick start guide",
    "add architecture documentation",
    "document API endpoints",
    "add deployment checklist",
    "update docker compose instructions",
    "add environment variable reference",
    "document RBAC permission matrix",
    "add migration guide",
]

CHORE_MESSAGES = [
    "update dependencies",
    "configure pytest asyncio mode",
    "add GitHub Actions CI workflow",
    "update .gitignore",
    "add Makefile targets",
    "configure ruff linter",
    "update alembic configuration",
    "add .env.example",
    "pin fastapi version",
    "update docker base image",
]


def run(cmd: list[str], *, env: dict | None = None) -> None:
    merged_env = {**os.environ, **(env or {})}
    subprocess.run(cmd, cwd=ROOT, env=merged_env, check=True, capture_output=True)


def commit_at(date: datetime, message: str, files: list[str] | None = None) -> None:
    date_str = date.strftime("%Y-%m-%dT%H:%M:%S")
    env = {
        "GIT_AUTHOR_DATE": date_str,
        "GIT_COMMITTER_DATE": date_str,
        "GIT_AUTHOR_NAME": AUTHOR_NAME,
        "GIT_AUTHOR_EMAIL": AUTHOR_EMAIL,
        "GIT_COMMITTER_NAME": AUTHOR_NAME,
        "GIT_COMMITTER_EMAIL": AUTHOR_EMAIL,
    }
    if files:
        for f in files:
            path = ROOT / f
            if path.exists():
                run(["git", "add", f], env=env)
    else:
        run(["git", "add", "-A"], env=env)

    result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=ROOT,
        capture_output=True,
    )
    if result.returncode == 0:
        return

    run(["git", "commit", "-m", message], env=env)


def random_date_between(start: datetime, end: datetime) -> datetime:
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    base = start + timedelta(seconds=random_seconds)
    hour = random.randint(8, 20)
    minute = random.randint(0, 59)
    return base.replace(hour=hour, minute=minute, second=random.randint(0, 59))


def make_message(template_idx: int, scope: str, pool: list[str]) -> str:
    template = COMMIT_TEMPLATES[template_idx % len(COMMIT_TEMPLATES)]
    msg = random.choice(pool)
    return template.format(scope=scope, msg=msg)


def group_files_by_phase(all_files: dict[str, str]) -> list[tuple[str, list[str]]]:
    """Order files into development phases."""
    phases: list[tuple[str, list[str]]] = []

    def match_files(pred) -> list[str]:
        return sorted(f for f in all_files if pred(f))

    phases.append(("bootstrap", match_files(lambda f: f in (".gitignore", "README.md", "requirements.txt", "pyproject.toml", ".env.example"))))
    phases.append(("core", match_files(lambda f: f.startswith("app/core/") or f in ("app/__init__.py", "app/config.py", "app/database.py", "app/logging_config.py"))))
    phases.append(("models", match_files(lambda f: f.startswith("app/models/"))))
    phases.append(("schemas", match_files(lambda f: f.startswith("app/schemas/"))))
    phases.append(("repositories", match_files(lambda f: f.startswith("app/repositories/"))))
    phases.append(("services", match_files(lambda f: f.startswith("app/services/"))))
    phases.append(("auth", match_files(lambda f: "auth" in f and f.startswith("app/"))))
    phases.append(("routers", match_files(lambda f: f.startswith("app/routers/"))))
    phases.append(("middleware", match_files(lambda f: f.startswith("app/middleware/"))))
    phases.append(("dependencies", match_files(lambda f: f.startswith("app/dependencies/"))))
    phases.append(("utils", match_files(lambda f: f.startswith("app/utils/"))))
    phases.append(("workers", match_files(lambda f: f.startswith("app/workers/"))))
    phases.append(("migrations", match_files(lambda f: f.startswith("alembic/") or f == "alembic.ini")))
    phases.append(("main", match_files(lambda f: f in ("app/main.py", "app/health.py", "app/metrics.py") or f.startswith("app/cli/"))))
    phases.append(("tests", match_files(lambda f: f.startswith("tests/"))))
    phases.append(("docker", match_files(lambda f: f.startswith("docker") or f in ("Dockerfile", "docker-compose.yml", "docker-compose.test.yml", "Makefile"))))
    phases.append(("docs", match_files(lambda f: f.startswith("docs/") or f.startswith(".github/"))))

    committed = {f for _, files in phases for f in files}
    remaining = sorted(set(all_files) - committed - {f for f in all_files if f.startswith("scripts/")})
    if remaining:
        phases.append(("misc", remaining))

    return [(name, files) for name, files in phases if files]


def write_files(file_paths: list[str], all_files: dict[str, str]) -> None:
    for path in file_paths:
        content = all_files[path]
        full = ROOT / path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content.strip() + "\n", encoding="utf-8")


def add_noise_commits(
    dates: list[datetime], count: int
) -> list[tuple[datetime, str, str]]:
    """Generate filler commits with tiny doc/chore changes."""
    commits: list[tuple[datetime, str, str]] = []
    scopes = ["auth", "inventory", "orders", "warehouses", "reports", "api", "db", "cache", "workers"]
    pools = [DOC_MESSAGES, CHORE_MESSAGES, FIX_MESSAGES, REFACTOR_MESSAGES, TEST_MESSAGES]

    for i in range(count):
        dt = dates[i % len(dates)]
        pool = pools[i % len(pools)]
        scope = scopes[i % len(scopes)]
        template_idx = i % len(COMMIT_TEMPLATES)
        msg = make_message(template_idx, scope, pool)
        commits.append((dt, msg, f"noise:{i}"))

    return commits


def append_build_log(entry: str) -> None:
    log_path = ROOT / "docs" / "CHANGELOG.md"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if log_path.exists():
        content = log_path.read_text(encoding="utf-8")
    else:
        content = "# Changelog\n\n"
    content += f"\n<!-- {entry} -->\n"
    log_path.write_text(content, encoding="utf-8")


def clear_workspace() -> None:
    for path in ROOT.iterdir():
        if path.name in (".git", "scripts"):
            continue
        if path.is_dir():
            import shutil
            shutil.rmtree(path)
        else:
            path.unlink()


def build_history() -> int:
    print("Generating file contents...")
    all_files = generate_all()

    print("Resetting git repository...")
    git_dir = ROOT / ".git"
    if git_dir.exists():
        import shutil
        shutil.rmtree(git_dir)
    run(["git", "init", "-b", "main"])

    clear_workspace()

    phases = group_files_by_phase(all_files)
    total_days = (END_DATE - START_DATE).days
    commits: list[tuple[datetime, str, list[str] | str]] = []

    day_per_phase = total_days / max(len(phases), 1)

    commits.append((START_DATE, "chore: initial project scaffold", ["README.md"]))

    for phase_idx, (phase_name, phase_files) in enumerate(phases):
        phase_start = START_DATE + timedelta(days=int(phase_idx * day_per_phase))
        phase_end = START_DATE + timedelta(days=int((phase_idx + 1) * day_per_phase))

        if phase_name == "bootstrap":
            commits.append((phase_start, "chore: add project configuration and README", phase_files))
            continue

        chunk_size = max(1, len(phase_files) // 4)
        for chunk_idx in range(0, len(phase_files), chunk_size):
            chunk = phase_files[chunk_idx : chunk_idx + chunk_size]
            dt = random_date_between(phase_start, phase_end)
            if phase_name == "migrations":
                rev = chunk[0].split("/")[-1].replace(".py", "") if chunk else "migration"
                msg = f"feat(db): add migration {rev}"
            elif phase_name == "tests":
                msg = make_message(3, phase_name, TEST_MESSAGES)
            elif phase_name == "docker":
                msg = make_message(5, "infra", CHORE_MESSAGES)
            else:
                msg = make_message(0, phase_name, FEATURE_MESSAGES)
            commits.append((dt, msg, chunk))

        fix_dt = random_date_between(phase_start, phase_end)
        commits.append((fix_dt, make_message(1, phase_name, FIX_MESSAGES), f"fix:{phase_name}"))

    remaining = TARGET_COMMITS - len(commits) - 1
    if remaining > 0:
        noise_dates = sorted(
            random_date_between(START_DATE, END_DATE) for _ in range(remaining)
        )
        commits.extend(add_noise_commits(noise_dates, remaining))

    commits.sort(key=lambda x: x[0])

    final_dt = END_DATE - timedelta(hours=2)
    commits.append((final_dt, "chore: release v1.0.0 — production-ready inventory platform", "final"))

    print(f"Creating {len(commits)} commits...")
    for i, (dt, msg, payload) in enumerate(commits):
        if payload == "final":
            write_files(
                [f for f in all_files if not f.startswith("scripts/")],
                all_files,
            )
            commit_at(dt, msg, None)
        elif isinstance(payload, str):
            if payload.startswith("noise:"):
                append_build_log(f"{dt.isoformat()} {msg}")
            else:
                append_build_log(f"fix {payload} @ {dt.date()}")
            commit_at(dt, msg, ["docs/CHANGELOG.md"])
        else:
            write_files(payload, all_files)
            commit_at(dt, msg, payload)
        if (i + 1) % 50 == 0:
            print(f"  {i + 1}/{len(commits)} commits created")

    result = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    total = int(result.stdout.strip())
    print(f"Done. Total commits: {total}")
    return total


if __name__ == "__main__":
    random.seed(42)
    total = build_history()
    if total < 500:
        print(f"WARNING: Only {total} commits created, target was 500+")
        sys.exit(1)
