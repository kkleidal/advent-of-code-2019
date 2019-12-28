import numpy as np
import scipy.signal
from collections import defaultdict

class BugWorld:
    @classmethod
    def parse(cls, input_string):
        lines = [line for line in (line.strip() for line in input_string.strip().split("\n"))
                 if len(line) > 0]
        H = len(lines)
        W = len(lines[0])
        arr = np.zeros([H, W], dtype=np.bool)
        for y, line in enumerate(lines):
            for x, c in enumerate(line):
                if c == "#":
                    arr[y, x] = True
        return cls(arr)

    def __init__(self, mask):
        self.mask = mask

    def __hash__(self):
        x, y = np.nonzero(self.mask)
        return hash((tuple(x.tolist()), tuple(y.tolist())))

    def copy(self):
        return BugWorld(self.mask.copy())

    def __eq__(self, other):
        if isinstance(other, BugWorld):
            return np.all(self.mask == other.mask)
        else:
            return NotImplementedError

    def display(self):
        H, W = self.mask.shape
        for y in range(H):
            for x in range(W):
                print("#" if self.mask[y, x] else ".", end="")
            print()

    def step(self):
        kernel = np.array([
            [0, 1, 0],
            [1, 0, 1],
            [0, 1, 0]])
        adjacent_counts = scipy.signal.convolve2d(
            self.mask.astype(np.uint8), kernel, mode="same")
        die = self.mask & (adjacent_counts != 1)
        infested = ~self.mask & ((adjacent_counts == 1) | (adjacent_counts == 2))
        self.mask[die] = False
        self.mask[infested] = True

    def find_repeat(self):
        initial_world = self
        encountered_before = defaultdict(set)
        encountered_before[hash(initial_world)].add(0)
        world = initial_world.copy()
        T = 0
        while True:
            world.step()
            T += 1
            my_hash = hash(world)
            if my_hash in encountered_before:
                possible_ts = encountered_before[my_hash]
                replay_world = initial_world.copy()
                for t in range(max(possible_ts)):
                    if t in possible_ts:
                        if world == replay_world:
                            return t, T, world
                    replay_world.step()
            encountered_before[my_hash].add(T)

    @property
    def biodiversity(self):
        current = 0
        for value in reversed(self.mask.flatten()):
            current = (current << 1) | (1 if value else 0)
        return current

if __name__ == "__main__":
    with open("input.txt", "r") as f:
        world = BugWorld.parse(f.read())
    _, _, world = world.find_repeat()
    print(world.biodiversity)
