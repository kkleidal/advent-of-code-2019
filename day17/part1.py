import numpy as np
import scipy.signal

from intcode import IntCodeProgram

def find_intersects(input_string):
    inputs = np.array([[1 if c == "#" else 0 for c in line.strip()]
                      for line in input_string.strip().split("\n")])
    kernel = np.array([
        [0, 1, 0],
        [1, 1, 1],
        [0, 1, 0]])
    y, x = np.nonzero(scipy.signal.convolve2d(inputs, kernel, mode="same") == 5)
    return np.stack([x, y], 1)

def calibration(intersects):
    return np.dot(intersects[:,0], intersects[:,1])

def get_board(program):
    process = program.process()
    lines = []
    line = []
    for output in process.run():
        c = chr(output)
        if c == "\n":
            lines.append("".join(line))
            line = []
        else:
            line.append(c)
    if len(line) > 0:
        lines.append("".join(line))
    return "\n".join(lines)

with open("input.txt", "r") as f:
    program = IntCodeProgram(list(map(int, f.read().strip().split(","))))
    print(calibration(find_intersects(get_board(program))))
