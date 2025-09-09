import ctypes
import functools
import typing

import sdl2
import sdl2.sdlttf

import kurses.colors
import kurses.font_resources
import kurses.stream
import kurses.term

RenderMethodSDL2 = typing.Callable[[sdl2.sdlttf.TTF_Font, int, sdl2.SDL_Color, sdl2.SDL_Color], sdl2.SDL_Surface]


def cast_render_method(_render_method) -> RenderMethodSDL2:
    def inner(font, _chr, fg, bg):
        r, g, b, a = 0x000000FF, 0x0000FF00, 0x00FF0000, 0xFF000000
        _surface_font = _render_method(font, _chr, fg)

        w, h = get_size_from_surface_sdl2(_surface_font)
        _surface = sdl2.SDL_CreateRGBSurface(
            0, w, h, 32, r, g, b, a
        )
        _color_bg = sdl2.SDL_MapRGB(_surface.contents.format.contents, bg.r, bg.g, bg.b)
        sdl2.SDL_FillRect(_surface, None, _color_bg)

        sdl2.SDL_BlitSurface(_surface_font, None, _surface, None)

        return _surface

    return inner


def cast_color_sdl2(color=(0, 0, 0)) -> sdl2.SDL_Color:
    return sdl2.SDL_Color(*color)


def get_size_from_texture_sdl2(texture: sdl2.SDL_Texture):
    w, h = ctypes.c_int(), ctypes.c_int()
    sdl2.SDL_QueryTexture(texture, None, None, ctypes.byref(w), ctypes.byref(h))
    return w.value, h.value


def get_size_from_surface_sdl2(surface: sdl2.SDL_Surface):
    return surface.contents.w, surface.contents.h


def create_texture_chr_sdl2(font: sdl2.sdlttf.TTF_Font, render_method: RenderMethodSDL2, renderer: sdl2.SDL_Renderer,
                            code: int, fg=(0, 0, 0), bg=(0, 0, 0), style=0) -> sdl2.SDL_Texture:
    sdl2.sdlttf.TTF_SetFontStyle(font, style)

    _surface = render_method(font, code, cast_color_sdl2(fg), cast_color_sdl2(bg))
    _texture = sdl2.SDL_CreateTextureFromSurface(renderer, _surface)

    sdl2.SDL_FreeSurface(_surface)

    return _texture


def get_style_sdl2(chr_attr: kurses.stream.CharacterAttribute, all_styles: dict) -> int:
    style = 0

    for _s in all_styles.keys():
        if getattr(chr_attr, _s):
            style |= all_styles[_s]

    return style


def get_size_surface_from_font(font: sdl2.sdlttf.TTF_Font, render_method: RenderMethodSDL2):
    _surface = render_method(font, ord(' '), cast_color_sdl2((0, 0, 0)), cast_color_sdl2((0, 0, 0)))
    size = get_size_from_surface_sdl2(_surface)

    sdl2.SDL_FreeSurface(_surface)

    return size


def get_size_textures_from_font(font: sdl2.sdlttf.TTF_Font, renderer: sdl2.SDL_Renderer, _method: RenderMethodSDL2):
    empty_texture = create_texture_chr_sdl2(font, _method, renderer, ord(' '))
    size = get_size_from_texture_sdl2(empty_texture)

    sdl2.SDL_DestroyTexture(empty_texture)

    return size


def get_render_font_method_sdl2(encoding: kurses.font_resources.EncodingFont,
                                quality: kurses.font_resources.QualityFont, render_methods: dict) -> RenderMethodSDL2:
    render_method = render_methods[encoding][quality]

    def inner(font, _chr, fg, bg):
        _chr = chr(_chr).encode() if isinstance(_chr, int) else _chr.encode()
        return render_method(font, _chr, fg, bg)

    return inner


