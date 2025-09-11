# -*- coding: utf-8 -*-

"""
tasauria.systems.zx_spectrum
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Classes and functions related to the Sinclair ZX Spectrum (1982) system.

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

import dataclasses
import typing

from tasauria.types import BizHawkName, BizHawkInput, BizHawkSystemInput


ZX_SPECTRUM_SYSTEM_NAME = "ZXSpectrum"


@dataclasses.dataclass
class ZXSpectrumController(BizHawkInput):
    """
    Encapsulation of ZX Spectrum controller inputs.
    """

    up: typing.Annotated[bool, BizHawkName("Up")] = False
    down: typing.Annotated[bool, BizHawkName("Down")] = False
    left: typing.Annotated[bool, BizHawkName("Left")] = False
    right: typing.Annotated[bool, BizHawkName("Right")] = False
    button: typing.Annotated[bool, BizHawkName("Button")] = False


@dataclasses.dataclass
class ZXSpectrumInput(BizHawkSystemInput):
    key_true_video: typing.Annotated[bool, BizHawkName("Key True Video")] = False
    key_inv_video: typing.Annotated[bool, BizHawkName("Key Inv Video")] = False
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
    key_break: typing.Annotated[bool, BizHawkName("Key Break")] = False
    key_delete: typing.Annotated[bool, BizHawkName("Key Delete")] = False
    key_graph: typing.Annotated[bool, BizHawkName("Key Graph")] = False
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
    key_extend_mode: typing.Annotated[bool, BizHawkName("Key Extend Mode")] = False
    key_edit: typing.Annotated[bool, BizHawkName("Key Edit")] = False
    key_a: typing.Annotated[bool, BizHawkName("Key A")] = False
    key_s: typing.Annotated[bool, BizHawkName("Key S")] = False
    key_d: typing.Annotated[bool, BizHawkName("Key D")] = False
    key_f: typing.Annotated[bool, BizHawkName("Key F")] = False
    key_g: typing.Annotated[bool, BizHawkName("Key G")] = False
    key_h: typing.Annotated[bool, BizHawkName("Key H")] = False
    key_j: typing.Annotated[bool, BizHawkName("Key J")] = False
    key_k: typing.Annotated[bool, BizHawkName("Key K")] = False
    key_l: typing.Annotated[bool, BizHawkName("Key L")] = False
    key_return: typing.Annotated[bool, BizHawkName("Key Return")] = False
    key_caps_shift: typing.Annotated[bool, BizHawkName("Key Caps Shift")] = False
    key_caps_lock: typing.Annotated[bool, BizHawkName("Key Caps Lock")] = False
    key_z: typing.Annotated[bool, BizHawkName("Key Z")] = False
    key_x: typing.Annotated[bool, BizHawkName("Key X")] = False
    key_c: typing.Annotated[bool, BizHawkName("Key C")] = False
    key_v: typing.Annotated[bool, BizHawkName("Key V")] = False
    key_b: typing.Annotated[bool, BizHawkName("Key B")] = False
    key_n: typing.Annotated[bool, BizHawkName("Key N")] = False
    key_m: typing.Annotated[bool, BizHawkName("Key M")] = False
    key_period: typing.Annotated[bool, BizHawkName("Key Period")] = False
    key_symbol_shift: typing.Annotated[bool, BizHawkName("Key Symbol Shift")] = False
    key_semicolon: typing.Annotated[bool, BizHawkName("Key Semi-Colon")] = False
    key_quote: typing.Annotated[bool, BizHawkName("Key Quote")] = False
    key_left_cursor: typing.Annotated[bool, BizHawkName("Key Left Cursor")] = False
    key_right_cursor: typing.Annotated[bool, BizHawkName("Key Right Cursor")] = False
    key_space: typing.Annotated[bool, BizHawkName("Key Space")] = False
    key_up_cursor: typing.Annotated[bool, BizHawkName("Key Up Cursor")] = False
    key_down_cursor: typing.Annotated[bool, BizHawkName("Key Dpwn Cursor")] = False
    key_comma: typing.Annotated[bool, BizHawkName("Key Comma")] = False
    reset: typing.Annotated[bool, BizHawkName("Reset")] = False
    power: typing.Annotated[bool, BizHawkName("Power")] = False
    play_tape: typing.Annotated[bool, BizHawkName("Play Tape")] = False
    stop_tape: typing.Annotated[bool, BizHawkName("Stop Tape")] = False
    rtz_tape: typing.Annotated[bool, BizHawkName("RTZ Tape")] = False
    record_tape: typing.Annotated[bool, BizHawkName("Record Tape")] = False
    insert_next_tape: typing.Annotated[bool, BizHawkName("Insert Next Tape")] = False
    insert_previous_tape: typing.Annotated[bool, BizHawkName("Insert Previous Tape")] = False
    next_tape_block: typing.Annotated[bool, BizHawkName("Next Tape Block")] = False
    previous_tape_block: typing.Annotated[bool, BizHawkName("Prev Tape Block")] = False
    get_tape_status: typing.Annotated[bool, BizHawkName("Get Tape Status")] = False
    insert_next_disk: typing.Annotated[bool, BizHawkName("Insert Next Disk")] = False
    insert_previous_disk: typing.Annotated[bool, BizHawkName("Insert Previous Disk")] = False
    get_disk_status: typing.Annotated[bool, BizHawkName("Get Disk Status")] = False

    @staticmethod
    def get_controller_type() -> typing.Type[BizHawkInput]:
        return ZXSpectrumController

    @staticmethod
    def get_max_controller_count() -> int:
        return 3
