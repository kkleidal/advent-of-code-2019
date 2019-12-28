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

    def __init__(self, mask, masks=None, all_but_center=None, center=None, shape=None):
        self.shape = shape or mask.shape
        self.masks = masks or {0: mask}
        self.center = center or (mask.shape[0] // 2, mask.shape[1] // 2)
        if all_but_center is None:
            self.all_but_center = np.ones(mask.shape, dtype=np.bool)
            self.all_but_center[self.center] = False
        else:
            self.all_but_center = all_but_center

    def bugs(self):
        for level, mask in self.masks.items():
            y, x = np.nonzero(mask)
            for y, x in zip(y, x):
                if (y, x) == self.center:
                    continue
                yield (y, x)

    def __hash__(self):
        return hash(tuple(sorted(self.bugs())))

    def copy(self):
        return BugWorld(None, masks={level: mask.copy() for level, mask in self.masks.items()},
                       all_but_center=self.all_but_center,
                       center=self.center,
                       shape=self.shape)

    def __eq__(self, other):
        if isinstance(other, BugWorld):
            if set(self.masks) != set(other.masks):
                return False
            for level in self.masks:
                if not np.all(self.masks[level] == other.masks[level]):
                    return False
            return True
        else:
            return NotImplementedError

    def display(self):
        for level in sorted(self.masks):
            print("Level %d:" % level)
            mask = self.masks[level]
            H, W = mask.shape
            for y in range(H):
                for x in range(W):
                    if (y, x) == self.center:
                        print("?", end="")
                    else:
                        print("#" if mask[y, x] else ".", end="")
                print()
            print()

    def count_adjacent(self, level, y, x, base_adjacent):
        inside_level = level + 1
        outside_level = level - 1

        has_inside = inside_level in self.masks
        has_outside = outside_level in self.masks

        adjacent = base_adjacent
        if has_outside:
            if y == 0:
                adjacent += 1 if self.masks[outside_level][1, 2] else 0
            elif y == 4:
                adjacent += 1 if self.masks[outside_level][3, 2] else 0
            if x == 0:
                adjacent += 1 if self.masks[outside_level][2, 1] else 0
            elif x == 4:
                adjacent += 1 if self.masks[outside_level][2, 3] else 0
        if has_inside:
            if (y, x) == (1, 2):
                adjacent += np.count_nonzero(self.masks[inside_level][0,:])
            elif (y, x) == (2, 1):
                adjacent += np.count_nonzero(self.masks[inside_level][:,0])
            elif (y, x) == (3, 2):
                adjacent += np.count_nonzero(self.masks[inside_level][-1,:])
            elif (y, x) == (2, 3):
                adjacent += np.count_nonzero(self.masks[inside_level][:,-1])
        return adjacent

    def step(self):
        H, W = self.shape
        die = set()
        infested = set()
        max_level = max(self.masks)
        min_level = min(self.masks)
        if np.any(self.masks[max_level]):
            self.masks[max_level + 1] = np.zeros([H, W], dtype=np.bool)
        if np.any(self.masks[min_level]):
            self.masks[min_level - 1] = np.zeros([H, W], dtype=np.bool)
        kernel = np.array([
            [0, 1, 0],
            [1, 0, 1],
            [0, 1, 0]])
        for level, mask in sorted(self.masks.items()):
            adjacent_counts = scipy.signal.convolve2d(
                mask.astype(np.uint8), kernel, mode="same")
            for y in range(H):
                for x in range(W):
                    if (y, x) == self.center:
                        continue
                    bug = mask[y, x]
                    adjacent = self.count_adjacent(level, y, x, adjacent_counts[y, x])
                    if not bug and adjacent in (1, 2):
                        infested.add((level, y, x))
                    if bug and adjacent != 1:
                        die.add((level, y, x))
        for level, y, x in die:
            self.masks[level][y, x] = False
        for level, y, x in infested:
            self.masks[level][y, x] = True

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

if __name__ == "__main__":
    with open("input.txt", "r") as f:
        world = BugWorld.parse(f.read())
    for t in range(200):
        world.step()
    print(sum(1 for _ in world.bugs()))
