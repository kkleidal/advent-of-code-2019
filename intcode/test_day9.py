import os

from . import IntCodeProgram

def test_example1_quine():
    code = [109,1,204,-1,1001,100,1,100,1008,100,16,101,1006,101,0,99]
    outputs = list(IntCodeProgram(code).process().run([]))
    assert tuple(outputs) == tuple(code)

def test_example2():
    code = [1102,34915192,34915192,7,4,7,99,0]
    outputs = list(IntCodeProgram(code).process().run([]))
    assert len(outputs) == 1
    assert outputs[0] >= 1e15
    assert outputs[0] < 1e16

def test_example3():
    code = [104,1125899906842624,99]
    outputs = list(IntCodeProgram(code).process().run([]))
    assert len(outputs) == 1
    assert outputs[0] == code[1]

dir_path = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(dir_path, "day9_input.txt"), "r") as f:
    day9_input = list(map(int, f.read().strip().split(",")))

def test_day9_part1():
    outputs = list(IntCodeProgram(day9_input).process().run([1]))
    assert len(outputs) == 1
    assert outputs[0] == 2932210790

def test_day9_part2():
    outputs = list(IntCodeProgram(day9_input).process().run([2]))
    assert len(outputs) == 1
    assert outputs[0] == 73144
