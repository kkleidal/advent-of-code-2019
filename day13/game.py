from abc import ABC, abstractmethod
from collections import defaultdict
import time
import numpy as np

from intcode import IntCodeProgram, ProgramExitted, ProcessHook

class Tile(ABC):
    registry = {}

    @staticmethod
    def register(cls):
        Tile.registry[cls.code] = cls()
        return cls

    def __eq__(self, other):
        return isinstance(other, Tile) and other.__class__ == self.__class__

    def __hash__(self):
        return hash(self.__class__)

    @abstractmethod
    def render(self):
        raise NotImplementedError

@Tile.register
class EmptyTile(Tile):
    code = 0

    def render(self):
        return " "

@Tile.register
class WallTile(Tile):
    code = 1

    def render(self):
        return "█"

@Tile.register
class BlockTile(Tile):
    code = 2

    def render(self):
        return "x"

@Tile.register
class HorizontalPaddleTile(Tile):
    code = 3

    def render(self):
        return "-"

@Tile.register
class BallTile(Tile):
    code = 4

    def render(self):
        return "o"

class Screen:
    def __init__(self):
        self._screen = defaultdict(lambda: EmptyTile())
        self._min_x = None
        self._max_x = None
        self._min_y = None
        self._max_y = None

    def _touch(self, pos):
        x, y = pos
        if self._min_x is None or x < self._min_x:
            self._min_x = x
        if self._max_x is None or x > self._max_x:
            self._max_x = x
        if self._min_y is None or y < self._min_y:
            self._min_y = y
        if self._max_y is None or y > self._max_y:
            self._max_y = y

    def __setitem__(self, pos, value):
        assert len(pos) == 2
        assert isinstance(value, Tile)
        self._touch(pos)
        self._screen[pos] = value

    def __getitem__(self, pos):
        return self._screen[pos]

    def __iter__(self):
        for pos, tile in self._screen.items():
            if not isinstance(tile, EmptyTile):
                yield pos, tile

    def array(self):
        return np.array([[self._screen[(x, y)].code for x in range(self._min_x, self._max_x + 1)]
                         for y in range(self._min_y, self._max_y + 1)])

    def render(self):
        lines = []
        for y in range(self._min_y, self._max_y + 1):
            line = []
            for x in range(self._min_x, self._max_x + 1):
                line.append(self._screen[(x, y)].render())
            lines.append("".join(line))
        return "\n".join(lines)

class GameHook(ProcessHook):
    def on_game_screen_updated(self, game, pos, tile):
        pass

    def on_game_score_updated(self, game, score):
        pass

class ArcadeGame:
    def __init__(self, program, hooks=[]):
        self.process = program.process(hooks=hooks)
        self.hooks = list(hooks)
        self.screen = Screen()
        self.score = 0
        self.t = 0
        self.is_finished = False

    def add_hook(self, hook):
        self.hooks.append(hook)

    def insert_quarters(self):
        self.process.memory[0] = 2

    def finished(self):
        return self.is_finished

    def waiting_for_input(self):
        return self.process.waiting_for_input()

    def step(self, visualizing=False):
        self.process.step_until_interrupt()
        while not self.process.waiting_for_input():
            x, y, tile = [self.process.recv() for _ in range(3)]
            if x == -1 and y == 0:
                self.score = tile
                for hook in self.hooks:
                    hook.on_game_score_updated(self, self.score)
            else:
                pos = (x, y)
                tile = Tile.registry[tile]
                if isinstance(tile, BallTile):
                    self.t += 1
                self.screen[pos] = tile
                for hook in self.hooks:
                    hook.on_game_screen_updated(self, pos, tile)
            self.process.step_until_interrupt()
            if visualizing:
                break

    def safe_step(self):
        if self.is_finished:
            return
        try:
            self.step()
        except ProgramExitted:
            self.is_finished = True

    def velocity(self):
        return tuple(self.process.memory[x] for x in [390, 391])

    def array(self):
        return self.screen.array()

    def send(self, input_value):
        assert input_value in (-1, 0, 1)
        assert self.process.waiting_for_input()
        self.process.send(input_value)

    def render(self):
        return "\n".join([self.screen.render(), "Score: %d" % self.score])

    def terminal_render(self):
        print(chr(27) + "[2J")
        print(self.render(), flush=True)

    def objects(self):
        return iter(self.screen)

    def count_blocks(self):
        count = 0
        for _, obj in self.objects():
            if isinstance(obj, BlockTile):
                count += 1
        return count

    def irun(self):
        try:
            while True:
                self.step()
                yield
        except ProgramExitted:
            self.is_finished = True

    def run(self):
        for _ in self.irun():
            pass
