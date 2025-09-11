# -*- coding: utf-8 -*-

"""
tasauria.systems.pcfx
~~~~~~~~~~~~~~~~~~~~~~

Classes and functions related to the NEC PC-FX (1994) system.

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

import dataclasses
import typing

from tasauria.types import BizHawkName, BizHawkInput, BizHawkSystemInput


PCFX_SYSTEM_NAME = "PCFX"


@dataclasses.dataclass
class PCFXController(BizHawkInput):
    """
    Encapsulation of PCFX controller inputs.
    """

    up: typing.Annotated[bool, BizHawkName("Up")] = False
    down: typing.Annotated[bool, BizHawkName("Down")] = False
    left: typing.Annotated[bool, BizHawkName("Left")] = False
    right: typing.Annotated[bool, BizHawkName("Right")] = False
    select: typing.Annotated[bool, BizHawkName("Select")] = False
    run: typing.Annotated[bool, BizHawkName("Run")] = False
    iv: typing.Annotated[bool, BizHawkName("IV")] = False
    v: typing.Annotated[bool, BizHawkName("V")] = False
    vi: typing.Annotated[bool, BizHawkName("VI")] = False
    iii: typing.Annotated[bool, BizHawkName("III")] = False
    ii: typing.Annotated[bool, BizHawkName("II")] = False
    i: typing.Annotated[bool, BizHawkName("I")] = False
    mode_1_a: typing.Annotated[bool, BizHawkName("Mode 1: Set A")] = False
    mode_1_b: typing.Annotated[bool, BizHawkName("Mode 1: Set B")] = False
    mode_2_a: typing.Annotated[bool, BizHawkName("Mode 2: Set A")] = False
    mode_2_b: typing.Annotated[bool, BizHawkName("Mode 2: Set B")] = False


@dataclasses.dataclass
class PCFXInput(BizHawkSystemInput):
    power: typing.Annotated[bool, BizHawkName("Power")] = False
    reset: typing.Annotated[bool, BizHawkName("Reset")] = False
    open_tray: typing.Annotated[bool, BizHawkName("Open Tray")] = False
    close_tray: typing.Annotated[bool, BizHawkName("Close Tray")] = False
    disk_index: typing.Annotated[int, BizHawkName("Disk Index")] = 0

    @staticmethod
    def get_controller_type() -> typing.Type[BizHawkInput]:
        return PCFXController

    @staticmethod
    def get_max_controller_count() -> int:
        return 2
