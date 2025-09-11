# -*- coding: utf-8 -*-

"""
tasauria.systems.odyssey2
~~~~~~~~~~~~~~~~~~~~~~~~~~

Classes and functions related to the Magnavox Odyssey 2 (1978) system.

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

import dataclasses
import typing

from tasauria.types import BizHawkName, BizHawkInput, BizHawkSystemInput


ODYSSEY_2_SYSTEM_NAME = "O2"


@dataclasses.dataclass
class Odyssey2Controller(BizHawkInput):
    """
    Encapsulation of Magnavox Odyssey 2 controller inputs.
    """

    up: typing.Annotated[bool, BizHawkName("Up")] = False
    down: typing.Annotated[bool, BizHawkName("Down")] = False
    left: typing.Annotated[bool, BizHawkName("Left")] = False
    right: typing.Annotated[bool, BizHawkName("Right")] = False
    f_button: typing.Annotated[bool, BizHawkName("F")] = False


@dataclasses.dataclass
class Odyssey2Input(BizHawkSystemInput):
    key_0: typing.Annotated[bool, BizHawkName("0")] = False
    key_1: typing.Annotated[bool, BizHawkName("1")] = False
    key_2: typing.Annotated[bool, BizHawkName("2")] = False
    key_3: typing.Annotated[bool, BizHawkName("3")] = False
    key_4: typing.Annotated[bool, BizHawkName("4")] = False
    key_5: typing.Annotated[bool, BizHawkName("5")] = False
    key_6: typing.Annotated[bool, BizHawkName("6")] = False
    key_7: typing.Annotated[bool, BizHawkName("7")] = False
    key_8: typing.Annotated[bool, BizHawkName("8")] = False
    key_9: typing.Annotated[bool, BizHawkName("9")] = False
    key_space: typing.Annotated[bool, BizHawkName("SPC")] = False
    key_question: typing.Annotated[bool, BizHawkName("?")] = False
    key_l: typing.Annotated[bool, BizHawkName("L")] = False
    key_p: typing.Annotated[bool, BizHawkName("P")] = False
    key_plus: typing.Annotated[bool, BizHawkName("+")] = False
    key_w: typing.Annotated[bool, BizHawkName("W")] = False
    key_e: typing.Annotated[bool, BizHawkName("E")] = False
    key_r: typing.Annotated[bool, BizHawkName("R")] = False
    key_t: typing.Annotated[bool, BizHawkName("T")] = False
    key_y: typing.Annotated[bool, BizHawkName("Y")] = False
    key_u: typing.Annotated[bool, BizHawkName("U")] = False
    key_i: typing.Annotated[bool, BizHawkName("I")] = False
    key_o: typing.Annotated[bool, BizHawkName("O")] = False
    key_q: typing.Annotated[bool, BizHawkName("Q")] = False
    key_s: typing.Annotated[bool, BizHawkName("S")] = False
    key_d: typing.Annotated[bool, BizHawkName("D")] = False
    key_f: typing.Annotated[bool, BizHawkName("F")] = False
    key_g: typing.Annotated[bool, BizHawkName("G")] = False
    key_h: typing.Annotated[bool, BizHawkName("H")] = False
    key_j: typing.Annotated[bool, BizHawkName("J")] = False
    key_k: typing.Annotated[bool, BizHawkName("K")] = False
    key_a: typing.Annotated[bool, BizHawkName("A")] = False
    key_z: typing.Annotated[bool, BizHawkName("Z")] = False
    key_x: typing.Annotated[bool, BizHawkName("X")] = False
    key_c: typing.Annotated[bool, BizHawkName("C")] = False
    key_v: typing.Annotated[bool, BizHawkName("V")] = False
    key_b: typing.Annotated[bool, BizHawkName("B")] = False
    key_m: typing.Annotated[bool, BizHawkName("M")] = False
    key_period: typing.Annotated[bool, BizHawkName("PERIOD")] = False
    key_minus: typing.Annotated[bool, BizHawkName("-")] = False
    key_asterisk: typing.Annotated[bool, BizHawkName("*")] = False
    key_slash: typing.Annotated[bool, BizHawkName("/")] = False
    key_equals: typing.Annotated[bool, BizHawkName("=")] = False
    key_yes: typing.Annotated[bool, BizHawkName("YES")] = False
    key_no: typing.Annotated[bool, BizHawkName("NO")] = False
    key_clear: typing.Annotated[bool, BizHawkName("CLR")] = False
    key_enter: typing.Annotated[bool, BizHawkName("ENT")] = False
    reset: typing.Annotated[bool, BizHawkName("Reset")] = False
    power: typing.Annotated[bool, BizHawkName("Power")] = False

    @staticmethod
    def get_controller_type() -> typing.Type[BizHawkInput]:
        return Odyssey2Controller

    @staticmethod
    def get_max_controller_count() -> int:
        return 2
