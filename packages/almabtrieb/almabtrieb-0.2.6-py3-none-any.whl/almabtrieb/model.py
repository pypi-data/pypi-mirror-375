"""
Data models used in communication with the Cattle Drive protocol

"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ActorInformation(BaseModel):
    """Information about an actor"""

    id: str = Field(
        examples=["http://host.example/actor/1"],
        description="The id of the actor",
    )

    name: str = Field(
        examples=["Alice"],
        description="The internal name of the actor",
    )


class NameAndVersion(BaseModel):
    """Name and version information"""

    name: str = Field(
        examples=["cattle_grid", "CattleDrive"],
        description="""Name of the server or protocol""",
    )

    version: str = Field(
        examples=["3.1.4"],
        description="""Version of the server or protocol""",
    )


class MethodInformationModel(BaseModel):
    """cattle_grid allows to define methods on the
    exchange through extensions. This class contains
    a description of them"""

    routing_key: str = Field(
        examples=["send_message"],
        description="""Name of the method""",
    )

    module: str = Field(
        examples=["cattle_grid"],
        description="""Module the extension was imported from. This is cattle_grid for build-in methods""",
    )

    description: str | None = Field(
        default=None,
        examples=["Send a message as the actor"],
        description="""Description of the method""",
    )


class InformationResponse(BaseModel):
    """Response for the information request"""

    actors: List[ActorInformation] = Field(
        examples=[
            [
                ActorInformation(id="http://host.example/actor/1", name="Alice"),
                ActorInformation(id="http://host.example/actor/2", name="Bob"),
            ]
        ],
        description="""Actors of the account on the server""",
    )

    base_urls: List[str] = Field(
        examples=[["http://host.example"]],
        alias="baseUrls",
        description="""The base urls of the server""",
    )

    method_information: List[MethodInformationModel] = Field(
        default_factory=list,
        examples=[
            [
                MethodInformationModel(
                    routing_key="send_message",
                    module="cattle_grid",
                    description="Send a message as the actor",
                )
            ]
        ],
        alias="methodInformation",
    )

    backend: NameAndVersion = Field(
        examples=[NameAndVersion(name="cattle_grid", version="3.1.4")],
        description="""Name and version of the backend""",
    )

    protocol: NameAndVersion = Field(
        examples=[NameAndVersion(name="CattleDrive", version="3.1.4")],
        description="""Name and version of the protocol being used""",
    )


class CreateActorRequest(BaseModel):
    """Request to create an actor"""

    base_url: str = Field(
        examples=["http://host.example"],
        serialization_alias="baseUrl",
        description="""Base url for the actor, the actor URI will be of the form `{base_url}/actor/{id}`""",
    )

    preferred_username: str | None = Field(
        None,
        examples=["alice", "bob"],
        description="""
    Add a preferred username. This name will be used in acct:username@domain and supplied to webfinger. Here domain is determine from baseUrl.
    """,
        serialization_alias="preferredUsername",
    )
    profile: Dict[str, Any] = Field(
        {},
        examples=[{"summary": "A new actor"}],
        description="""
    New profile object for the actor.
    """,
    )
    automatically_accept_followers: bool | None = Field(
        examples=[True],
        description="""
    Enables setting actors to automatically accept follow requests
    """,
        serialization_alias="automaticallyAcceptFollowers",
    )
    name: str | None = Field(
        None, examples=["Alice"], description="The name of the actor"
    )


class WithActor(BaseModel):
    """Used as base for messages requiring an actor"""

    actor: str = Field(
        examples=["http://host.example/actor/1"],
        description="""The actor performing the action""",
    )


class FetchMessage(WithActor):
    """Message to fetch an object from the Fediverse"""

    uri: str = Field(
        examples=["http://remote.example/object/1"],
        description="""The resource to fetch""",
    )


class FetchResponse(WithActor):
    """Result of a a fetch request"""

    uri: str = Field(
        examples=["http://remote.example/object/1"],
        description="""The resource that was requested""",
    )

    data: dict | None = Field(description="""The data returned for the object""")


class TriggerMessage(WithActor):
    """Message to trigger something on the ActivityExchange"""

    model_config = ConfigDict(
        extra="allow",
    )
