# -*- coding: utf-8 -*-

"""
tasauria.systems.gb
~~~~~~~~~~~~~~~~~~~~

Classes and functions related to the Nintendo Game Boy (1989) and Nintendo Game Boy Color (1998) system.

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

import dataclasses
import typing

from tasauria.types import BizHawkName, BizHawkInput


GAMEBOY_SYSTEM_NAME = "GB"
GAMEBOY_COLOR_SYSTEM_NAME = "GBC"


@dataclasses.dataclass
class GameBoyInput(BizHawkInput):
    """
    Encapsulation of Nintendo Game Boy/Game Boy Color inputs.
    """

    up: typing.Annotated[bool, BizHawkName("Up")] = False
    down: typing.Annotated[bool, BizHawkName("Down")] = False
    left: typing.Annotated[bool, BizHawkName("Left")] = False
    right: typing.Annotated[bool, BizHawkName("Right")] = False
    start_button: typing.Annotated[bool, BizHawkName("Start")] = False
    select_button: typing.Annotated[bool, BizHawkName("Select")] = False
    b_button: typing.Annotated[bool, BizHawkName("B")] = False
    a_button: typing.Annotated[bool, BizHawkName("A")] = False
    power: typing.Annotated[bool, BizHawkName("Power")] = False
