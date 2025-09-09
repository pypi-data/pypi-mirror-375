import typing

TupleColor = typing.Tuple[int, int, int]
Color = typing.Union[TupleColor, int]
GeneratorTupleColor = typing.Generator[TupleColor, None, None]


def rgb_to_hex(rgb: TupleColor) -> int:
    return (rgb[0] << 16) + (rgb[1] << 8) + rgb[2]


def hex_to_rgb(hex_color: int) -> TupleColor:
    hex_str = hex(hex_color)[2:]

    hex_str = hex_str.rjust(6, '0')

    r = int(hex_str[0:2], 16)
    g = int(hex_str[2:4], 16)
    b = int(hex_str[4:6], 16)

    return r, g, b


def get_true_colors() -> GeneratorTupleColor:
    for r in range(0, 256):
        for g in range(0, 256):
            for b in range(0, 256):
                yield r, g, b


def get_8bit_colors() -> GeneratorTupleColor:
    for r in range(0, 256, 36):
        for g in range(0, 256, 36):
            for b in range(0, 256, 85):
                yield r, g, b


def get_2bit_colors() -> GeneratorTupleColor:
    for r in (0, 85, 170, 255):
        for g in (0, 85, 170, 255):
            for b in (0, 85, 170, 255):
                yield r, g, b


def get_1bit_colors() -> GeneratorTupleColor:
    for r in range(0, 256, 255):
        for g in range(0, 256, 255):
            for b in range(0, 256, 255):
                yield r, g, b


def rgb_to_bit_depth(rgb: TupleColor, bit_depth: int) -> int:
    factor = 256 // bit_depth
    r, g, b = rgb

    r = r // factor * factor
    g = g // factor * factor
    b = b // factor * factor

    return (r << 16) + (g << 8) + (b << 4)


def cast_depth_colors(rgb: TupleColor, bits: int) -> TupleColor:
    r, g, b = rgb
    factor = 2 ** (8 - bits)

    r = (r // factor) * factor
    g = (g // factor) * factor
    b = (b // factor) * factor

    color = tuple(map(int, (r, g, b)))
    r, g, b = color

    return r, g, b
