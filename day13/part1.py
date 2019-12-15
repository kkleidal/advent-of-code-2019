from game import IntCodeProgram, ArcadeGame

with open("input.txt", "r") as f:
    program = IntCodeProgram(list(map(int, f.read().strip().split(","))))
    game = ArcadeGame(program)
    game.run()
    print(game.count_blocks())
