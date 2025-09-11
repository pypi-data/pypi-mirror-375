# -*- coding: utf-8 -*-

"""
tasauria.systems.intellivision
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Classes and functions related to the Mattel Intellivision (1979) system.

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

import dataclasses
import typing

from tasauria.types import BizHawkName, BizHawkInput, BizHawkSystemInput


INTELLIVISION_SYSTEM_NAME = "INTV"


@dataclasses.dataclass
class IntellivisionController(BizHawkInput):
    """
    Encapsulation of Intellivision controller inputs.
    """

    l_button: typing.Annotated[bool, BizHawkName("L")] = False
    r_button: typing.Annotated[bool, BizHawkName("R")] = False
    top_button: typing.Annotated[bool, BizHawkName("Top")] = False
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
    enter: typing.Annotated[bool, BizHawkName("Enter")] = False
    clear: typing.Annotated[bool, BizHawkName("Clear")] = False
    disc_x: typing.Annotated[int, BizHawkName("Disc X")] = 0
    disc_y: typing.Annotated[int, BizHawkName("Disc Y")] = 0


@dataclasses.dataclass
class IntellivisionInput(BizHawkSystemInput):
    power: typing.Annotated[bool, BizHawkName("Power")] = False
    reset: typing.Annotated[bool, BizHawkName("Reset")] = False

    @staticmethod
    def get_controller_type() -> typing.Type[BizHawkInput]:
        return IntellivisionController

    @staticmethod
    def get_max_controller_count() -> int:
        return 2
