import click
from .plugins import get_entry_points


@click.group()
def cli():
    click.echo("In CLI")


@cli.command()
def configure():
    click.echo("Configuring")


if __name__ == '__main__':
    cli()
