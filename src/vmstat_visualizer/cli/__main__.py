"""
This is the entrypoint to netcdfella app.
"""
import click

import vmstat_visualizer.cli.visualizer as viz
from vmstat_visualizer.cli.es_export import export_es


@click.group(no_args_is_help=True)
def cli():
    """vmstat-visualizer is the cli for vmstat-visualizer.
    Use it to visualize vmstat logs.
    """


def main():
    "main is the entrypoint of vmstat-visualizer"
    cli.add_command(viz.visualize)
    cli.add_command(viz.compare)
    cli.add_command(export_es)
    cli(prog_name="vmstat-visualizer")


if __name__ == "__main__":
    main()
