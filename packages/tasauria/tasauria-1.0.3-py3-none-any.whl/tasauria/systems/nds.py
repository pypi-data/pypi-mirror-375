# -*- coding: utf-8 -*-

"""
tasauria.systems.nds
~~~~~~~~~~~~~~~~~~~~~

Classes and functions related to the Nintendo DS (2004) system.

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

import dataclasses
import typing

from tasauria.types import BizHawkName, BizHawkInput


NINTENDO_DS_SYSTEM_NAME = "NDS"


@dataclasses.dataclass
class NintendoDSInput(BizHawkInput):
    """
    Encapsulation of Nintendo DS inputs.
    """

    up: typing.Annotated[bool, BizHawkName("Up")] = False
    down: typing.Annotated[bool, BizHawkName("Down")] = False
    left: typing.Annotated[bool, BizHawkName("Left")] = False
    right: typing.Annotated[bool, BizHawkName("Right")] = False
    start_button: typing.Annotated[bool, BizHawkName("Start")] = False
    select_button: typing.Annotated[bool, BizHawkName("Select")] = False
    b_button: typing.Annotated[bool, BizHawkName("B")] = False
    a_button: typing.Annotated[bool, BizHawkName("A")] = False
    y_button: typing.Annotated[bool, BizHawkName("Y")] = False
    x_button: typing.Annotated[bool, BizHawkName("X")] = False
    l_button: typing.Annotated[bool, BizHawkName("L")] = False
    r_button: typing.Annotated[bool, BizHawkName("R")] = False
    lid_open: typing.Annotated[bool, BizHawkName("LidOpen")] = False
    lid_close: typing.Annotated[bool, BizHawkName("LidClose")] = False
    touch: typing.Annotated[bool, BizHawkName("Touch")] = False
    microphone: typing.Annotated[bool, BizHawkName("Microphone")] = False
    power: typing.Annotated[bool, BizHawkName("Power")] = False
    touch_x: typing.Annotated[int, BizHawkName("Touch X")] = 0
    touch_y: typing.Annotated[int, BizHawkName("Touch Y")] = 0
    mic_volume: typing.Annotated[int, BizHawkName("Mic Volume")] = 0
    gba_light_sensor: typing.Annotated[int, BizHawkName("GBA Light Sensor")] = 0
