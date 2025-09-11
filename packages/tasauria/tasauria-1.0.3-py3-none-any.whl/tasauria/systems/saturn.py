# -*- coding: utf-8 -*-

"""
tasauria.systems.saturn
~~~~~~~~~~~~~~~~~~~~~~~~

Classes and functions related to the SEGA Saturn (1994) system.

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

import dataclasses
import typing

from tasauria.types import BizHawkName, BizHawkInput, BizHawkSystemInput


SATURN_SYSTEM_NAME = "SAT"


@dataclasses.dataclass
class SaturnController(BizHawkInput):
    """
    Encapsulation of SEGA Saturn controller inputs.
    """

    up: typing.Annotated[bool, BizHawkName("Up")] = False
    down: typing.Annotated[bool, BizHawkName("Down")] = False
    left: typing.Annotated[bool, BizHawkName("Left")] = False
    right: typing.Annotated[bool, BizHawkName("Right")] = False
    start: typing.Annotated[bool, BizHawkName("Start")] = False
    a_button: typing.Annotated[bool, BizHawkName("A")] = False
    b_button: typing.Annotated[bool, BizHawkName("B")] = False
    c_button: typing.Annotated[bool, BizHawkName("C")] = False
    x_button: typing.Annotated[bool, BizHawkName("X")] = False
    y_button: typing.Annotated[bool, BizHawkName("Y")] = False
    z_button: typing.Annotated[bool, BizHawkName("Z")] = False
    l_button: typing.Annotated[bool, BizHawkName("L")] = False
    r_button: typing.Annotated[bool, BizHawkName("R")] = False


@dataclasses.dataclass
class SaturnInput(BizHawkSystemInput):
    power: typing.Annotated[bool, BizHawkName("Power")] = False
    reset: typing.Annotated[bool, BizHawkName("Reset")] = False
    open_tray: typing.Annotated[bool, BizHawkName("Open Tray")] = False
    close_tray: typing.Annotated[bool, BizHawkName("Close Tray")] = False
    disk_index: typing.Annotated[int, BizHawkName("Disk Index")] = 0

    smpc_reset: typing.Annotated[bool, BizHawkName("P13 Smpc Reset")] = False
    stv_test: typing.Annotated[bool, BizHawkName("P13 St-V Test")] = False
    stv_service: typing.Annotated[bool, BizHawkName("P13 St-V Service")] = False
    stv_pause: typing.Annotated[bool, BizHawkName("P13 St-V Pause")] = False

    @staticmethod
    def get_controller_type() -> typing.Type[BizHawkInput]:
        return SaturnController

    @staticmethod
    def get_max_controller_count() -> int:
        return 2
