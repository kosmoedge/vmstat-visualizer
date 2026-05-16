"""CLI command for exporting parsed vmstat data to JSON/CSV."""

import click
from vmstat_visualizer.parser.parser import Parser
from vmstat_visualizer.exporters import export_ndjson, export_csv


@click.command("export", no_args_is_help=True)
@click.argument("file", type=click.Path(exists=True))
@click.option(
    "--to",
    "fmt",
    type=click.Choice(["json", "csv"], case_sensitive=False),
    required=True,
    help="Output format: json (NDJSON) or csv.",
)
@click.option(
    "-o",
    "--output-file",
    default=None,
    help="Write output to a file instead of stdout.",
)
def export(file, fmt, output_file):
    """Export parsed vmstat data to JSON or CSV format."""
    parser = Parser(file)
    parser.parse()

    if not parser.timeseries:
        click.echo("No data found in file.", err=True)
        raise SystemExit(1)

    if fmt == "json":
        result = export_ndjson(parser.timeseries)
    else:
        result = export_csv(parser.timeseries)

    if output_file:
        with open(output_file, "w") as f:
            f.write(result)
        click.echo(f">>> Exported {len(parser.timeseries)} entries to {output_file}")
    else:
        click.echo(result)
