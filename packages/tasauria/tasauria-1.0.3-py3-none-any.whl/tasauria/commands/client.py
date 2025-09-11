# -*- coding: utf-8 -*-

"""
tasauria.commands.client
~~~~~~~~~~~~~~~~~~~~~~~~~

Client-related commands.

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

import dataclasses
import typing

from tasauria.commands import Command, NoArguments


class ClientFrameStatusServerOutput(typing.TypedDict):
    cycleCount: int
    frameCount: int
    lagCount: int
    lagged: bool


@dataclasses.dataclass
class FrameStatus:
    cycle_count: int
    frame_count: int
    lag_count: int
    is_lagged: bool


class ClientFrameStatusCommand(Command[NoArguments, NoArguments, ClientFrameStatusServerOutput, FrameStatus]):
    @staticmethod
    def marshal_input(
        **kwargs: typing.Any,
    ) -> typing.Tuple[str, NoArguments]:
        return (
            "/client/framestatus",
            {}
        )

    @staticmethod
    def unmarshal_output(
        payload: ClientFrameStatusServerOutput,
        **kwargs: typing.Any
    ) -> FrameStatus:
        return FrameStatus(
            cycle_count=payload["cycleCount"],
            frame_count=payload["frameCount"],
            lag_count=payload["lagCount"],
            is_lagged=payload["lagged"]
        )


class ClientFrameAdvanceInput(typing.TypedDict):
    unpause: bool


class ClientFrameAdvanceCommand(Command[ClientFrameAdvanceInput, ClientFrameAdvanceInput, ClientFrameStatusServerOutput, FrameStatus]):
    @staticmethod
    def marshal_input(
        **kwargs: typing.Any,
    ) -> typing.Tuple[str, ClientFrameAdvanceInput]:
        return (
            "/client/frameadvance",
            {
                "unpause": kwargs.get("unpause", None)
            }
        )

    @staticmethod
    def unmarshal_output(
        payload: ClientFrameStatusServerOutput,
        **kwargs: typing.Any
    ) -> FrameStatus:
        return FrameStatus(
            cycle_count=payload["cycleCount"],
            frame_count=payload["frameCount"],
            lag_count=payload["lagCount"],
            is_lagged=payload["lagged"]
        )


class ClientGameServerOutput(typing.TypedDict):
    loaded: bool
    name: str
    system: str
    boardType: str
    region: str
    displayType: str
    hash: str
    inDatabase: bool
    databaseStatus: str
    databaseStatusBad: bool
    gameOptions: typing.Dict[str, typing.Optional[str]]


@dataclasses.dataclass
class GameInfo:
    loaded: bool
    name: str
    system: str
    board_type: str
    region: str
    display_type: str
    hash: str
    in_database: bool
    database_status: str
    database_status_bad: bool
    game_options: typing.Dict[str, typing.Optional[str]]


class ClientGameCommand(Command[NoArguments, NoArguments, ClientGameServerOutput, GameInfo]):
    @staticmethod
    def marshal_input(
        **kwargs: typing.Any,
    ) -> typing.Tuple[str, NoArguments]:
        return (
            "/client/game",
            {}
        )

    @staticmethod
    def unmarshal_output(
        payload: ClientGameServerOutput,
        **kwargs: typing.Any
    ) -> GameInfo:
        return GameInfo(
            loaded=payload["loaded"],
            name=payload["name"],
            system=payload["system"],
            board_type=payload["boardType"],
            region=payload["region"],
            display_type=payload["displayType"],
            hash=payload["hash"],
            in_database=payload["inDatabase"],
            database_status=payload["databaseStatus"],
            database_status_bad=payload["databaseStatusBad"],
            game_options=payload["gameOptions"],
        )
