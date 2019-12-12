from intcode import IntCodeProgram, ProgramExitted, TurtleRobot

with open("input.txt", "r") as f:
    program = IntCodeProgram(list(map(int, f.read().strip().split(","))))

robot = TurtleRobot(program)
robot.run()
print(len(robot.canvas))
