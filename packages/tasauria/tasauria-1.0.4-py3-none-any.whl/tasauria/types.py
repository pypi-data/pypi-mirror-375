# -*- coding: utf-8 -*-

"""
tasauria.types
~~~~~~~~~~~~~~~

Types, dataclasses, and type-related functions that appear commonly throughout tasauria.

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

import copy
import dataclasses
import typing


@dataclasses.dataclass
class BizHawkName:
    """
    An annotation type that can be used to indicate to data processing routines what
    name is used for this attribute in BizHawk.
    """

    name: str


def get_bizhawk_name(type_to_test: typing.Any) -> typing.Optional[BizHawkName]:
    """
    Returns the BizHawkName annotation associated with a type if one exists.
    """

    if typing.get_origin(type_to_test) is typing.Annotated:
        for annotation in typing.get_args(type_to_test):
            if isinstance(annotation, BizHawkName):
                return annotation

    return None


BizHawkInputOrSubclass = typing.TypeVar("BizHawkInputOrSubclass", bound="BizHawkInput")


@dataclasses.dataclass
class BizHawkInput:
    """
    An ABC covering the functionality all inputs have.
    """

    @classmethod
    def transform_from_bizhawk_names(
        cls: typing.Type[BizHawkInputOrSubclass],
        values: typing.Dict[str, typing.Union[int, bool]],
        prefix: str = ""
    ) -> typing.Dict[str, typing.Union[int, bool]]:
        """
        Transforms a dictionary containing BizHawk-format input names to values into a dictionary containing
        the same information but with the field names of this BizHawkInput dataclass.
        """

        dictionary: typing.Dict[str, typing.Union[int, bool]] = {}

        for field in dataclasses.fields(cls):
            bizhawk_name = get_bizhawk_name(field.type)

            if bizhawk_name is not None and prefix + bizhawk_name.name in values:
                dictionary[field.name] = values[prefix + bizhawk_name.name]

        return dictionary

    @classmethod
    def from_dict(
        cls: typing.Type[BizHawkInputOrSubclass],
        values: typing.Dict[str, typing.Union[int, bool]],
        prefix: str = ""
    ) -> BizHawkInputOrSubclass:
        """
        Converts a dictionary received from the TASauria plugin server into an input of this type.

        Any values that don't map into this type will be ignored, and any missing fields will have default values.
        """

        return cls(**cls.transform_from_bizhawk_names(values, prefix=prefix))

    def copy(
        self: BizHawkInputOrSubclass
    ) -> BizHawkInputOrSubclass:
        """
        Makes a deep copy of this input state.

        You can use this to, e.g., copy the state of controller 1 to controller 2 or so on.
        """

        return copy.deepcopy(self)

    @classmethod
    def default(
        cls: typing.Type[BizHawkInputOrSubclass]
    ) -> BizHawkInputOrSubclass:
        """
        Returns a default state for this input type.
        """

        return cls.from_dict({})

    def to_dict(
        self,
        prefix: str = ""
    ) -> typing.Dict[str, typing.Union[int, bool]]:
        """
        Converts this type into a BizHawk-format dictionary of input values.
        """

        dictionary: typing.Dict[str, typing.Union[int, bool]] = {}

        for field in dataclasses.fields(self):
            bizhawk_name = get_bizhawk_name(field.type)

            if bizhawk_name is not None:
                dictionary[prefix + bizhawk_name.name] = getattr(self, field.name)

        return dictionary


BizHawkSystemInputOrSubclass = typing.TypeVar("BizHawkSystemInputOrSubclass", bound="BizHawkSystemInput")


@dataclasses.dataclass
class BizHawkSystemInput(BizHawkInput):
    """
    An ABC representing input at the system level.

    This nests the controllers, so the result is an encapsulation of both system input (e.g. Power/Reset buttons),
    and prefixed controller inputs (e.g. `P1 Start`).
    """

    controllers: typing.List[BizHawkInput] = dataclasses.field(default_factory=list)

    @staticmethod
    def get_controller_type() -> typing.Type[BizHawkInput]:
        raise NotImplementedError()

    @staticmethod
    def get_max_controller_count() -> int:
        raise NotImplementedError()

    @classmethod
    def from_dict(
        cls: typing.Type[BizHawkSystemInputOrSubclass],
        values: typing.Dict[str, typing.Union[int, bool]],
        prefix: str = ""
    ) -> BizHawkSystemInputOrSubclass:

        return cls(
            controllers=[
                cls.get_controller_type().from_dict(values, prefix=f"{prefix}P{controller_index + 1} ")
                for controller_index in range(cls.get_max_controller_count())
            ],
            **cls.transform_from_bizhawk_names(values, prefix=prefix)
        )

    def to_dict(
        self,
        prefix: str = ""
    ) -> typing.Dict[str, typing.Union[int, bool]]:
        dictionary = super().to_dict(prefix)

        for controller_index, controller in enumerate(self.controllers):
            dictionary.update(controller.to_dict(prefix=f"{prefix}P{controller_index + 1} "))

        return dictionary


class TASauriaJoypadPayload(typing.TypedDict):
    system: str
    boardType: str
    state: typing.Dict[str, typing.Union[bool, int]]
