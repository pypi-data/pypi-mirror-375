import dataclasses
import enum

import kurses.colors

DEFAULT_PTSIZE = 16


@dataclasses.dataclass
class Attribute:
    x: int
    y: int


@dataclasses.dataclass
class CharacterAttribute(Attribute):
    code: int = ord(' ')
    foreign: kurses.colors.TupleColor = (255, 255, 255)
    background: kurses.colors.TupleColor = (0, 0, 0)
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strikethrough: bool = False
    blink: int = 0
    sx: int = 1
    sy: int = 1

    def __eq__(self, other):
        return self.code == other.code

    def __hash__(self):
        _hash_tuple = (
            self.code, self.foreign, self.background, self.bold, self.italic, self.underline, self.strikethrough,
            self.sx, self.sy
        )

        return hash(_hash_tuple)

    def __bool__(self):
        return not self.code == ord(' ')

    @property
    def chr(self) -> str:
        return chr(self.code)

    @property
    def position(self):
        return self.x, self.y


@dataclasses.dataclass
class RectangleAttribute(Attribute):
    w: int
    h: int
    color: kurses.colors.TupleColor

    @property
    def size(self):
        return self.w, self.h

    @property
    def position(self):
        return self.x, self.y


class TypeCursor(enum.Enum):
    LINE = 0
    RECT = 1
    SOLID_RECT = 2
    VERTICAL = 3
    UNDERSCORE = 4
    EMPTY = 5
