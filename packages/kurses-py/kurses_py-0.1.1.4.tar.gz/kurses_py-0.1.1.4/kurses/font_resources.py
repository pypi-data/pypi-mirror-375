import abc
import enum
import typing

import kurses.stream
from kurses.stream import CharacterAttribute

R = typing.TypeVar("R", bound="FontResources")


class QualityFont(enum.Enum):
    SOLID = 0
    SHADED = 1
    LCD = 2
    BLENDED = 3


class EncodingFont(enum.Enum):
    ASCII = 0
    UTF_8 = 1
    UNICODE = 2


class FontResources(abc.ABC, typing.Generic[R]):
    def __init__(self, filename: str, ptsize: int = 16, depth_colors: int = 8, **kwargs):
        self.__allocate_textures: typing.Dict[CharacterAttribute, typing.Any] = {}
        self.__filename = filename
        self.__ptsize = ptsize
        self.__depth_colors = depth_colors
        self.__quality_font = kwargs.get("quality", QualityFont.BLENDED)
        self.__encoding = kwargs.get("encoding", EncodingFont.ASCII)
        self.auto_clean_cache = kwargs.get("auto_clean_cache", True)
        self.auto_clean_buffer = kwargs.get("auto_clean_buffer", True)

    @property
    def allocate_textures(self):
        return self.__allocate_textures

    @property
    def filename(self) -> str:
        return self.__filename

    @property
    def ptsize(self) -> int:
        return self.__ptsize

    @property
    def depth_colors(self) -> int:
        return self.__depth_colors

    @property
    def quality(self) -> QualityFont:
        return self.__quality_font

    @property
    def encoding(self) -> EncodingFont:
        return self.__encoding

    @property
    @abc.abstractmethod
    def size(self) -> typing.Tuple[int, int]: ...

    @property
    @abc.abstractmethod
    def font(self) -> R: ...

    @abc.abstractmethod
    def clean_cache(self): ...

    @abc.abstractmethod
    def present_chr(self, surface: R, _chr: kurses.stream.CharacterAttribute) -> R: ...
