import abc
import typing

import kurses.font_resources
import kurses.stream

K = typing.TypeVar("K", bound="TextureSurface")


class TextureSurface(abc.ABC, typing.Generic[K]):
    def __init__(self, font: kurses.font_resources.FontResources, streams: typing.List[kurses.stream.StreamBuffer]):
        self.__font = font
        self.__streams = streams

    @abc.abstractmethod
    def create(self, surface: K): ...

    @abc.abstractmethod
    def destroy(self): ...

    @property
    def font(self) -> kurses.font_resources.FontResources:
        return self.__font

    @property
    def stream(self) -> kurses.stream.StreamBuffer:
        return self.__streams[0]

    @property
    def streams(self) -> typing.List[kurses.stream.StreamBuffer]:
        return self.__streams

    @streams.setter
    def streams(self, streams: typing.List[kurses.stream.StreamBuffer]):
        self.__streams = streams

    @abc.abstractmethod
    def present(self, surface: K) -> K: ...

    @abc.abstractmethod
    def clear(self, surface: K) -> None: ...

    @property
    @abc.abstractmethod
    def current(self) -> typing.Union[K, None]: ...

    @property
    @abc.abstractmethod
    def size(self) -> typing.Tuple[int, int]: ...
