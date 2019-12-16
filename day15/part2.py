import time
import keyboard
from robot import IntCodeProgram, Robot, Environment, WallFollower

visualize = False
interactive = False

with open("input.txt", "r") as f:
    code = list(map(int, f.read().strip().split(",")))
program = IntCodeProgram(code)
robot = Robot(program)
env = Environment(robot)
follower = WallFollower(env)
try:
    while True:
        if visualize:
            env.terminal_render()
            time.sleep(0.001)
            if interactive:
                while True:
                    inp = keyboard.read_key()
                    keys = {
                        "h": 3,
                        "k": 2,
                        "j": 1,
                        "l": 4,
                    }
                    if inp in keys:
                        env.step(keys[inp])
                        break
            else:
                follower.step()
        else:
            follower.step()
except StopIteration:
    print(env.find_farthest_room_from_oxygen())
