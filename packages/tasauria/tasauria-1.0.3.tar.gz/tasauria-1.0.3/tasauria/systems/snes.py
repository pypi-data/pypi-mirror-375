# -*- coding: utf-8 -*-

"""
tasauria.systems.snes
~~~~~~~~~~~~~~~~~~~~~~

Classes and functions related to the Super Nintendo Entertainment System (1990) system.

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

import dataclasses
import typing

from tasauria.types import BizHawkName, BizHawkInput, BizHawkSystemInput


SNES_SYSTEM_NAME = "SNES"


@dataclasses.dataclass
class SNESController(BizHawkInput):
    """
    Encapsulation of Super Nintendo Entertainment System controller inputs.
    """

    up: typing.Annotated[bool, BizHawkName("Up")] = False
    down: typing.Annotated[bool, BizHawkName("Down")] = False
    left: typing.Annotated[bool, BizHawkName("Left")] = False
    right: typing.Annotated[bool, BizHawkName("Right")] = False
    start_button: typing.Annotated[bool, BizHawkName("Start")] = False
    select_button: typing.Annotated[bool, BizHawkName("Select")] = False
    y_button: typing.Annotated[bool, BizHawkName("Y")] = False
    b_button: typing.Annotated[bool, BizHawkName("B")] = False
    x_button: typing.Annotated[bool, BizHawkName("X")] = False
    a_button: typing.Annotated[bool, BizHawkName("A")] = False
    l_button: typing.Annotated[bool, BizHawkName("L")] = False
    r_button: typing.Annotated[bool, BizHawkName("R")] = False


@dataclasses.dataclass
class SNESInput(BizHawkSystemInput):
    reset: typing.Annotated[bool, BizHawkName("Reset")] = False
    power: typing.Annotated[bool, BizHawkName("Power")] = False

    @staticmethod
    def get_controller_type() -> typing.Type[BizHawkInput]:
        return SNESController

    @staticmethod
    def get_max_controller_count() -> int:
        return 2
