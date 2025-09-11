# -*- coding: utf-8 -*-

"""
tasauria.systems.gba
~~~~~~~~~~~~~~~~~~~~~

Classes and functions related to the Nintendo Game Boy Advance (2001) system.

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

import dataclasses
import typing

from tasauria.types import BizHawkName, BizHawkInput


GAMEBOY_ADVANCE_SYSTEM_NAME = "GBA"


@dataclasses.dataclass
class GameBoyAdvanceInput(BizHawkInput):
    """
    Encapsulation of Nintendo Game Boy Advance inputs.
    """

    up: typing.Annotated[bool, BizHawkName("Up")] = False
    down: typing.Annotated[bool, BizHawkName("Down")] = False
    left: typing.Annotated[bool, BizHawkName("Left")] = False
    right: typing.Annotated[bool, BizHawkName("Right")] = False
    start_button: typing.Annotated[bool, BizHawkName("Start")] = False
    select_button: typing.Annotated[bool, BizHawkName("Select")] = False
    b_button: typing.Annotated[bool, BizHawkName("B")] = False
    a_button: typing.Annotated[bool, BizHawkName("A")] = False
    l_button: typing.Annotated[bool, BizHawkName("L")] = False
    r_button: typing.Annotated[bool, BizHawkName("R")] = False
    power: typing.Annotated[bool, BizHawkName("Power")] = False
    tilt_x: typing.Annotated[int, BizHawkName("Tilt X")] = 0
    tilt_y: typing.Annotated[int, BizHawkName("Tilt Y")] = 0
    tilt_z: typing.Annotated[int, BizHawkName("Tilt Z")] = 0
    light_sensor: typing.Annotated[int, BizHawkName("Light Sensor")] = 0
