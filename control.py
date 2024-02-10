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
                tbot.set_motor_speeds()
            elif command == "turn-right":
                tbot.turn_right(speed)
            elif command == "left-forward":
                tbot.set_motor_speeds(0.7 * speed, speed)
            elif command == "right-forward":
                tbot.set_motor_speeds(speed, 0.7 * speed)
            elif command == "left-reverse":
                tbot.set_motor_speeds(-0.7 * speed, -speed)
            elif command == "right-reverse":
                tbot.set_motor_speeds(-speed, -0.7 * speed)
            else:
                tbot.stop()

