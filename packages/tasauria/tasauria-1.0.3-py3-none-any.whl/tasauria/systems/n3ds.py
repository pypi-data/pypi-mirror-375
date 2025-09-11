# -*- coding: utf-8 -*-

"""
tasauria.systems.n3ds
~~~~~~~~~~~~~~~~~~~~~~

Classes and functions related to the Nintendo 3DS (2011) system.

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

import dataclasses
import typing

from tasauria.types import BizHawkName, BizHawkInput


NINTENDO_3DS_SYSTEM_NAME = "3DS"


@dataclasses.dataclass
class Nintendo3DSInput(BizHawkInput):
    """
    Encapsulation of Nintendo 3DS inputs.
    """

    a_button: typing.Annotated[bool, BizHawkName("A")] = False
    b_button: typing.Annotated[bool, BizHawkName("B")] = False
    x_button: typing.Annotated[bool, BizHawkName("X")] = False
    y_button: typing.Annotated[bool, BizHawkName("Y")] = False
    up: typing.Annotated[bool, BizHawkName("Up")] = False
    down: typing.Annotated[bool, BizHawkName("Down")] = False
    left: typing.Annotated[bool, BizHawkName("Left")] = False
    right: typing.Annotated[bool, BizHawkName("Right")] = False
    l_button: typing.Annotated[bool, BizHawkName("L")] = False
    r_button: typing.Annotated[bool, BizHawkName("R")] = False
    start_button: typing.Annotated[bool, BizHawkName("Start")] = False
    select_button: typing.Annotated[bool, BizHawkName("Select")] = False
    debug: typing.Annotated[bool, BizHawkName("Debug")] = False
    gpio14: typing.Annotated[bool, BizHawkName("GPIO14")] = False
    zl_button: typing.Annotated[bool, BizHawkName("ZL")] = False
    zr_button: typing.Annotated[bool, BizHawkName("ZR")] = False
    touch: typing.Annotated[bool, BizHawkName("Touch")] = False
    tilt: typing.Annotated[bool, BizHawkName("Tilt")] = False
    reset: typing.Annotated[bool, BizHawkName("Reset")] = False
    circle_pad_x: typing.Annotated[int, BizHawkName("Circle Pad X")] = 0
    circle_pad_y: typing.Annotated[int, BizHawkName("Circle Pad Y")] = 0
    c_stick_x: typing.Annotated[int, BizHawkName("C-Stick X")] = 0
    c_stick_y: typing.Annotated[int, BizHawkName("C-Stick Y")] = 0
    touch_x: typing.Annotated[int, BizHawkName("Touch X")] = 0
    touch_y: typing.Annotated[int, BizHawkName("Touch Y")] = 0
    tilt_x: typing.Annotated[int, BizHawkName("Tilt X")] = 0
    tilt_y: typing.Annotated[int, BizHawkName("Tilt Y")] = 0
