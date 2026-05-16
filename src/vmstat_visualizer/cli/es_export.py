"""CLI command for one-shot Elasticsearch export."""

import click
from vmstat_visualizer.parser.parser import Parser


@click.command("export-es", no_args_is_help=True)
@click.argument("file", type=click.Path(exists=True))
@click.option(
    "--es-url",
    default=None,
    help="Elasticsearch URL (e.g. https://localhost:9200). Not needed with --cloud-id.",
)
@click.option(
    "--es-api-key",
    default=None,
    envvar="ES_API_KEY",
    help="Elasticsearch API key. Can also be set via ES_API_KEY env var.",
)
@click.option(
    "--cloud-id",
    default=None,
    envvar="ES_CLOUD_ID",
    help="Elastic Cloud ID. Can also be set via ES_CLOUD_ID env var.",
)
@click.option(
    "--index",
    default="vmstat",
    help="Target Elasticsearch index name.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Print the bulk request body to stdout instead of sending.",
)
@click.option(
    "--no-verify-certs",
    is_flag=True,
    default=False,
    help="Disable TLS certificate verification.",
)
def export_es(file, es_url, es_api_key, cloud_id, index, dry_run,
              no_verify_certs):
    """Export parsed vmstat data to Elasticsearch in one shot.

    Requires: pip install elasticsearch
    """
    parser = Parser(file)
    parser.parse()

    if not parser.timeseries:
        click.echo("No data found in file.", err=True)
        raise SystemExit(1)

    click.echo(f">>> Parsed {len(parser.timeseries)} entries from {file}")

    if dry_run:
        from vmstat_visualizer.es_exporter import build_bulk_body
        body = build_bulk_body(parser.timeseries, index=index,
                               source_file=file)
        click.echo(body)
        return

    if not es_url and not cloud_id:
        raise click.UsageError(
            "Either --es-url or --cloud-id is required (unless --dry-run)."
        )

    from vmstat_visualizer.es_exporter import export_to_elasticsearch
    result = export_to_elasticsearch(
        parser.timeseries,
        es_url=es_url,
        api_key=es_api_key,
        cloud_id=cloud_id,
        index=index,
        source_file=file,
        verify_certs=not no_verify_certs,
    )

    click.echo(f">>> Indexed {result['indexed']} documents to '{index}'")
    if result['errors']:
        click.echo(f">>> {len(result['errors'])} errors occurred", err=True)
        for err in result['errors'][:5]:
            click.echo(f"    {err}", err=True)
