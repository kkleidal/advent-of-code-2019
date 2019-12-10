import os

from . import IntCodeProgram

dir_path = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(dir_path, "day5_input.txt"), "r") as f:
    day5_input = list(map(int, f.read().strip().split(",")))

def test_day5_part1():
    outputs = list(IntCodeProgram(day5_input).process().run([1]))
    assert len(outputs) == 10
    assert all(x == 0 for x in outputs[:9])
    assert outputs[9] == 16209841

def test_day5_part2():
    outputs = list(IntCodeProgram(day5_input).process().run([5]))
    assert len(outputs) == 1
    assert outputs[0] == 8834787