class SDL2FontResources(kurses.font_resources.FontResources):
    __ALL_RENDER_METHODS_SDL2 = {
        kurses.font_resources.EncodingFont.ASCII: {
            kurses.font_resources.QualityFont.SOLID: cast_render_method(sdl2.sdlttf.TTF_RenderText_Solid),
            kurses.font_resources.QualityFont.SHADED: sdl2.sdlttf.TTF_RenderText_Shaded,
            kurses.font_resources.QualityFont.LCD: sdl2.sdlttf.TTF_RenderText_LCD,
            kurses.font_resources.QualityFont.BLENDED: cast_render_method(sdl2.sdlttf.TTF_RenderText_Blended)
        },
        kurses.font_resources.EncodingFont.UTF_8: {
            kurses.font_resources.QualityFont.SOLID: cast_render_method(sdl2.sdlttf.TTF_RenderUTF8_Solid),
            kurses.font_resources.QualityFont.SHADED: sdl2.sdlttf.TTF_RenderUTF8_Shaded,
            kurses.font_resources.QualityFont.LCD: sdl2.sdlttf.TTF_RenderUTF8_LCD,
            kurses.font_resources.QualityFont.BLENDED: cast_render_method(sdl2.sdlttf.TTF_RenderUTF8_Blended)
        },
        kurses.font_resources.EncodingFont.UNICODE: {
            kurses.font_resources.QualityFont.SOLID: cast_render_method(sdl2.sdlttf.TTF_RenderUNICODE_Solid),
            kurses.font_resources.QualityFont.SHADED: sdl2.sdlttf.TTF_RenderUNICODE_Shaded,
            kurses.font_resources.QualityFont.LCD: sdl2.sdlttf.TTF_RenderUNICODE_LCD,
            kurses.font_resources.QualityFont.BLENDED: cast_render_method(sdl2.sdlttf.TTF_RenderUNICODE_Blended)
        },
    }

    __ALL_FONT_STYLES = {
        "bold": sdl2.sdlttf.TTF_STYLE_BOLD,
        "italic": sdl2.sdlttf.TTF_STYLE_ITALIC,
        "underline": sdl2.sdlttf.TTF_STYLE_UNDERLINE,
        "strikethrough": sdl2.sdlttf.TTF_STYLE_STRIKETHROUGH,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__c_font = sdl2.sdlttf.TTF_OpenFont(self.filename.encode(), ptsize=self.ptsize)

        if self.__c_font is None:
            raise FileNotFoundError("Font no found")

        self.__default_render_method = lambda: get_render_font_method_sdl2(
            self.encoding, self.quality, self.__ALL_RENDER_METHODS_SDL2
        )

        self.__size = get_size_surface_from_font(
            self.__c_font, self.__default_render_method()
        )

    def __del__(self):
        self.clean_cache()
        sdl2.sdlttf.TTF_CloseFont(self.font)

    @property
    def size(self) -> typing.Tuple[int, int]:
        self.__size = get_size_surface_from_font(
            self.__c_font, self.__default_render_method()
        )

        return self.__size

    @property
    def font(self) -> sdl2.sdlttf.TTF_Font:
        return self.__c_font

    def clean_cache(self):
        for _, texture in self.allocate_textures.items():
            sdl2.SDL_DestroyTexture(texture)

    def present_chr(self, surface: sdl2.SDL_Renderer, _chr: kurses.stream.CharacterAttribute) -> sdl2.SDL_Renderer:
        _cast_depth_colors = functools.partial(kurses.colors.cast_depth_colors, bits=self.depth_colors)
        _get_style_sdl2 = functools.partial(get_style_sdl2, all_styles=self.__ALL_FONT_STYLES)

        if _chr not in self.allocate_textures:
            self.allocate_textures[_chr] = create_texture_chr_sdl2(
                self.font, self.__default_render_method(),
                surface,
                _chr.code,
                _cast_depth_colors(_chr.foreign),
                _cast_depth_colors(_chr.background),
                _get_style_sdl2(_chr)
            )

        return self.allocate_textures[_chr]
