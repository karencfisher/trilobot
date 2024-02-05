from trilobot import *


def dispatch_command(que, speed):
    tbot = Trilobot()
    while True:
        # If there is a command in the queue, dequeue and execute it
        if not que.empty():
            command = que.get()
            if command == "exit":
                tbot.stop()
                break
            elif command == "forward":
                tbot.forward(speed)
            elif command == "reverse":
                tbot.backward(speed)
            elif command == "turn-left":
                tbot.turn_left(speed)
            elif command == "turn-right":
                tbot.turn_right(speed)
            elif command == "left-forward":
                tbot.curve_forward_left(speed)
            elif command == "right-forward":
                tbot.curve_forward_right(speed)
            elif command == "left-reverse":
                tbot.curve_backward_left(speed)
            elif command == "right-reverse":
                tbot.curve_backward_right(speed)
            else:
                tbot.stop()

