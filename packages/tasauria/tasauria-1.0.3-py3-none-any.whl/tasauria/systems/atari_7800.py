# -*- coding: utf-8 -*-

"""
tasauria.systems.atari_7800
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Classes and functions related to the Atari 7800 (1986) system.

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

import dataclasses
import typing

from tasauria.types import BizHawkName, BizHawkInput, BizHawkSystemInput


ATARI_7800_SYSTEM_NAME = "A78"


@dataclasses.dataclass
class Atari7800Controller(BizHawkInput):
    """
    Encapsulation of Atari 7800 controller inputs.
    """

    up: typing.Annotated[bool, BizHawkName("Up")] = False
    down: typing.Annotated[bool, BizHawkName("Down")] = False
    left: typing.Annotated[bool, BizHawkName("Left")] = False
    right: typing.Annotated[bool, BizHawkName("Right")] = False
    trigger: typing.Annotated[bool, BizHawkName("Trigger")] = False
    trigger_2: typing.Annotated[bool, BizHawkName("Trigger 2")] = False


@dataclasses.dataclass
class Atari7800Input(BizHawkSystemInput):
    power: typing.Annotated[bool, BizHawkName("Power")] = False
    reset: typing.Annotated[bool, BizHawkName("Reset")] = False
    select: typing.Annotated[bool, BizHawkName("Select")] = False
    bw: typing.Annotated[bool, BizHawkName("BW")] = False
    left_difficulty: typing.Annotated[bool, BizHawkName("Toggle Left Difficulty")] = False
    right_difficulty: typing.Annotated[bool, BizHawkName("Toggle Right Difficulty")] = False
    pause: typing.Annotated[bool, BizHawkName("Pause")] = False

    @staticmethod
    def get_controller_type() -> typing.Type[BizHawkInput]:
        return Atari7800Controller

    @staticmethod
    def get_max_controller_count() -> int:
        return 2
