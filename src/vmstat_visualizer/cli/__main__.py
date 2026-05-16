"""
Entrypoint for the vmstat-visualizer CLI.
"""
import click

import vmstat_visualizer.cli.visualizer as viz
from vmstat_visualizer.cli.export import export


@click.group(no_args_is_help=True)
def cli():
    """vmstat-visualizer is the cli for vmstat-visualizer.
    Use it to visualize vmstat logs.
    """


def main():
    "main is the entrypoint of vmstat-visualizer"
    cli.add_command(viz.visualize)
    cli.add_command(viz.compare)
    cli.add_command(export)
    cli(prog_name="vmstat-visualizer")


if __name__ == "__main__":
    main()
