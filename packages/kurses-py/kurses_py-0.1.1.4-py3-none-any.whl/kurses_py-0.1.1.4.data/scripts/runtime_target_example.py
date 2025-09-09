import random
import typing

from kurses import VirtualTerminal
from kurses.events import EventTargetRuntime

term = VirtualTerminal(font_filename="ModernDOS8x16.ttf")
stream = term.stream


class MyTarget(EventTargetRuntime):
    def __init__(self):
        self.position = 0, 0

    def load(self):
        term.resizable = True
        stream.resetall()

    def update(self, dt):
        x, y = self.position

        stream.clrscr()

        stream.gotoxy(x, y)
        stream.set_foreign_color(tuple(random.randint(0, 255) for _ in range(3)))
        stream.set_background_color(tuple(random.randint(0, 255) for _ in range(3)))
        stream.print("Hello\n")

        stream.gotoxy(x + 5, y + 1)
        stream.italic(True)
        stream.print("world!")

    def key_down(self, key: chr):
        print(f"Key down: {key}")

    def key_up(self, key: chr):
        print(f"Key up: {key}")

    def mouse(self, position: typing.Tuple[int, int], click: int):
        self.position = position

    def exit(self):
        stream.resetall()
        stream.gotoxy(0, 0)
        stream.set_foreign_color((255, 255, 255))
        stream.print("Goodbye")


if __name__ == "__main__":
    term.set_runtime(MyTarget)

    term.main_loop()
