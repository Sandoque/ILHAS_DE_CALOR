"""
Command line entrypoint for ETL module.

Usage:
    python -m etl.pipeline.cli run-full              # Run full INMET ETL for all years
    python -m etl.pipeline.cli run-inmet             # Run full INMET ETL for standard years
    python -m etl.pipeline.cli run-inmet --year 2024 2023  # Run specific years
    python -m etl.pipeline.cli run-inc --year 2024   # Run incremental ETL
    python -m etl.pipeline.cli run-mapbiomas         # Run MapBiomas land cover ETL
"""
from __future__ import annotations

import argparse

from etl.pipeline.run_full_pipeline import run_full
from etl.pipeline.run_incremental import run_incremental
from etl.utils.logger import get_logger

logger = get_logger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ETL runner for Observatório Estadual de Ilhas de Calor – PE",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Full pipeline (all years)
    subparsers.add_parser(
        "run-full",
        help="Run full INMET ETL for all years (1961-2024)",
    )

    # INMET pipeline (with year selection)
    inmet_parser = subparsers.add_parser(
        "run-inmet",
        help="Run INMET climate ETL (specify years or default range)",
    )
    inmet_parser.add_argument(
        "--year",
        type=int,
        nargs="+",
        help="Year(s) to process (default: 2010-2024)",
    )

    # Incremental pipeline
    inc_parser = subparsers.add_parser(
        "run-inc",
        help="Run incremental INMET ETL (detect missing years)",
    )
    inc_parser.add_argument(
        "--year",
        type=int,
        help="Specific year to process",
    )

    # MapBiomas pipeline
    subparsers.add_parser(
        "run-mapbiomas",
        help="Run MapBiomas land cover ETL (aux_cobertura_vegetal_pe)",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "run-full":
        logger.info("Running full INMET ETL pipeline (all years)")
        run_full()
    
    elif args.command == "run-inmet":
        if args.year:
            logger.info("Running INMET ETL for years: %s", args.year)
            run_full(years=args.year)
        else:
            logger.info("Running INMET ETL for default years (2010-2024)")
            run_full(years=list(range(2010, 2025)))
    
    elif args.command == "run-inc":
        logger.info("Running incremental INMET ETL")
        run_incremental(args.year)
    
    elif args.command == "run-mapbiomas":
        logger.info("Running MapBiomas land cover ETL")
        from etl.mapbiomas.run_mapbiomas_pipeline import run_mapbiomas

        run_mapbiomas()
    
    else:  # pragma: no cover
        parser.print_help()


if __name__ == "__main__":  # pragma: no cover
    main()
