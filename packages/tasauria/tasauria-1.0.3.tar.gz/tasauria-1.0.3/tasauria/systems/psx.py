# -*- coding: utf-8 -*-

"""
tasauria.systems.psx
~~~~~~~~~~~~~~~~~~~~~

Classes and functions related to the Sony PlayStation (1994) system.

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

import dataclasses
import typing

from tasauria.types import BizHawkName, BizHawkInput, BizHawkSystemInput


PLAYSTATION_SYSTEM_NAME = "PSX"


@dataclasses.dataclass
class PlayStationController(BizHawkInput):
    """
    Encapsulation of Sony PlayStation controller inputs.
    """

    dpad_up: typing.Annotated[bool, BizHawkName("D-Pad Up")] = False
    dpad_down: typing.Annotated[bool, BizHawkName("D-Pad Down")] = False
    dpad_left: typing.Annotated[bool, BizHawkName("D-Pad Left")] = False
    dpad_right: typing.Annotated[bool, BizHawkName("D-Pad Right")] = False
    select: typing.Annotated[bool, BizHawkName("Select")] = False
    start: typing.Annotated[bool, BizHawkName("Start")] = False
    triangle: typing.Annotated[bool, BizHawkName("△")] = False
    cross: typing.Annotated[bool, BizHawkName("X")] = False
    square: typing.Annotated[bool, BizHawkName("□")] = False
    circle: typing.Annotated[bool, BizHawkName("○")] = False
    l1: typing.Annotated[bool, BizHawkName("L1")] = False
    l2: typing.Annotated[bool, BizHawkName("L2")] = False
    r1: typing.Annotated[bool, BizHawkName("R1")] = False
    r2: typing.Annotated[bool, BizHawkName("R2")] = False
    l3: typing.Annotated[bool, BizHawkName("Left Stick, Button")] = False
    r3: typing.Annotated[bool, BizHawkName("Right Stick, Button")] = False
    analog: typing.Annotated[bool, BizHawkName("Analog")] = False
    left_stick_y: typing.Annotated[int, BizHawkName("Left Stick Up / Down")] = 128
    left_stick_x: typing.Annotated[int, BizHawkName("Left Stick Left / Right")] = 128
    right_stick_y: typing.Annotated[int, BizHawkName("Right Stick Up / Down")] = 128
    right_stick_x: typing.Annotated[int, BizHawkName("Right Stick Left / Right")] = 128


@dataclasses.dataclass
class PlayStationInput(BizHawkSystemInput):
    power: typing.Annotated[bool, BizHawkName("Power")] = False
    reset: typing.Annotated[bool, BizHawkName("Reset")] = False
    open_tray: typing.Annotated[bool, BizHawkName("Open Tray")] = False
    close_tray: typing.Annotated[bool, BizHawkName("Close Tray")] = False
    disk_index: typing.Annotated[int, BizHawkName("Disk Index")] = 0

    @staticmethod
    def get_controller_type() -> typing.Type[BizHawkInput]:
        return PlayStationController

    @staticmethod
    def get_max_controller_count() -> int:
        return 8
