import argparse as ap
import logging
import sys

from .query_user_interval import cli_entrypoint


main_parser = ap.ArgumentParser(
    description="`fractal-slurm-tools-user-interval` command-line interface",
    allow_abbrev=False,
)

main_parser.add_argument(
    "--fractal-backend-url",
    type=str,
    required=True,
)
main_parser.add_argument(
    "--emails",
    help=(
        "Comma-separated list of user emails, "
        "or path to a file with one email per line."
    ),
    type=str,
    required=True,
)
main_parser.add_argument(
    "--base-output-folder",
    type=str,
    help="Base folder for output files.",
    required=True,
)
main_parser.add_argument(
    "--first-month",
    help="First month to consider, in MM-YYYY format (e.g. 01-2025)",
    type=str,
    required=True,
)
main_parser.add_argument(
    "--last-month",
    help="Last month to consider, in MM-YYYY format (e.g. 12-2025)",
    type=str,
    required=True,
)
main_parser.add_argument(
    "--verbose",
    help="If set, use DEBUG as a logging level.",
    action="store_true",
)


def _parse_arguments(sys_argv: list[str] | None = None) -> ap.Namespace:
    """
    Parse `sys.argv` or custom CLI arguments.

    Arguments:
        sys_argv: If set, overrides `sys.argv` (useful for testing).
    """
    if sys_argv is None:
        sys_argv = sys.argv[:]
    args = main_parser.parse_args(sys_argv[1:])
    return args


def main():
    args = _parse_arguments()

    fmt = "%(asctime)s; %(levelname)s; %(message)s"
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format=fmt)
    else:
        logging.basicConfig(level=logging.INFO, format=fmt)
    from . import __VERSION__

    logging.debug(f"fractal-slurm-tools-user-interval version: {__VERSION__}")
    logging.debug(f"{args=}")

    cli_entrypoint(
        fractal_backend_url=args.fractal_backend_url,
        emails=args.emails,
        first_month=args.first_month,
        last_month=args.last_month,
        base_output_folder=args.base_output_folder,
    )
