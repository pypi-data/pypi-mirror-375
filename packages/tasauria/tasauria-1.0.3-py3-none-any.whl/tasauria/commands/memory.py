# -*- coding: utf-8 -*-

"""
tasauria.commands.memory
~~~~~~~~~~~~~~~~~~~~~~~~~

Memory-related commands.

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

import base64
import typing

from tasauria.commands import Command


class MemoryReadIntegerInput(typing.TypedDict):
    address: int
    size: int
    signed: bool
    little: bool
    domain: typing.Optional[str]


class MemoryReadIntegerServerOutput(typing.TypedDict):
    data: int
    domain: str


class MemoryReadIntegerCommand(Command[MemoryReadIntegerInput, MemoryReadIntegerInput, MemoryReadIntegerServerOutput, int]):
    @staticmethod
    def marshal_input(
        **kwargs: typing.Any,
    ) -> typing.Tuple[str, MemoryReadIntegerInput]:
        return (
            "/memory/readinteger",
            {
                "address": kwargs.get("address", 0),
                "size": kwargs.get("size", 4),
                "signed": kwargs.get("signed", True),
                "little": kwargs.get("little", False),
                "domain": kwargs.get("domain", None)
            }
        )

    @staticmethod
    def unmarshal_output(
        payload: MemoryReadIntegerServerOutput,
        **kwargs: typing.Any
    ) -> int:
        return payload["data"]


class MemoryReadFloatInput(typing.TypedDict):
    address: int
    little: bool
    domain: typing.Optional[str]


class MemoryReadFloatServerOutput(typing.TypedDict):
    data: float
    domain: str


class MemoryReadFloatCommand(Command[MemoryReadFloatInput, MemoryReadFloatInput, MemoryReadFloatServerOutput, float]):
    @staticmethod
    def marshal_input(
        **kwargs: typing.Any,
    ) -> typing.Tuple[str, MemoryReadFloatInput]:
        return (
            "/memory/readfloat",
            {
                "address": kwargs.get("address", 0),
                "little": kwargs.get("little", False),
                "domain": kwargs.get("domain", None)
            }
        )

    @staticmethod
    def unmarshal_output(
        payload: MemoryReadFloatServerOutput,
        **kwargs: typing.Any
    ) -> float:
        return payload["data"]


class MemoryReadRangeInput(typing.TypedDict):
    address: int
    size: int
    domain: typing.Optional[str]


class MemoryReadRangeServerOutput(typing.TypedDict):
    data: str
    domain: str


class MemoryReadRangeCommand(Command[MemoryReadRangeInput, MemoryReadRangeInput, MemoryReadRangeServerOutput, bytes]):
    @staticmethod
    def marshal_input(
        **kwargs: typing.Any,
    ) -> typing.Tuple[str, MemoryReadRangeInput]:
        return (
            "/memory/readrange",
            {
                "address": kwargs.get("address", 0),
                "size": kwargs.get("size", 1),
                "domain": kwargs.get("domain", None)
            }
        )

    @staticmethod
    def unmarshal_output(
        payload: MemoryReadRangeServerOutput,
        **kwargs: typing.Any
    ) -> bytes:
        return base64.b64decode(payload["data"])


# Writes
class MemoryWriteIntegerInput(MemoryReadIntegerInput):
    data: int


class MemoryWriteIntegerCommand(Command[MemoryWriteIntegerInput, MemoryWriteIntegerInput, MemoryReadIntegerServerOutput, int]):
    @staticmethod
    def marshal_input(
        **kwargs: typing.Any,
    ) -> typing.Tuple[str, MemoryWriteIntegerInput]:
        return (
            "/memory/writeinteger",
            {
                "address": kwargs.get("address", 0),
                "size": kwargs.get("size", 4),
                "signed": kwargs.get("signed", True),
                "little": kwargs.get("little", False),
                "data": kwargs.get("data", 0),
                "domain": kwargs.get("domain", None)
            }
        )

    @staticmethod
    def unmarshal_output(
        payload: MemoryReadIntegerServerOutput,
        **kwargs: typing.Any
    ) -> int:
        return payload["data"]


class MemoryWriteFloatInput(MemoryReadFloatInput):
    data: float


class MemoryWriteFloatCommand(Command[MemoryWriteFloatInput, MemoryWriteFloatInput, MemoryReadFloatServerOutput, float]):
    @staticmethod
    def marshal_input(
        **kwargs: typing.Any,
    ) -> typing.Tuple[str, MemoryWriteFloatInput]:
        return (
            "/memory/writefloat",
            {
                "address": kwargs.get("address", 0),
                "little": kwargs.get("little", False),
                "data": kwargs.get("data", 0.0),
                "domain": kwargs.get("domain", None)
            }
        )

    @staticmethod
    def unmarshal_output(
        payload: MemoryReadFloatServerOutput,
        **kwargs: typing.Any
    ) -> float:
        return payload["data"]


class MemoryWriteRangeInput(MemoryReadRangeInput):
    data: bytes


class MemoryWriteRangeServerInput(typing.TypedDict):
    address: int
    size: int
    data: str
    domain: typing.Optional[str]


class MemoryWriteRangeCommand(Command[MemoryWriteRangeInput, MemoryWriteRangeServerInput, MemoryReadRangeServerOutput, bytes]):
    @staticmethod
    def marshal_input(
        **kwargs: typing.Any,
    ) -> typing.Tuple[str, MemoryWriteRangeServerInput]:
        return (
            "/memory/writerange",
            {
                "address": kwargs.get("address", 0),
                "size": kwargs.get("size", 1),
                "data": base64.b64encode(kwargs.get("data", b"")).decode("utf-8"),
                "domain": kwargs.get("domain", None)
            }
        )

    @staticmethod
    def unmarshal_output(
        payload: MemoryReadRangeServerOutput,
        **kwargs: typing.Any
    ) -> bytes:
        return base64.b64decode(payload["data"])
