from click_aliases import ClickAliasedGroup
from clusteroid.app import ClusteroidTUI
from textual_serve.server import Server
import click


@click.group(
    cls=ClickAliasedGroup,
    context_settings={"show_default": True},
    invoke_without_command=True
    )
@click.option("-d", "--debug", is_flag=True, help="Log level becomes debug.")
@click.version_option(package_name="clusteroid")
@click.pass_context
def cli(ctx, debug=False, database=None):
    ctx.ensure_object(dict)
    if ctx.invoked_subcommand:
        return
    ClusteroidTUI().run()


@cli.command()
@click.option("-h", "--host", type=str, help="Specify host.", default="0.0.0.0")
@click.option("-p", "--port", type=int, help="Serve on port.", default=8000)
@click.pass_context
def web(ctx, host="0.0.0.0", port=8000):
    server = Server("clusteroid", host=host, port=port)
    server.serve()

if __name__ == "__main__":
    cli()

