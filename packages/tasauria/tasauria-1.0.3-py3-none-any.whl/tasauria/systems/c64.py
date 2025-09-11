# -*- coding: utf-8 -*-

"""
tasauria.systems.c64
~~~~~~~~~~~~~~~~~~~~~

Classes and functions related to the Commodore 64 (1982) system.

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

import dataclasses
import typing

from tasauria.types import BizHawkName, BizHawkInput, BizHawkSystemInput


COMMODORE_64_SYSTEM_NAME = "C64"


@dataclasses.dataclass
class Commodore64Controller(BizHawkInput):
    """
    Encapsulation of Commodore 64 controller inputs.
    """

    up: typing.Annotated[bool, BizHawkName("Up")] = False
    down: typing.Annotated[bool, BizHawkName("Down")] = False
    left: typing.Annotated[bool, BizHawkName("Left")] = False
    right: typing.Annotated[bool, BizHawkName("Right")] = False
    button: typing.Annotated[bool, BizHawkName("Button")] = False


@dataclasses.dataclass
class Commodore64Input(BizHawkSystemInput):
    key_left: typing.Annotated[bool, BizHawkName("Key Left Arrow")] = False
    key_1: typing.Annotated[bool, BizHawkName("Key 1")] = False
    key_2: typing.Annotated[bool, BizHawkName("Key 2")] = False
    key_3: typing.Annotated[bool, BizHawkName("Key 3")] = False
    key_4: typing.Annotated[bool, BizHawkName("Key 4")] = False
    key_5: typing.Annotated[bool, BizHawkName("Key 5")] = False
    key_6: typing.Annotated[bool, BizHawkName("Key 6")] = False
    key_7: typing.Annotated[bool, BizHawkName("Key 7")] = False
    key_8: typing.Annotated[bool, BizHawkName("Key 8")] = False
    key_9: typing.Annotated[bool, BizHawkName("Key 9")] = False
    key_0: typing.Annotated[bool, BizHawkName("Key 0")] = False
    key_plus: typing.Annotated[bool, BizHawkName("Key Plus")] = False
    key_minus: typing.Annotated[bool, BizHawkName("Key Minus")] = False
    key_pound: typing.Annotated[bool, BizHawkName("Key Pound")] = False
    key_clear_home: typing.Annotated[bool, BizHawkName("Key Clear/Home")] = False
    key_insert_delete: typing.Annotated[bool, BizHawkName("Key Insert/Delete")] = False
    key_control: typing.Annotated[bool, BizHawkName("Key Control")] = False
    key_q: typing.Annotated[bool, BizHawkName("Key Q")] = False
    key_w: typing.Annotated[bool, BizHawkName("Key W")] = False
    key_e: typing.Annotated[bool, BizHawkName("Key E")] = False
    key_r: typing.Annotated[bool, BizHawkName("Key R")] = False
    key_t: typing.Annotated[bool, BizHawkName("Key T")] = False
    key_y: typing.Annotated[bool, BizHawkName("Key Y")] = False
    key_u: typing.Annotated[bool, BizHawkName("Key U")] = False
    key_i: typing.Annotated[bool, BizHawkName("Key I")] = False
    key_o: typing.Annotated[bool, BizHawkName("Key O")] = False
    key_p: typing.Annotated[bool, BizHawkName("Key P")] = False
    key_at: typing.Annotated[bool, BizHawkName("Key At")] = False
    key_asterisk: typing.Annotated[bool, BizHawkName("Key Asterisk")] = False
    key_up: typing.Annotated[bool, BizHawkName("Key Up Arrow")] = False
    key_restore: typing.Annotated[bool, BizHawkName("Key Restore")] = False
    key_run_stop: typing.Annotated[bool, BizHawkName("Key Run/Stop")] = False
    key_lck: typing.Annotated[bool, BizHawkName("Key Lck")] = False
    key_a: typing.Annotated[bool, BizHawkName("Key A")] = False
    key_s: typing.Annotated[bool, BizHawkName("Key S")] = False
    key_d: typing.Annotated[bool, BizHawkName("Key D")] = False
    key_f: typing.Annotated[bool, BizHawkName("Key F")] = False
    key_g: typing.Annotated[bool, BizHawkName("Key G")] = False
    key_h: typing.Annotated[bool, BizHawkName("Key H")] = False
    key_j: typing.Annotated[bool, BizHawkName("Key J")] = False
    key_k: typing.Annotated[bool, BizHawkName("Key K")] = False
    key_l: typing.Annotated[bool, BizHawkName("Key L")] = False
    key_colon: typing.Annotated[bool, BizHawkName("Key Colon")] = False
    key_semicolon: typing.Annotated[bool, BizHawkName("Key Semicolon")] = False
    key_equals: typing.Annotated[bool, BizHawkName("Key Equal")] = False
    key_return: typing.Annotated[bool, BizHawkName("Key Return")] = False
    key_commodore: typing.Annotated[bool, BizHawkName("Key Commodore")] = False
    key_left_shift: typing.Annotated[bool, BizHawkName("Key Left Shift")] = False
    key_z: typing.Annotated[bool, BizHawkName("Key Z")] = False
    key_x: typing.Annotated[bool, BizHawkName("Key X")] = False
    key_c: typing.Annotated[bool, BizHawkName("Key C")] = False
    key_v: typing.Annotated[bool, BizHawkName("Key V")] = False
    key_b: typing.Annotated[bool, BizHawkName("Key B")] = False
    key_n: typing.Annotated[bool, BizHawkName("Key N")] = False
    key_m: typing.Annotated[bool, BizHawkName("Key M")] = False
    key_comma: typing.Annotated[bool, BizHawkName("Key Comma")] = False
    key_period: typing.Annotated[bool, BizHawkName("Key Period")] = False
    key_slash: typing.Annotated[bool, BizHawkName("Key Slash")] = False
    key_right_shift: typing.Annotated[bool, BizHawkName("Key Right Shift")] = False
    key_cursor_ud: typing.Annotated[bool, BizHawkName("Key Cursor Up/Down")] = False
    key_cursor_lr: typing.Annotated[bool, BizHawkName("Key Cursor Left/Right")] = False
    key_space: typing.Annotated[bool, BizHawkName("Key Space")] = False
    key_f1: typing.Annotated[bool, BizHawkName("Key F1")] = False
    key_f3: typing.Annotated[bool, BizHawkName("Key F3")] = False
    key_f5: typing.Annotated[bool, BizHawkName("Key F5")] = False
    key_f7: typing.Annotated[bool, BizHawkName("Key F7")] = False
    previous_disk: typing.Annotated[bool, BizHawkName("Previous Disk")] = False
    next_disk: typing.Annotated[bool, BizHawkName("Next Disk")] = False
    power: typing.Annotated[bool, BizHawkName("Power")] = False
    reset: typing.Annotated[bool, BizHawkName("Reset")] = False

    @staticmethod
    def get_controller_type() -> typing.Type[BizHawkInput]:
        return Commodore64Controller

    @staticmethod
    def get_max_controller_count() -> int:
        return 2
