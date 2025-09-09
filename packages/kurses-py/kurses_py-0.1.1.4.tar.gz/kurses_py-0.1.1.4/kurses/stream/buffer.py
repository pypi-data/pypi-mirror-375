import typing

from kurses.stream import CharacterAttribute, RectangleAttribute


def fix_position_attribute(shape: typing.Tuple[int, int], index: typing.Tuple[int, int],
                           attr: typing.Union[CharacterAttribute, RectangleAttribute]):
    rows, columns = shape
    x, y = index

    while x >= columns:
        x = x - (columns + 1)
        y += 1

    while x < 0:
        x = x + (columns + 1)
        y -= 1

    attr.x = x
    attr.y = y

    return (x, y), attr


def protect_buffer_matrix(shape: typing.Tuple[int, int], index: typing.Tuple[int, int], buffer: typing.List[
    typing.List[typing.Optional[typing.Union[CharacterAttribute, RectangleAttribute]]]],
                          attr: typing.Union[CharacterAttribute, RectangleAttribute]):
    rows, columns = shape
    x, y = index

    if 0 <= x < columns and 0 <= y < rows:
        buffer[y][x] = attr

    return buffer


class BufferMatrix:
    def __init__(self, shape: typing.Tuple[int, int]):
        rows, columns = shape

        self.__rows: int = rows
        self.__cols: int = columns
        self.__buffer_matrix: typing.List[
            typing.List[typing.Optional[typing.Union[CharacterAttribute, RectangleAttribute]]]] = [[None] * columns for
                                                                                                   _ in range(rows)]

    @property
    def cols(self) -> int:
        return self.__cols

    @property
    def rows(self) -> int:
        return self.__rows

    def __setitem__(self, index: typing.Tuple[int, int], value: typing.Union[CharacterAttribute, RectangleAttribute]):
        x, y = 0, 0

        if isinstance(index, tuple):
            x, y = index

        (x, y), value = fix_position_attribute(self.shape, (x, y), value)

        protect_buffer_matrix(self.shape, (x, y), self.__buffer_matrix, value)

    def __getitem__(self, index: typing.Tuple[int, int]) -> typing.Union[CharacterAttribute, RectangleAttribute, None]:
        x, y = index

        return self.__buffer_matrix[y][x]

    def clear(self):
        self.__buffer_matrix = [[None] * self.__cols for _ in range(self.__rows)]

    def reshape(self, shape: typing.Tuple[int, int]):
        all_buff_objects = [obj for obj in self]

        self.__rows, self.__cols = shape
        self.__buffer_matrix = [[None] * self.__cols for _ in range(self.__rows)]

        for obj in all_buff_objects:
            x, y = obj.x, obj.y

            (x, y), value = fix_position_attribute(self.shape, (x, y), obj)

            protect_buffer_matrix(self.shape, (x, y), self.__buffer_matrix, value)

    @property
    def shape(self) -> typing.Tuple[int, int]:
        return self.__rows, self.__cols

    @shape.setter
    def shape(self, shape: typing.Tuple[int, int]):
        self.__rows, self.__cols = shape

    def __iter__(self) -> typing.Generator[typing.Union[CharacterAttribute, RectangleAttribute], None, None]:
        for i in range(self.__rows):
            for j in range(self.__cols):
                attr = self.__buffer_matrix[i][j]

                if attr is not None:
                    yield attr
