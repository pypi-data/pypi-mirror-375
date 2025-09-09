import abc
import enum
import typing

import kurses.colors
import kurses.stream
import kurses.texture_surface
import kurses.events

DEFAULT_WINDOW_TITLE = "Virtual console"

T = typing.TypeVar("T", bound="VirtualTerminal")


class Rendering(enum.Enum):
    HARDWARE = 0
    SOFTWARE = 1


class VirtualTerminal(abc.ABC, typing.Generic[T]):
    def __init__(self, font_filename: str, shape=(80, 30), **kwargs):
        """
        VirtualTerminal constructor.

        :keyword font_filename: Font source filename.
        :type font_filename: str

        :keyword shape: Limit frames per second, with default value 80x30.
        :type shape: typing.Tuple[int, int]
        :keyword size: Size window, with default value 640x480.
        :type size: int
        :keyword title: Title window, with default value "Virtual terminal".
        :type title: str
        :keyword type_rendering: Type rendering, with default value Rendering.HARDWARE.
        :type type_rendering: Rendering
        :keyword fps: Limit frames per second, with default value 30.
        :type fps: int
        """
        rows, cols = shape

        self.__main_stream = kurses.stream.StreamBuffer(rows, cols)
        self.__stream_list = [self.__main_stream]
        self.__window_title = kwargs.get("title", "Virtual terminal")
        self.__type_rendering = kwargs.get("rendering", Rendering.HARDWARE)

        self._font_filename = font_filename
        self._dt = 1.0
        self._resizable = kwargs.get("resizable", False)

        self.fps = kwargs.get("fps", 30)
        self.running = True

    @property
    def type_rendering(self) -> Rendering:
        return self.__type_rendering

    @property
    def stream(self) -> kurses.stream.StreamBuffer:
        """
        Get main stream buffer of Virtual term

        :return: Main buffer
        """
        return self.__stream_list[0]

    @property
    def shape(self) -> typing.Tuple[int, int]:
        return self.stream.shape

    @property
    @abc.abstractmethod
    def size(self) -> typing.Tuple[int, int]:
        """
        Get the size of Window.

        :return: Size window.
        :rtype: typing.Tuple[int, int]
        """
        ...

    @property
    def dt(self) -> float:
        """
        Get the delta time of all loop program.

        :return: Delta time.
        :rtype: float
        """
        return self._dt

    @property
    def resizable(self) -> bool:
        """
        Get the resizable property of the console.

        :return: The resizable property of the console.
        :rtype: bool
        """
        return self._resizable

    @resizable.setter
    def resizable(self, resizable: bool):
        """
        Set the resizable property of the console.

        :param resizable:
        :return:
        """
        self._resizable = resizable

    @property
    @abc.abstractmethod
    def resizable_window(self) -> bool:
        """
        Get the resizable property of the window.

        :return: bool
        """

    @resizable_window.setter
    @abc.abstractmethod
    def resizable_window(self, resizable: bool):
        """
        Set the resizable property of the window.

        :param resizable: bool
        :return:
        """

    @property
    def streams(self) -> typing.List[kurses.stream.StreamBuffer]:
        """
        Get list of virtual buffers.

        :return: typing.List[kurses.buffer.VirtualBuffer]
        """
        return self.__stream_list

    @property
    @abc.abstractmethod
    def title(self) -> str:
        """
        Get title of virtual console (Windows).

        :return: str
        """
        return self.__window_title

    @title.setter
    @abc.abstractmethod
    def title(self, _str: str):
        """
        Set title of virtual console (Windows).

        :type _str: String of title.
        :type _str: str
        :return: None
        """

    @abc.abstractmethod
    def set_target(self, target: typing.Callable[[], None]):
        """
        Set main loop function.

        :param target: Main loop function.
        :type target: typing.Callable[[None], None]
        :return: None
        """
        ...

    @abc.abstractmethod
    def set_runtime(self, target: typing.Type[kurses.events.EventTargetRuntime]):
        ...

    @abc.abstractmethod
    def main_loop(self):
        """
        Run virtual console, with all background service (SDL2 or Pygame).

        :return: None
        """
        ...

    @abc.abstractmethod
    def keyspressed(self) -> typing.List[str]:
        """
        Get all key pressed.

        :return: typing.List[str]
        """
        ...

    @property
    @abc.abstractmethod
    def window(self) -> T:
        """
        Get window instance.

        :return: T
        """
        ...

    @property
    @abc.abstractmethod
    def surface(self) -> T:
        """
        Get surface instance.

        :return: T
        """
        ...

    @abc.abstractmethod
    def push_events(self, event: T):
        """
        Push type event.

        :param event: Type event.
        :type event: T
        :return: None
        """
        ...

    @abc.abstractmethod
    def present(self):
        """
        Update surface.

        :return: None
        """
        ...

    @abc.abstractmethod
    def quit(self):
        """
        Quit virtual console.

        :return: None
        """
        ...

    @abc.abstractmethod
    def draw(self):
        """
        Draw in virtual console
        :return:
        """
        ...

    @abc.abstractmethod
    def clean(self):
        """
        Clean in virtual console

        :return:
        """
        ...
