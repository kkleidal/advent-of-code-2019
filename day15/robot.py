import pdb
from collections import defaultdict, deque
from intcode import IntCodeProgram
import numpy as np
import keyboard
import time

class Robot:
    def __init__(self, program):
        self.process = program.process()
        self.process.step_until_interrupt()

    def move(self, move):
        self.process.send(move)
        return self.process.recv()

class Tiles:
    UNKNOWN = 0
    EMPTY = 1
    WALL = 2

class Environment:
    def __init__(self, robot):
        self.robot = robot
        self.position = (0, 0)
        self.environment = defaultdict(int)
        self.environment[self.position] = Tiles.EMPTY
        self.oxygen = None

    def step(self, input):
        moved_pos = (
            self.position[0] + {1: 0, 2: 0, 3: -1, 4: 1}[input],
            self.position[1] + {1: 1, 2: -1, 3: 0, 4: 0}[input],
        )
        output = self.robot.move(input)
        if output == 0:
            self.environment[moved_pos] = Tiles.WALL
        elif output == 1:
            self.environment[moved_pos] = Tiles.EMPTY
            self.position = moved_pos
        elif output == 2:
            self.environment[moved_pos] = Tiles.EMPTY
            self.oxygen = moved_pos
            self.position = moved_pos
        else:
            raise NotImplementedError

    def array(self):
        min_x = min(min(pos[0] for pos in self.environment), self.position[0])
        min_y = min(min(pos[1] for pos in self.environment), self.position[1])
        max_x = max(max(pos[0] for pos in self.environment), self.position[0])
        max_y = max(max(pos[1] for pos in self.environment), self.position[1])
        if self.oxygen is not None:
            min_x = min(min_x, self.oxygen[0])
            min_y = min(min_y, self.oxygen[1])
            max_x = max(max_x, self.oxygen[0])
            max_y = max(max_y, self.oxygen[1])
        out = []
        for y in range(min_y, max_y + 1):
            line = []
            for x in range(min_x, max_x + 1):
                line.append(self.environment[(x, y)])
            line = np.array(line)
            out.append(line)
        arr = np.stack(out, 0)
        if self.oxygen is not None:
            arr[(self.oxygen[1] - min_y, self.oxygen[0] - min_x)] = 4
        if self.position is not None:
            arr[(self.position[1] - min_y, self.position[0] - min_x)] = 3
        return arr

    def render(self):
        return "\n".join("".join([" ", ".", "█", "@", "*"][x] for x in line) for line in self.array().tolist())

    def terminal_render(self):
        print(chr(27) + "[2J")
        print(self.render(), flush=True)

    def find_shortest_distance(self):
        start = (0, 0)
        end = self.oxygen
        assert end is not None
        q = deque([(self.position, 0, set())])
        while q:
            pos, dist, history = q.pop()
            if pos == end:
                return dist
            for dx, dy in [(1, 0), (0, 1), (0, -1), (-1, 0)]:
                new_pos = (pos[0] + dx, pos[1] + dy)
                if new_pos in history:
                    continue
                if self.environment[new_pos] == Tiles.EMPTY:
                    new_history = set(history)
                    new_history.add(new_pos)
                    q.appendleft((new_pos, dist + 1, new_history))
        return None

    def extract_graph(self):
        nodes = set()
        adjacency = {}
        for pos, tile in self.environment.items():
            if tile == Tiles.EMPTY:
                neighbors = set()
                for dx, dy in [(1, 0), (0, 1), (0, -1), (-1, 0)]:
                    new_pos = (pos[0] + dx, pos[1] + dy)
                    if self.environment[new_pos] == Tiles.EMPTY:
                        neighbors.add(new_pos)
                nodes.add(pos)
                adjacency[pos] = neighbors
        return nodes, adjacency

    def find_farthest_room_from_oxygen(self):
        nodes, adjacency = self.extract_graph()
        shortest = {}
        q = deque([(self.oxygen, 0, set())])
        while q:
            pos, dist, history = q.pop()
            if pos in shortest:
                continue
            else:
                shortest[pos] = dist
            for new_pos in adjacency[pos]:
                if new_pos in history:
                    continue
                new_history = set(history)
                new_history.add(new_pos)
                q.appendleft((new_pos, dist + 1, new_history))
        return max(shortest.values())


class Directions:
    NORTH = 2
    SOUTH = 1
    EAST = 3
    WEST = 4

left_turn = {
    Directions.NORTH: Directions.WEST,
    Directions.WEST: Directions.SOUTH,
    Directions.SOUTH: Directions.EAST,
    Directions.EAST: Directions.NORTH,
}
right_turn = {v: k for k, v in left_turn.items()}

class WallFollower:
    def __init__(self, env):
        self.env = env
        self.state = 0
        self.initial_state = None
        self.direction = None

    def step(self):
        if self.state == 0:
            pos = self.env.position
            self.env.step(Directions.NORTH)
            if pos == self.env.position:
                # Hit a wall, keep it on my right side
                self.state = 1
                self.direction = Directions.WEST
        elif self.state == 1:
            pos = self.env.position
            state = (pos, self.direction)
            if self.initial_state is None:
                self.initial_state = state
            elif self.initial_state == state:
                raise StopIteration
            self.env.step(self.direction)
            if pos == self.env.position:
                # Hit a wall, keep it on my right side
                self.direction = left_turn[self.direction]
            else:
                # Didn't hit a wall, try to turn right
                self.direction = right_turn[self.direction]
