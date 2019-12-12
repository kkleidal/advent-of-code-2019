from intcode import IntCodeProgram, ProgramExitted, TurtleRobot

with open("input.txt", "r") as f:
    program = IntCodeProgram(list(map(int, f.read().strip().split(","))))

robot = TurtleRobot(program, start_panel=1)
robot.run()
print(robot.render())
