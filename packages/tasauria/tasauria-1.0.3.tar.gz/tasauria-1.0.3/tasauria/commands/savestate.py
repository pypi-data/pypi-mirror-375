# -*- coding: utf-8 -*-

"""
tasauria.commands.savestate
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Savestate-related commands.

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

import typing

from tasauria.commands import Command


class SavestateSaveSlotInput(typing.TypedDict):
    slot: int
    suppress_osd: bool


class SavestateSaveSlotServerInput(typing.TypedDict):
    slot: int
    suppressOSD: bool


class SavestateSaveSlotServerOutput(typing.TypedDict):
    success: bool


class SavestateSaveSlotCommand(Command[SavestateSaveSlotInput, SavestateSaveSlotServerInput, SavestateSaveSlotServerOutput, bool]):
    @staticmethod
    def marshal_input(
        **kwargs: typing.Any,
    ) -> typing.Tuple[str, SavestateSaveSlotServerInput]:
        return (
            "/savestate/saveslot",
            {
                "slot": kwargs.get("slot", 0),
                "suppressOSD": kwargs.get("suppress_osd", False),
            }
        )

    @staticmethod
    def unmarshal_output(
        payload: SavestateSaveSlotServerOutput,
        **kwargs: typing.Any
    ) -> bool:
        return payload["success"]


class SavestateLoadSlotCommand(Command[SavestateSaveSlotInput, SavestateSaveSlotServerInput, SavestateSaveSlotServerOutput, bool]):
    @staticmethod
    def marshal_input(
        **kwargs: typing.Any,
    ) -> typing.Tuple[str, SavestateSaveSlotServerInput]:
        return (
            "/savestate/loadslot",
            {
                "slot": kwargs.get("slot", 0),
                "suppressOSD": kwargs.get("suppress_osd", False),
            }
        )

    @staticmethod
    def unmarshal_output(
        payload: SavestateSaveSlotServerOutput,
        **kwargs: typing.Any
    ) -> bool:
        return payload["success"]
