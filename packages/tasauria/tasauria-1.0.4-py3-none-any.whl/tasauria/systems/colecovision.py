# -*- coding: utf-8 -*-

"""
tasauria.systems.colecovision
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Classes and functions related to the ColecoVision (1982) system.

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

import dataclasses
import typing

from tasauria.types import BizHawkName, BizHawkInput, BizHawkSystemInput


COLECOVISION_SYSTEM_NAME = "Coleco"


@dataclasses.dataclass
class ColecoVisionController(BizHawkInput):
    """
    Encapsulation of ColecoVision controller inputs.
    """

    up: typing.Annotated[bool, BizHawkName("Up")] = False
    down: typing.Annotated[bool, BizHawkName("Down")] = False
    left: typing.Annotated[bool, BizHawkName("Left")] = False
    right: typing.Annotated[bool, BizHawkName("Right")] = False
    l_button: typing.Annotated[bool, BizHawkName("L")] = False
    r_button: typing.Annotated[bool, BizHawkName("R")] = False
    key_0: typing.Annotated[bool, BizHawkName("Key 0")] = False
    key_1: typing.Annotated[bool, BizHawkName("Key 1")] = False
    key_2: typing.Annotated[bool, BizHawkName("Key 2")] = False
    key_3: typing.Annotated[bool, BizHawkName("Key 3")] = False
    key_4: typing.Annotated[bool, BizHawkName("Key 4")] = False
    key_5: typing.Annotated[bool, BizHawkName("Key 5")] = False
    key_6: typing.Annotated[bool, BizHawkName("Key 6")] = False
    key_7: typing.Annotated[bool, BizHawkName("Key 7")] = False
    key_8: typing.Annotated[bool, BizHawkName("Key 8")] = False
    key_9: typing.Annotated[bool, BizHawkName("Key 9")] = False
    key_pound: typing.Annotated[bool, BizHawkName("Pound")] = False
    key_star: typing.Annotated[bool, BizHawkName("Star")] = False


@dataclasses.dataclass
class ColecoVisionInput(BizHawkSystemInput):
    power: typing.Annotated[bool, BizHawkName("Power")] = False
    reset: typing.Annotated[bool, BizHawkName("Reset")] = False

    @staticmethod
    def get_controller_type() -> typing.Type[BizHawkInput]:
        return ColecoVisionController

    @staticmethod
    def get_max_controller_count() -> int:
        return 2
