"""CLI management commands."""

from __future__ import annotations

import argparse
import asyncio
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventory Platform management CLI")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("seed", help="Seed demo tenant data")

    args = parser.parse_args()
    if args.command == "seed":
        from app.cli.seed_demo import seed
        asyncio.run(seed())
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
