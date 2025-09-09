# load module
from kurses import VirtualTerminal

# instance Virtual console
term = VirtualTerminal(font_filename="ModernDOS8x16.ttf")  # load font resources
stream = term.stream  # get main buffer console


# define loop function
def loop():
    stream.resetall()  # restore default attributes in the buffer console

    # set attributes of first string
    stream.gotoxy(0, 0)  # go to position x: 0, y: 0
    stream.set_background_color((255, 255, 255))  # set background color characters
    stream.set_foreign_color((0, 0, 0))  # set foreign color
    stream.print("Hello\n")  # print into buffer console

    # set attributes of second string
    stream.gotoxy(5, 1)  # go to position x: 5, y: 1
    stream.italic(True)  # set true italic
    stream.print("world!")  # print into buffer console, again


# set loop function
term.set_target(loop)

# run all program
term.main_loop()
