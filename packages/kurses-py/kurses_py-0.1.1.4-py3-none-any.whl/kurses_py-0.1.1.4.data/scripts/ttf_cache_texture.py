import ctypes
import dataclasses
import string
import sys
import typing

import sdl2
import sdl2.sdlttf as ttf

WINDOW_SIZE_WIDTH, WINDOW_SIZE_HEIGHT = 640, 480
ROWS, COLS = 80, 30


@dataclasses.dataclass
class TextureCharacter:
    code: int
    background: typing.Tuple[int, int, int] = (255, 255, 255)
    foreign: typing.Tuple[int, int, int] = (255, 255, 255)

    def __hash__(self):
        return hash((
            self.code,
            self.background,
            self.foreign
        ))


def get_true_colors():
    for r in range(0, 256):
        for g in range(0, 256):
            for b in range(0, 256):
                yield r, g, b


def get_8bit_colors():
    for r in range(0, 256, 36):
        for g in range(0, 256, 36):
            for b in range(0, 256, 85):
                yield r, g, b


def get_2bit_colors():
    for r in (0, 85, 170, 255):
        for g in (0, 85, 170, 255):
            for b in (0, 85, 170, 255):
                yield r, g, b


def get_1bit_colors():
    for r in range(0, 256, 255):
        for g in range(0, 256, 255):
            for b in range(0, 256, 255):
                yield r, g, b


def query_texture(_texture: sdl2.SDL_Texture):
    w, h = ctypes.c_int(), ctypes.c_int()
    sdl2.SDL_QueryTexture(_texture, None, None, ctypes.byref(w), ctypes.byref(h))
    return w.value, h.value


def create_cache_textures(renderer: sdl2.SDL_Renderer, font: ttf.TTF_Font, allocate_texture, size_texture,
                          shape=(ROWS, COLS)):
    rows, cols = shape
    w, h = size_texture
    x, y = 0, 0

    dst_texture = sdl2.SDL_CreateTexture(renderer, sdl2.SDL_PIXELFORMAT_RGBA8888, sdl2.SDL_TEXTUREACCESS_TARGET,
                                         w * rows, h * cols)
    limit_w, limit_h = query_texture(dst_texture)
    sdl2.SDL_SetRenderTarget(renderer, dst_texture)

    sdl2.SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255)
    sdl2.SDL_RenderClear(renderer)

    def _render_target():
        sdl2.SDL_SetRenderTarget(renderer, None)

        return dst_texture

    for background in get_1bit_colors():
        for foreign in get_1bit_colors():
            for code in map(ord, string.ascii_letters):
                c = TextureCharacter(code, background, foreign)

                if c not in allocate_texture:
                    print(c.foreign, c.background)
                    chr_surface = ttf.TTF_RenderUTF8_Shaded(font, chr(c.code).encode(), sdl2.SDL_Color(*c.foreign),
                                                            sdl2.SDL_Color(*c.background))
                    chr_texture = sdl2.SDL_CreateTextureFromSurface(renderer, chr_surface)
                    sdl2.SDL_FreeSurface(chr_surface)

                    allocate_texture[c] = chr_texture

                _texture = allocate_texture[c]
                sdl2.SDL_RenderCopy(renderer, _texture, None, sdl2.SDL_Rect(x * w, y * h, w, h))

                x += 1

                if x * w >= limit_w:
                    y += 1
                    x = 0

                if y * h >= limit_h:
                    return _render_target()

    return _render_target()


def test_cache_textures():
    allocate_texture = {}

    sdl2.SDL_Init(0)
    ttf.TTF_Init()

    font = ttf.TTF_OpenFont(b"ModernDOS8x16.ttf", 16)

    if not font:
        return 1

    window = sdl2.SDL_CreateWindow(
        b"Cache textures",
        sdl2.SDL_WINDOWPOS_UNDEFINED, sdl2.SDL_WINDOWPOS_UNDEFINED,
        WINDOW_SIZE_WIDTH, WINDOW_SIZE_HEIGHT,
        sdl2.SDL_WINDOW_SHOWN
    )

    if not window:
        return 1

    renderer = sdl2.SDL_CreateRenderer(window, -1, 0)
    running = True

    w, h = WINDOW_SIZE_WIDTH // ROWS, WINDOW_SIZE_HEIGHT // COLS

    while running:
        event = sdl2.SDL_Event()
        while sdl2.SDL_PollEvent(ctypes.byref(event)):
            if event.type == sdl2.SDL_QUIT:
                running = False

        sdl2.SDL_RenderClear(renderer)
        sdl2.SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255)

        cache_texture = create_cache_textures(renderer, font, allocate_texture, (w, h))
        sdl2.SDL_RenderCopy(renderer, cache_texture, None, None)

        sdl2.SDL_RenderPresent(renderer)

    sdl2.SDL_Quit()

    return 0


if __name__ == "__main__":
    sys.exit(test_cache_textures())
