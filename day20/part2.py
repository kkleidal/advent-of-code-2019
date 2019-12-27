from part1 import Maze

if __name__ == "__main__":
    with open("input.txt", "r") as f:
        maze = Maze.parse(f.read())
    print(maze.recursive_shortest_path())
