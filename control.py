from trilobot import *
import os
import time


def dispatch_command(que, speed):
    print(f"Start trilobot process {os.getpid()}")
    tbot = Trilobot()
    print(tbot, que)
    while True:
        if not que.empty():
            tbot.set_button_led(2, True)
            time.sleep(.1)
            tbot.set_button_led(2, False)
            time.sleep(.1)

            command = que.get()
            print(f'Command: {command}')
            if command == "exit":
                tbot.stop()
                break
            elif command == "forward":
                tbot.forward(speed)
            elif command == "reverse":
                tbot.backward(speed)
            elif command == "left":
                tbot.turn_left(speed)
            elif command == "right":
                tbot.turn_right(speed)
            else:
                tbot.stop()
        else:
            tbot.set_button_led(3, True)
            time.sleep(.1)
            tbot.set_button_led(3, False)
            time.sleep(.1)

    print("End trilobot process")

