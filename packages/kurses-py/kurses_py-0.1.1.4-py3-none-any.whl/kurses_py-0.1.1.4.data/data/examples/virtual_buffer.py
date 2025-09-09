# load module
import kurses.stream
from kurses import VirtualTerminal, StreamBuffer

# instance Virtual console
term = VirtualTerminal(font_filename="ModernDOS8x16.ttf")  # load font resources
buffer_0 = term.stream  # get main buffer console
buffer_1 = StreamBuffer(80, 30, sx=2, sy=2)

buffer_0.type_cursor = kurses.stream.TypeCursor.VERTICAL
buffer_1.type_cursor = kurses.stream.TypeCursor.VERTICAL


# define loop function
def loop():
    buffer_1.resetall()  # restore default attributes in the buffer console

    # set attributes of second string
    buffer_0.gotoxy(10, 2)  # go to position x: 5, y: 1
    buffer_0.italic(True)  # set true italic
    buffer_0.print("world!")  # print into buffer console, again

    # set attributes of first string
    buffer_1.gotoxy(0, 0)  # go to position x: 0, y: 0
    buffer_1.set_background_color((255, 255, 255))  # set background color characters
    buffer_1.set_foreign_color((0, 0, 0))  # set foreign color
    buffer_1.print("Hello")  # print into buffer console


# append virtual buffer
term.streams.append(buffer_1)

# set loop function
term.set_target(loop)

# run all program
term.main_loop()
