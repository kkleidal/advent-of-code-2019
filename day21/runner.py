import argparse
from intcode import IntCodeProgram, ProgramExitted

parser = argparse.ArgumentParser()
parser.add_argument("script")
args = parser.parse_args()

with open("intcode.txt", "r") as f:
    program = IntCodeProgram(list(map(int, f.read().strip().split(","))))

with open(args.script, "r") as f:
    script = f.read().strip() + "\n"

process = program.process()
script_iter = iter(script)
try:
    while True:
        process.step_until_interrupt()
        if process.waiting_for_input():
            c = next(script_iter)
            print(c, end="", flush=True)
            process.send(ord(c))
        else:
            x = process.recv()
            try:
                print(chr(x), end="", flush=True)
            except ValueError:
                print("You won: %d" % x, flush=True)
                break
except ProgramExitted:
    print("You lost.")
