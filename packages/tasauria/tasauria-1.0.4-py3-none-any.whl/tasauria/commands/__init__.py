# -*- coding: utf-8 -*-

"""
tasauria.commands
~~~~~~~~~~~~~~~~~~

Wrapper implementations for the TASauria server's commands.

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

import typing


# The type the command expects to get in as Python kwargs
PythonCommandInput = typing.TypeVar("PythonCommandInput", bound=typing.Mapping[str, typing.Any])
# The format the server is actually expecting of the arguments to this command
ServerCommandInput = typing.TypeVar("ServerCommandInput", bound=typing.Mapping[str, typing.Any])
# The format the server returns upon the command executing successfully
ServerCommandOutput = typing.TypeVar("ServerCommandOutput", bound=typing.Mapping[str, typing.Any])
# Whatever we choose to return from the command on the Python end
PythonCommandOutput = typing.TypeVar("PythonCommandOutput")


class Command(typing.Generic[PythonCommandInput, ServerCommandInput, ServerCommandOutput, PythonCommandOutput]):
    """
    Abstract base class for command implementations
    """

    @staticmethod
    def marshal_input(
        # This should be:
        #   **kwargs: typing.Unpack[PythonCommandInput],
        # where PythonCommandInput is bound=TypedDict,
        # but this is just impossible for some reason :)
        **kwargs: typing.Any
    ) -> typing.Tuple[str, ServerCommandInput]:
        """
        Converts our Python-end wrapped input into a tuple of:
        - The command name
        - The argument payload to send to the server
        """

        raise NotImplementedError()

    @staticmethod
    def unmarshal_output(
        payload: ServerCommandOutput,
        **kwargs: typing.Any
    ) -> PythonCommandOutput:
        """
        Takes the payload from the server and returns an appropriate Python type to wrap it.

        The keyword arguments to this function are the same as is sent to `marshal_input`.
        This allows decoding to use information about what arguments were sent.
        """

        raise NotImplementedError()


AnyCommand = Command[
    typing.Any,
    typing.Dict[str, typing.Any],
    typing.Dict[str, typing.Any],
    typing.Any
]


class NoArguments(typing.TypedDict):
    pass
