# -*- coding: utf-8 -*-

"""
tasauria.systems.n64
~~~~~~~~~~~~~~~~~~~~~

Classes and functions related to the Nintendo 64 (1996) system.

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

import dataclasses
import typing

from tasauria.types import BizHawkName, BizHawkInput, BizHawkSystemInput


NINTENDO_64_SYSTEM_NAME = "N64"


@dataclasses.dataclass
class Nintendo64Controller(BizHawkInput):
    """
    Encapsulation of Nintendo 64 controller inputs.
    """

    dpad_up: typing.Annotated[bool, BizHawkName("DPad U")] = False
    dpad_down: typing.Annotated[bool, BizHawkName("DPad D")] = False
    dpad_left: typing.Annotated[bool, BizHawkName("DPad L")] = False
    dpad_right: typing.Annotated[bool, BizHawkName("DPad R")] = False
    start_button: typing.Annotated[bool, BizHawkName("Start")] = False
    z_button: typing.Annotated[bool, BizHawkName("Z")] = False
    b_button: typing.Annotated[bool, BizHawkName("B")] = False
    a_button: typing.Annotated[bool, BizHawkName("A")] = False
    c_up: typing.Annotated[bool, BizHawkName("C Up")] = False
    c_down: typing.Annotated[bool, BizHawkName("C Down")] = False
    c_left: typing.Annotated[bool, BizHawkName("C Left")] = False
    c_right: typing.Annotated[bool, BizHawkName("C Right")] = False
    l_button: typing.Annotated[bool, BizHawkName("L")] = False
    r_button: typing.Annotated[bool, BizHawkName("R")] = False
    x_axis: typing.Annotated[int, BizHawkName("X Axis")] = 0
    y_axis: typing.Annotated[int, BizHawkName("Y Axis")] = 0


@dataclasses.dataclass
class Nintendo64Input(BizHawkSystemInput):
    reset: typing.Annotated[bool, BizHawkName("Reset")] = False
    power: typing.Annotated[bool, BizHawkName("Power")] = False

    @staticmethod
    def get_controller_type() -> typing.Type[BizHawkInput]:
        return Nintendo64Controller

    @staticmethod
    def get_max_controller_count() -> int:
        return 4
