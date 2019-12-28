import argparse
from intcode import IntCodeProgram, ProgramExitted

parser = argparse.ArgumentParser()
parser.add_argument("prefix_scripts", nargs="*")
args = parser.parse_args()

with open("intcode.txt", "r") as f:
    program = IntCodeProgram(list(map(int, f.read().strip().split(","))))

process = program.process()
prefix = []
for script in args.prefix_scripts:
    with open(script, "r") as f:
        prefix.extend(f.read().strip().split("\n"))
try:
    while True:
        process.step_until_interrupt()
        if process.waiting_for_input():
            print(">>> ", end="", flush=True)
            if len(prefix) > 0:
                cmd = prefix.pop(0).strip()
                print(cmd)
            else:
                cmd = input()
            for c in cmd.strip():
                process.send(ord(c))
            process.send(ord("\n"))
        else:
            x = process.recv()
            try:
                print(chr(x), end="", flush=True)
            except ValueError:
                print("You won: %d" % x, flush=True)
                break
except ProgramExitted:
    print("Program exitted.")
