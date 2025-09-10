import click
import os
import json
import asyncio

from .cli_methods import (
    handle_create_actor,
    handle_fetch,
    handle_trigger,
    list_incoming,
    list_outgoing,
    print_info,
)

from . import Almabtrieb


@click.group
@click.option(
    "--connection_string",
    help="Connection String to use, if None the CONNECTION_STRING environment variable is used",
)
@click.pass_context
def main(ctx, connection_string: str | None):
    """Helper to inspect traffic from the cattle drive protocol"""
    ctx.ensure_object(dict)

    if connection_string is None:
        connection_string = os.environ.get("CONNECTION_STRING")

    if connection_string is None:
        print("ERROR: Need to specify connection string")
        exit(1)

    ctx.obj["connection"] = Almabtrieb.from_connection_string(connection_string)


@main.command("in")
@click.pass_context
def incoming(ctx):
    """Displays incoming messages"""
    asyncio.run(list_incoming(ctx.obj["connection"]))


@main.command("out")
@click.pass_context
def outgoing(ctx):
    """Displays outgoing messages"""
    asyncio.run(list_outgoing(ctx.obj["connection"]))


@main.command
@click.pass_context
def info(ctx):
    """Prints the information about the connection."""
    asyncio.run(print_info(ctx.obj["connection"]))


@main.command
@click.argument("method", type=str)
@click.argument("input", type=click.File("r"))
@click.pass_context
def trigger(ctx, method, input):
    """triggers the method with content input. Use - to type it in from stdin.
    Input is expected to be JSON."""
    try:
        parsed = json.loads(input.read())
    except Exception:
        print("Failed to parse json")
        exit(1)

    asyncio.run(handle_trigger(ctx.obj["connection"], method, parsed))


@main.command
@click.argument("actor_id", type=str)
@click.argument("object_id", type=str)
@click.pass_context
def fetch(ctx, actor_id, object_id):
    """Allows fetching ActivityPub objects"""
    asyncio.run(handle_fetch(ctx.obj["connection"], actor_id, object_id))


@main.command
@click.argument("base_url", type=str)
@click.option("--username", help="Specify the preferred username")
@click.option("--auto_follow", help="automatically accept followers")
@click.option("--name", help="internal name of the actor")
@click.option("--profile", type=click.File("r"))
@click.pass_context
def create(ctx, base_url, username, auto_follow, name, profile):
    """Allows one to create an actor"""
    if profile:
        parsed_profile = json.loads(profile.read())
    else:
        parsed_profile = {}

    asyncio.run(
        handle_create_actor(
            ctx.obj["connection"],
            base_url=base_url,
            preferred_username=username,
            automatically_accept_followers=auto_follow,
            name=name,
            profile=parsed_profile,
        )
    )


if __name__ == "__main__":
    main()
