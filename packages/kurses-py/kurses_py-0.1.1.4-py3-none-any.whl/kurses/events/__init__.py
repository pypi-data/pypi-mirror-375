import abc
import typing


class EventTargetRuntime(abc.ABC):
    """
    EventTargetRuntime interface.
    """

    def load(self):
        """
        Event when the program is loaded successfully and before starting the loop.
        :return:
        """
        ...

    @abc.abstractmethod
    def update(self, dt: typing.Union[int, float]):
        """
        Main event for the program loop.
        :param dt:
        :return:
        """
        ...

    def draw(self):
        """
        Main event for the program loop.
        :return:
        """
        ...

    def resize(self, resizable: bool):
        """
        Event when the window is resized.
        :param resizable:
        :return:
        """
        ...

    def minimized(self):
        """
        Event when the window is minimized.
        :return:
        """
        ...

    def hidden(self):
        """
        Event when the window is hidden.
        :return:
        """
        ...

    def showed(self):
        """
        Event when the window is showed.
        :return:
        """
        ...

    def exposed(self):
        """
        Event when the window is exposed.
        :return:
        """
        ...

    def restored(self):
        """
        Event when the window is restored.
        :return:
        """
        ...

    def close(self):
        """
        Event when the window is closed.
        :return:
        """
        ...

    def exit(self):
        """
        Event when the window is exit.
        :return:
        """
        ...

    def key_down(self, key: str):
        """
        Event when the key is pressed.
        :param key:
        :return:
        """
        ...

    def key_up(self, key: str):
        """
        Event when the key is released.
        :param key:
        :return:
        """
        ...

    def mouse(self, position: typing.Tuple[int, int], click: typing.List[str]):
        """
        Event when the mouse is clicked.
        :param position:
        :param click:
        :return:
        """
        ...

    def scroll(self, move: int):
        """
        Event when the window is scrolling.
        :param move:
        :return:
        """
        ...


class EmptyTargetRuntime(EventTargetRuntime):
    """
    Empty EventTargetRuntime for testing only.
    """

    def update(self, dt: typing.Union[int, float]):
        ...


def empty_target() -> None:
    """
    Empty target for testing only.
    :return:
    """
    ...
