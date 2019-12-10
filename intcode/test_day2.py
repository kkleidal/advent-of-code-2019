import os

from . import IntCodeProgram

dir_path = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(dir_path, "day2_input.txt"), "r") as f:
    day2_input = list(map(int, f.read().strip().split(",")))

def day2_program(noun, verb):
    program = list(day2_input)
    program[1] = noun
    program[2] = verb
    return program

def test_day2_part1():
    process = IntCodeProgram(day2_program(12, 2)).process()
    outputs = list(process.run([]))
    assert len(outputs) == 0
    assert process.memory[0] == 5866663

def test_day2_part2():
    found = None
    for noun in range(100):
        for verb in range(100):
            process = IntCodeProgram(day2_program(noun, verb)).process()
            outputs = list(process.run([]))
            assert len(outputs) == 0
            if process.memory[0] == 19690720:
                found = (noun, verb)
                break
        if found:
            break
    assert 100 * found[0] + found[1] == 4259
