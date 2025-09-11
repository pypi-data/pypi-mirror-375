# -*- coding: utf-8 -*-

"""
tasauria.commands.client
~~~~~~~~~~~~~~~~~~~~~~~~~

TASauria meta commands.

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

import typing

from tasauria.commands import AnyCommand, Command, NoArguments
from tasauria.exceptions import TASauriaServerError


class MetaBatchInput(typing.TypedDict):
    commands: typing.List[
        typing.Tuple[
            typing.Type[AnyCommand],
            typing.Dict[str, typing.Any]
        ]
    ]


class MetaBatchServerInput(typing.TypedDict):
    commands: typing.List[typing.Dict[str, typing.Any]]


class MetaBatchServerOutput(typing.TypedDict):
    output: typing.List[typing.Dict[str, typing.Any]]


class MetaBatchCommand(Command[MetaBatchInput, MetaBatchServerInput, MetaBatchServerOutput, typing.List[typing.Any]]):
    @staticmethod
    def marshal_input(
        **kwargs: typing.Any,
    ) -> typing.Tuple[str, MetaBatchServerInput]:
        kw: MetaBatchInput = typing.cast(MetaBatchInput, kwargs)

        commands = [c[0].marshal_input(**c[1]) for c in kw["commands"]]

        return (
            "/meta/batch",
            {
                "commands": [
                    {
                        "command": c[0],
                        **c[1]
                    } for c in commands
                ]
            }
        )

    @staticmethod
    def unmarshal_output(
        payload: MetaBatchServerOutput,
        **kwargs: typing.Any
    ) -> typing.List[typing.Any]:
        kw: MetaBatchInput = typing.cast(MetaBatchInput, kwargs)

        for output in payload["output"]:
            if "error" in output:
                raise TASauriaServerError("Some commands failed: " + output["error"])

        return [
            command.unmarshal_output(output, **args)
            for (command, args), output in zip(kw["commands"], payload['output'])
        ]


class MetaPingServerOutput(typing.TypedDict):
    pong: bool


class MetaPingCommand(Command[NoArguments, NoArguments, MetaPingServerOutput, bool]):
    @staticmethod
    def marshal_input(
        **kwargs: typing.Any,
    ) -> typing.Tuple[str, NoArguments]:
        return (
            "/meta/ping",
            {}
        )

    @staticmethod
    def unmarshal_output(
        payload: MetaPingServerOutput,
        **kwargs: typing.Any
    ) -> bool:
        return payload["pong"]
