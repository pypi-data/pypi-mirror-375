# -*- coding: utf-8 -*-

"""
tasauria.systems.turbografx
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Classes and functions related to the NEC TurboGrafx-16 (1987) and NEC PC Engine SuperGrafx (1989) system.

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

import dataclasses
import typing

from tasauria.types import BizHawkName, BizHawkInput, BizHawkSystemInput


TURBOGRAFX_SYSTEM_NAME = "PCE"


@dataclasses.dataclass
class TurboGrafxController(BizHawkInput):
    """
    Encapsulation of TurboGrafx/SuperGrafx controller inputs.
    """

    up: typing.Annotated[bool, BizHawkName("Up")] = False
    down: typing.Annotated[bool, BizHawkName("Down")] = False
    left: typing.Annotated[bool, BizHawkName("Left")] = False
    right: typing.Annotated[bool, BizHawkName("Right")] = False
    select: typing.Annotated[bool, BizHawkName("Select")] = False
    run: typing.Annotated[bool, BizHawkName("Run")] = False
    mode_2: typing.Annotated[bool, BizHawkName("Mode: Set 2-button")] = False
    mode_6: typing.Annotated[bool, BizHawkName("Mode: Set 6-button")] = False
    iv: typing.Annotated[bool, BizHawkName("IV")] = False
    v: typing.Annotated[bool, BizHawkName("V")] = False
    vi: typing.Annotated[bool, BizHawkName("VI")] = False
    iii: typing.Annotated[bool, BizHawkName("III")] = False
    ii: typing.Annotated[bool, BizHawkName("II")] = False
    i: typing.Annotated[bool, BizHawkName("I")] = False


@dataclasses.dataclass
class TurboGrafxInput(BizHawkSystemInput):
    power: typing.Annotated[bool, BizHawkName("Power")] = False
    reset: typing.Annotated[bool, BizHawkName("Reset")] = False

    @staticmethod
    def get_controller_type() -> typing.Type[BizHawkInput]:
        return TurboGrafxController

    @staticmethod
    def get_max_controller_count() -> int:
        return 5
