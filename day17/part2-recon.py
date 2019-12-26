import numpy as np
import scipy
from collections import defaultdict
from part1 import get_array, find_intersects_from_array

with open("map.txt", "r") as f:
    map_string = f.read()

def get_array(input_string):
    return np.array([[0 if c == "." else (1 if c == "#" else 2) for c in line.strip()]
                      for line in input_string.strip().split("\n")])

def find_intersects_from_array(array):
    kernel = np.array([
        [0, 1, 0],
        [1, 1, 1],
        [0, 1, 0]])
    array = (array > 0).astype(np.int32)
    y, x = np.nonzero(scipy.signal.convolve2d(array, kernel, mode="same") == 5)
    return np.stack([x, y], 1)

def find_ends_from_array(array):
    kernel = np.array([
        [0, 1, 0],
        [1, 1, 1],
        [0, 1, 0]])
    array = (array > 0).astype(np.int32)
    mask = scipy.signal.convolve2d(array, kernel, mode="same") == 2
    mask &= array > 0
    y, x = np.nonzero(mask)
    return np.stack([x, y], 1)

def find_components(map_array, intersects):
    interect_id_by_points = {}
    for i in range(intersects.shape[0]):
        interect_id_by_points[tuple(intersects[i].tolist())] = i
    for i in range(intersects.shape[0]):
        x, y = intersects[i]
        for d in directions:
            xt = x + d[0]
            yt = y + d[1]
            if xt > 0 and yt > 0 and xt < map_array.shape[1] and yt < map_array.shape[0]:
                if map_array[yt, xt]:
                    hits_intersect = trace(xt, yt, interect_id_by_points)

class Map:
    def __init__(self, map_array):
        self.map_array = map_array
        self.intersects = set(tuple(x) for x in find_intersects_from_array(map_array).tolist())
        self.spots = np.count_nonzero(map_array > 0)

    def available_directions(self, pos):
        x, y = pos
        available = {}
        if y + 1 < self.map_array.shape[0] and self.map_array[y + 1, x]:
            available[(0, 1)] = (x, y + 1)
        if x + 1 < self.map_array.shape[1] and self.map_array[y, x + 1]:
            available[(1, 0)] = (x + 1, y)
        if y - 1 >= 0 and self.map_array[y - 1, x]:
            available[(0, -1)] = (x, y - 1)
        if x - 1 >= 0 and self.map_array[y, x - 1]:
            available[(-1, 0)] = (x - 1, y)
        return available

    def render(self, visited):
        for y in range(self.map_array.shape[0]):
            for x in range(self.map_array.shape[1]):
                if self.map_array[y, x]:
                    print("@" if (x, y) in visited else "#", end="")
                else:
                    print(".", end="")
            print()


circle_positions = {
    (1, 0): 0,
    (0, 1): 1,
    (-1, 0): 2,
    (0, -1): 3,
}
def rotate_to(from_dir, to_dir):
    left_rotations = None
    right_rotations = circle_positions[to_dir] - circle_positions[from_dir]
    if right_rotations < 0:
        left_rotations = -right_rotations
        right_rotations = None
        if left_rotations > 2:
            right_rotations = 4 - left_rotations
            left_rotations = None
    else:
        if right_rotations > 2:
            left_rotations = 4 - right_rotations
            right_rotations = None
    if right_rotations is None:
        for i in range(left_rotations):
            yield "L"
    else:
        for i in range(right_rotations):
            yield "R"
            

def find_paths(map_ds, start, end, pos, direction, visited=set(), path=[]):
    visited = set(visited)
    visited.add(pos)
    if pos == end and len(visited) == map_ds.spots:
        yield path
    available_directions = map_ds.available_directions(pos)

    unvisited_directions = set()
    for new_direction, new_pos in available_directions.items():
        if new_pos not in visited:
            unvisited_directions.add(new_direction)
    for new_direction, new_pos in available_directions.items():
        valid = new_pos not in visited \
                or (new_pos in map_ds.intersects
                    and len(unvisited_directions) == 0)
        if not valid:
            continue
        new_path = list(path)
        new_path.extend(rotate_to(direction, new_direction))
        new_path.append(1)
        new_visited = visited | {new_pos}
        yield from find_paths(map_ds, start, end, new_pos, new_direction, visited=new_visited,
                              path=new_path)

def collapse_path(path):
    new_path = []
    state = 0
    current = 0
    for x in path:
        if state == 0:
            if x in {"R", "L"}:
                new_path.append(x)
            else:
                current = x
                state = 1
        elif state == 1:
            if x in {"R", "L"}:
                while current >= 10:
                    new_path.append(9)
                    current -= 9
                new_path.append(current)
                new_path.append(x)
                state = 0
            else:
                current += x
        else:
            raise NotImplementedError
    if state == 1:
        while current >= 10:
            new_path.append(9)
            current -= 9
        new_path.append(current)
    return new_path

def length_of_longest_non_overlapping_strings(path):
    N = len(path)
    dp_table = np.zeros([N + 1, N + 1], dtype=np.int32)
    for i in range(1, N + 1):
        for j in range(1, N + 1):
            if (path[i - 1] == path[j - 1]
                and dp_table[i - 1][j - 1] < (j - i)):
                dp_table[i][j] = dp_table[i - 1][j - 1] + 1
            else:
                dp_table[i][j] = 0
    I, J = np.nonzero(dp_table)
    values = dp_table[I, J]
    occurrences = defaultdict(set)
    for overlap, i, j in sorted(((value, i, j) for i, j, value in zip(I, J, values)), reverse=True):
        if overlap > 10 or overlap < 3:
            continue
        part = tuple(path[i - overlap:i])
        occurrences[part].add(i - overlap)
        occurrences[part].add(j - overlap)
    score = 0
    for part, indices in sorted(occurrences.items(), key=lambda x: -len(x[1])):
        score += len(part) * len(indices)
    return (score, path, occurrences)

def greedy_longest_repeating_subsequence_algorithm(path):
    path = collapse_path(path)
    return length_of_longest_non_overlapping_strings(path)

map_array = get_array(map_string)
intersects = find_intersects_from_array(map_array)
ends = find_ends_from_array(map_array)
start = tuple(np.argwhere(map_array == 2)[0])
ends = {tuple(end) for end in ends.tolist()} - {start}
assert len(ends) == 1
end = next(iter(ends))
direction = (0, -1)
print(np.count_nonzero(map_array > 0))
map_ds = Map(map_array)

possibilities = []
for path in find_paths(map_ds, start, end, start, direction):
    possibilities.append(greedy_longest_repeating_subsequence_algorithm(path))
for score, path, options in sorted(possibilities, reverse=True)[:10]:
    print(score)
    print(path)
    for part, indices in sorted(options.items(), key=lambda x: -len(x[1])):
        print(part, indices)
    print("==========")

print(start)
print(end)
print(intersects)
