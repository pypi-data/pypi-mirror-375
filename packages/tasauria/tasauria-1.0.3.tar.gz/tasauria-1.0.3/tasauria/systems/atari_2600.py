# -*- coding: utf-8 -*-

"""
tasauria.systems.atari_2600
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Classes and functions related to the Atari 2600 (1977) system.

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

import dataclasses
import typing

from tasauria.types import BizHawkName, BizHawkInput, BizHawkSystemInput


ATARI_2600_SYSTEM_NAME = "A26"


@dataclasses.dataclass
class Atari2600Controller(BizHawkInput):
    """
    Encapsulation of Atari 2600 controller inputs.
    """

    up: typing.Annotated[bool, BizHawkName("Up")] = False
    down: typing.Annotated[bool, BizHawkName("Down")] = False
    left: typing.Annotated[bool, BizHawkName("Left")] = False
    right: typing.Annotated[bool, BizHawkName("Right")] = False
    button: typing.Annotated[bool, BizHawkName("Button")] = False


@dataclasses.dataclass
class Atari2600Input(BizHawkSystemInput):
    reset: typing.Annotated[bool, BizHawkName("Reset")] = False
    select: typing.Annotated[bool, BizHawkName("Select")] = False
    power: typing.Annotated[bool, BizHawkName("Power")] = False
    left_difficulty: typing.Annotated[bool, BizHawkName("Toggle Left Difficulty")] = False
    right_difficulty: typing.Annotated[bool, BizHawkName("Toggle Right Difficulty")] = False

    @staticmethod
    def get_controller_type() -> typing.Type[BizHawkInput]:
        return Atari2600Controller

    @staticmethod
    def get_max_controller_count() -> int:
        return 2
