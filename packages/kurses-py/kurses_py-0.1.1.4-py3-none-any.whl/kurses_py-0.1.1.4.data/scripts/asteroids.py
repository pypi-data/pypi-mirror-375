import random
import time

import kurses.stream
from kurses import VirtualTerminal, StreamBuffer
from kurses.font_resources import QualityFont

SHIP = """\
 |
/0\\
"""


def draw_ship(x, y, buffer):
    buffer.gotoxy(x, y)
    buffer.set_foreign_color((255, 0, 255))
    buffer.print(SHIP)
    buffer.resetall()


def random_asteroid(_x=(0, 80), _y=(0, 30)):
    return (
        random.randint(*_x),
        random.randint(*_y),
        random.randint(1, 2),
        random.sample([(255, 255, 255), (255, 255, 0), (0, 0, 255), (0, 255, 255), (255, 0, 0), (0, 255, 0)], 1)[0],
        random.sample("*", 1)[0],
    )


console = VirtualTerminal(font_filename="ModernDOS8x16.ttf", quality=QualityFont.LCD)

main_buffer = console.stream

score_buffer = StreamBuffer(40, 15, sx=2, sy=2, type_cursor=kurses.stream.TypeCursor.RECT)
score_buffer.x = 0
score_buffer.y = 0
score_buffer.type_cursor = kurses.stream.TypeCursor.EMPTY

asteroids = [random_asteroid() for _ in range(5)]

x_ship, y_ship = random.randint(0, 70), random.randint(0, 30)

life, score = 100, 0
shoots = []


def loop():
    global x_ship, y_ship, life, score
    rows, columns = main_buffer.buffersize

    time.sleep(0.025)

    for stream in console.streams:
        stream.clrscr()

    if life > 0:
        if score >= 10:
            _msg = "You win!"
            main_buffer.bold(True)
            main_buffer.cputsxy(40 - (len(_msg) // 2), 15, _msg)

            main_buffer.resetall()

            _msg = "Press SPACE for play again"
            main_buffer.set_foreign_color((255, 255, 0))
            main_buffer.cputsxy(40 - (len(_msg) // 2), 16, _msg)

            main_buffer.resetall()

            if "space" in console.keyspressed():
                life = 100

        else:
            if "w" in console.keyspressed() and y_ship >= 0:
                y_ship -= 1
            elif "s" in console.keyspressed() and y_ship <= rows - 3:
                y_ship += 1

            if "a" in console.keyspressed() and x_ship >= 0:
                x_ship -= 1
            elif "d" in console.keyspressed() and x_ship <= columns - 3:
                x_ship += 1

            if "space" in console.keyspressed():
                if len(shoots) == 0:
                    shoots.append((x_ship, y_ship))

            draw_ship(x_ship, y_ship, main_buffer)

            for i, (_x, _y, speed, color, c) in enumerate(asteroids):
                main_buffer.set_foreign_color(color)
                main_buffer.putchxy(_x, _y, c)
                main_buffer.resetall()

                _y += speed

                if _y > rows:
                    _x = random.randint(0, columns)
                    _y = 0

                if _x in range(x_ship, x_ship + 3) and _y in range(y_ship, y_ship + 3):
                    if c == '.':
                        score += 1
                    else:
                        life -= 5

                    asteroids.remove(asteroids[i])
                    asteroids.append(random_asteroid(_y=(0, 0)))
                else:
                    asteroids[i] = _x, _y, speed, color, c

            for i, (_x, _y) in enumerate(shoots):
                _y -= 1
                main_buffer.set_foreign_color((0, 255, 0))
                main_buffer.putchxy(_x, _y, '0')
                main_buffer.resetall()

                if _y < 0:
                    shoots.remove(shoots[i])
                else:
                    shoots[i] = _x, _y

            for i, (_x, _y) in enumerate(shoots):
                for j, (_xx, _yy, speed, color, c) in enumerate(asteroids):
                    if _x == _xx and _y == _yy:
                        asteroids.remove(asteroids[j])
                        score += 1

            _msg = f"life: {life}"
            score_buffer.gotoxy(0, 0)
            score_buffer.bold(True)
            score_buffer.set_background_color((255, 0, 0))
            score_buffer.set_foreign_color((255, 255, 0))
            score_buffer.print(_msg)
            score_buffer.resetall()

            _msg = f"score: {score}"
            score_buffer.gotoxy(40 - len(_msg), 0)
            score_buffer.bold(True)
            score_buffer.set_background_color((0, 0, 255))
            score_buffer.set_foreign_color((255, 255, 255))
            score_buffer.print(_msg)
            score_buffer.resetall()

    else:
        _msg = "You lost!"
        main_buffer.bold(True)
        main_buffer.cputsxy(40 - (len(_msg) // 2), 15, _msg)

        main_buffer.resetall()

        _msg = "Press SPACE for play again"
        main_buffer.set_foreign_color((255, 0, 0))
        main_buffer.cputsxy(40 - (len(_msg) // 2), 16, _msg)

        main_buffer.resetall()

        if "space" in console.keyspressed():
            life = 100


if __name__ == '__main__':
    console.streams.append(score_buffer)

    console.title = "Asteroids"
    console.set_target(loop)
    console.main_loop()
