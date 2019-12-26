import numpy as np
import scipy.signal

from intcode import IntCodeProgram

def get_array(input_string):
    return np.array([[0 if c == "." else 1 for c in line.strip()]
                      for line in input_string.strip().split("\n")])

def find_intersects_from_array(array):
    kernel = np.array([
        [0, 1, 0],
        [1, 1, 1],
        [0, 1, 0]])
    y, x = np.nonzero(scipy.signal.convolve2d(array, kernel, mode="same") == 5)
    return np.stack([x, y], 1)

def find_intersects(input_string):
    return find_intersects_from_array(get_array(input_string))

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

if __name__ == "__main__":
    with open("input.txt", "r") as f:
        program = IntCodeProgram(list(map(int, f.read().strip().split(","))))
        print(calibration(find_intersects(get_board(program))))
