import numpy as np
import os

from . import IntCodeProgram, TurtleRobot

part2_output = '''
.#....###..####.#..#.#.....##..#..#.###....
.#....#..#....#.#.#..#....#..#.#..#.#..#...
.#....#..#...#..##...#....#....####.#..#...
.#....###...#...#.#..#....#.##.#..#.###....
.#....#....#....#.#..#....#..#.#..#.#.#....
.####.#....####.#..#.####..###.#..#.#..#...
'''

dir_path = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(dir_path, "day11_input.txt"), "r") as f:
    day11_input = list(map(int, f.read().strip().split(",")))

def test_part1():
    program = IntCodeProgram(day11_input)
    robot = TurtleRobot(program, start_panel=0)
    robot.run()
    assert len(robot.canvas) == 2064

def test_part2():
    expected = np.stack([np.array([1 if c == "#" else 0 for c in line])
                         for line in part2_output.strip().split("\n")], axis=0)
    program = IntCodeProgram(day11_input)
    robot = TurtleRobot(program, start_panel=1)
    robot.run()
    assert np.all(robot.array() == expected)
