import sys

from intcode import IntCodeProgram

day9_input = list(map(int, sys.stdin.read().strip().split(",")))
print(list(IntCodeProgram(day9_input).process().run([2]))[0])
