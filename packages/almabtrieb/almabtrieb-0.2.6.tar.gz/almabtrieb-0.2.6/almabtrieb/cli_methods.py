import json

from almabtrieb import Almabtrieb


async def list_incoming(connection: Almabtrieb):
    async with connection:
        async for msg in connection.incoming():
            print(json.dumps(msg, indent=2))


async def list_outgoing(connection: Almabtrieb):
    async with connection:
        async for msg in connection.outgoing():
            print(json.dumps(msg, indent=2))


async def print_info(connection: Almabtrieb):
    async with connection:
        info = await connection.info()

        print("Base URLs: " + ", ".join(info.base_urls))
        print()

        print("Method information:".upper())
        print()
        for mi in info.method_information:
            print(f"{mi.routing_key + ':':<30} {mi.module}")
            print(f"   {mi.description}")
            print()

        print("Actors:".upper())
        for actor in info.actors:
            print(f"{actor.name + ':':<30} {actor.id}")
        print()


async def handle_trigger(connection: Almabtrieb, method: str, data: dict):
    async with connection:
        await connection.trigger(method, data)


async def handle_fetch(connection: Almabtrieb, actor_id: str, object_id: str):
    async with connection:
        result = await connection.fetch(actor_id, object_id)

        print(json.dumps(result.data, indent=2))


async def handle_create_actor(
    connection: Almabtrieb,
    base_url: str,
    preferred_username: str | None,
    automatically_accept_followers: bool | None,
    name: str | None,
    profile: dict,
):
    async with connection:
        result = await connection.create_actor(
            base_url,
            preferred_username=preferred_username,
            automatically_accept_followers=automatically_accept_followers,
            profile=profile,
            name=name,
        )

        print(json.dumps(result, indent=2))
