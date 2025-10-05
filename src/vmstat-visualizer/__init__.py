"""
parser module implements the commands for parsing
vmstat output files.
"""

import click


@click.command("parse", no_args_is_help=True)
@click.argument("file", default="vmstat.log", type=click.Path(exists=True))
@click.option(
    "-o",
    "--output-dir",
    default="./",
    help="set the output directory for plots.",
)
@click.option(
    "-k",
    "--output-kinds",
    default="png",
    help="set the output kind for conversion.",
)
def parse(
    file, output_dir, output_kinds
):
    """
    Parse a vmstat output file and generate plots.
    """
    print(f">>> Initiating parsing of file: {file}")

