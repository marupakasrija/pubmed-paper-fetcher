"""Command-line interface for the PubMed Paper Fetcher."""

import argparse
import logging
import sys
from typing import List, Optional

from .fetcher import PubMedFetcher


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments.

    Args:
        args: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Fetch research papers from PubMed with authors from pharmaceutical companies",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "query", help="PubMed search query (supports full PubMed query syntax)"
    )

    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")

    parser.add_argument(
        "-f",
        "--file",
        help="Output file path (CSV format). If not provided, prints to console.",
    )

    parser.add_argument(
        "-m",
        "--max-results",
        type=int,
        default=100,
        help="Maximum number of results to fetch",
    )

    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the command-line interface.

    Args:
        args: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    parsed_args = parse_args(args)

    # Configure logging
    log_level = logging.DEBUG if parsed_args.debug else logging.INFO
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)

    try:
        # Initialize fetcher
        fetcher = PubMedFetcher(debug=parsed_args.debug)

        # Fetch and process papers
        logger.info(f"Fetching papers for query: {parsed_args.query}")
        df = fetcher.fetch_and_process(
            parsed_args.query, max_results=parsed_args.max_results
        )

        # Output results
        if df.empty:
            logger.info("No papers found with non-academic authors")
            return 0

        if parsed_args.file:
            df.to_csv(parsed_args.file, index=False)
            logger.info(f"Results saved to {parsed_args.file}")
        else:
            # Print to console
            print(df.to_string(index=False))

        logger.info(f"Found {len(df)} papers with non-academic authors")
        return 0

    except Exception as e:
        logger.error(f"Error: {e}")
        if parsed_args.debug:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
