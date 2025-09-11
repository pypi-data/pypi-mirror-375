# -*- coding: utf-8 -*-

"""
tasauria.commands.movie
~~~~~~~~~~~~~~~~~~~~~~~~

Movie-related commands.

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

import dataclasses
import typing

from tasauria.commands import Command, NoArguments


class MovieInfoServerOutput(typing.TypedDict):
    loaded: bool
    mode: str
    readOnly: bool
    fileName: str
    length: int
    frameRate: float
    rerecords: int


@dataclasses.dataclass
class MovieInfo:
    loaded: bool
    mode: str
    read_only: bool
    file_name: str
    length: int
    frame_rate: float
    rerecords: int


class MovieInfoCommand(Command[NoArguments, NoArguments, MovieInfoServerOutput, MovieInfo]):
    @staticmethod
    def marshal_input(
        **kwargs: typing.Any,
    ) -> typing.Tuple[str, NoArguments]:
        return (
            "/movie/info",
            {}
        )

    @staticmethod
    def unmarshal_output(
        payload: MovieInfoServerOutput,
        **kwargs: typing.Any
    ) -> MovieInfo:
        return MovieInfo(
            loaded=payload["loaded"],
            mode=payload["mode"],
            read_only=payload["readOnly"],
            file_name=payload["fileName"],
            length=payload["length"],
            frame_rate=payload["frameRate"],
            rerecords=payload["rerecords"]
        )
