# load modules
import random

from kurses import VirtualTerminal

# instance Virtual console
console = VirtualTerminal("ModernDOS8x16.ttf")
buffer = console.stream  # get buffer console

# define global variables
x, y = 0, 0


# define loop function
def loop():
    global x, y

    buffer.clrscr()
    buffer.resetall()  # restore default attributes in the buffer console

    # check key pressed
    if "w" in console.keyspressed():
        y -= 1
    elif "s" in console.keyspressed():
        y += 1
    if "a" in console.keyspressed():
        x -= 1
    elif "d" in console.keyspressed():
        x += 1

    # all draw events of string with random colors
    _x = x

    for _c in "Random color":
        buffer.set_foreign_color(tuple(random.randint(0, 255) for _ in range(3)))
        buffer.set_background_color(tuple(random.randint(0, 255) for _ in range(3)))
        buffer.gotoxy(_x, y)  # set position
        buffer.cputs(_c)  # print character into buffer console
        _x += 1


# set loop function
console.set_target(loop)

# run all program
console.main_loop()
