import random

from kurses import VirtualTerminal
from kurses.term import Rendering

if __name__ == "__main__":
    console = VirtualTerminal("ModernDOS8x16.ttf", type_rendering=Rendering.HARDWARE)
    console.resizable = True

    x, y = 0, 0

    def main():
        global x, y

        term = console.streams[0]

        term.clrscr()

        if "w" in console.keyspressed():
            y -= 1
        elif "s" in console.keyspressed():
            y += 1

        if "a" in console.keyspressed():
            x -= 1
        elif "d" in console.keyspressed():
            x += 1

        term.resetall()
        term.set_background_color((0, 255, 0))
        term.set_foreign_color((225, 23, 155))
        term.putrect(0, 0, 5, 30)
        term.cputsxy(0, 0, "Hello world")

        term.italic(True)
        term.bold(True)
        term.set_background_color((255, 255, 255))
        term.set_foreign_color((0, 0, 0))
        term.cputsxy(6, 1, "Italic and bold text")

        term.resetall()

        term.underline(True)
        term.cputsxy(16, 16, "Underline text")

        term.resetall()

        term.strikethrough(True)
        term.set_foreign_color((255, 0, 0))
        term.cputsxy(24, 24, "Strikethrough text")

        term.resetall()
        _x = x

        for _c in "Random color":
            term.set_foreign_color(tuple(random.randint(0, 255) for _ in range(3)))
            term.set_background_color(tuple(random.randint(0, 255) for _ in range(3)))
            term.gotoxy(_x, y)
            term.cputs(_c)
            _x += 1

    console.set_target(main)
    console.main_loop()
