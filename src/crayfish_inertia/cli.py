"""Command-line interface."""

from __future__ import annotations

import argparse

from crayfish_inertia.tasks import (
    run_all,
    run_task1_qc,
    run_task2_projection_exports,
    run_task3_realized_exports,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crayfish-inertia",
        description="Export workflow for the crayfish endemism inertia paper.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("task1", help="Create endemic cohort QC table.")
    subparsers.add_parser("task2", help="Export continental projection CSVs.")
    subparsers.add_parser("task3", help="Export realized presence CSVs.")
    subparsers.add_parser("all", help="Run Task 1, Task 2, and Task 3.")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "task1":
        run_task1_qc()
    elif args.command == "task2":
        run_task2_projection_exports()
    elif args.command == "task3":
        run_task3_realized_exports()
    elif args.command == "all":
        run_all()
    else:
        parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
