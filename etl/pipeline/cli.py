"""
Command line entrypoint for ETL module.

Usage:
    python -m etl.pipeline.cli run-full
    python -m etl.pipeline.cli run-inc --year 2024
"""
from __future__ import annotations

import argparse

from etl.pipeline.run_full_pipeline import run_full
from etl.pipeline.run_incremental import run_incremental
from etl.utils.logger import get_logger

logger = get_logger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ETL runner for Observatório Estadual de Ilhas de Calor – PE")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("run-full", help="Run full ETL for all years")

    inc_parser = subparsers.add_parser("run-inc", help="Run incremental ETL")
    inc_parser.add_argument("--year", type=int, help="Specific year to process")

    subparsers.add_parser("run-mapbiomas", help="Run MapBiomas land cover ETL")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "run-full":
        run_full()
    elif args.command == "run-inc":
        run_incremental(args.year)
    elif args.command == "run-mapbiomas":
        from etl.mapbiomas.run_mapbiomas_pipeline import run_mapbiomas

        run_mapbiomas()
    else:  # pragma: no cover
        parser.print_help()


if __name__ == "__main__":  # pragma: no cover
    main()
