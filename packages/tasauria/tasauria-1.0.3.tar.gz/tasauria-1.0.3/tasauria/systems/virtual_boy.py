# -*- coding: utf-8 -*-

"""
tasauria.systems.virtual_boy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Classes and functions related to the Nintendo Virtual Boy (1995) system.

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

import dataclasses
import typing

from tasauria.types import BizHawkName, BizHawkInput, BizHawkSystemInput


VIRTUAL_BOY_SYSTEM_NAME = "VB"


@dataclasses.dataclass
class VirtualBoyController(BizHawkInput):
    """
    Encapsulation of Nintendo Virtual Boy controller inputs.
    """

    l_up: typing.Annotated[bool, BizHawkName("L_Up")] = False
    l_down: typing.Annotated[bool, BizHawkName("L_Down")] = False
    l_left: typing.Annotated[bool, BizHawkName("L_Left")] = False
    l_right: typing.Annotated[bool, BizHawkName("L_Right")] = False
    select_button: typing.Annotated[bool, BizHawkName("Select")] = False
    start_button: typing.Annotated[bool, BizHawkName("Start")] = False
    b_button: typing.Annotated[bool, BizHawkName("B")] = False
    a_button: typing.Annotated[bool, BizHawkName("A")] = False
    r_up: typing.Annotated[bool, BizHawkName("R_Up")] = False
    r_down: typing.Annotated[bool, BizHawkName("R_Down")] = False
    r_left: typing.Annotated[bool, BizHawkName("R_Left")] = False
    r_right: typing.Annotated[bool, BizHawkName("R_Right")] = False
    l_button: typing.Annotated[bool, BizHawkName("L")] = False
    r_button: typing.Annotated[bool, BizHawkName("R")] = False


@dataclasses.dataclass
class VirtualBoyInput(BizHawkSystemInput):
    power: typing.Annotated[bool, BizHawkName("Power")] = False
    reset: typing.Annotated[bool, BizHawkName("Reset")] = False

    battery_voltage_normal: typing.Annotated[bool, BizHawkName("P2 Battery Voltage: Set Normal")] = False
    battery_voltage_low: typing.Annotated[bool, BizHawkName("P2 Battery Voltage: Set Low")] = False

    @staticmethod
    def get_controller_type() -> typing.Type[BizHawkInput]:
        return VirtualBoyController

    @staticmethod
    def get_max_controller_count() -> int:
        return 1
