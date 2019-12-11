import numpy as np

def cached(fn):
    cache = {}
    def wrapped(self, *args):
        key = (self, tuple(args))
        if key not in cache:
            cache[key] = fn(self)
        return cache[key]
    return wrapped

class AsteroidBelt:
    def __init__(self, asteroids):
        self.asteroids = asteroids

    @cached
    def most_unique(self):
        unique = self.detect_unique()
        idx = self.station()
        return self.asteroids[idx], unique[idx]

    @cached
    def station(self):
        unique = self.detect_unique()
        idx = np.argmax(unique)
        return idx

    def laser_order(self):
        station = self.station()
        N = self.asteroids.shape[0]

        offset = self.get_offset()[station]
        N = offset.shape[0]

        angle = np.arctan2(offset[:, 0], offset[:, 1])
        distance = np.sqrt(np.sum(np.square(offset), axis=-1))
        vaporized = np.zeros([N], dtype=np.bool)
        vaporized[station] = True

        rounded_angle = angle.round(decimals=10)
        angle_bins = np.unique(rounded_angle)[::-1]
        angle_bins = np.concatenate([angle_bins[angle_bins <= 0], angle_bins[angle_bins > 0]], axis=0)

        order = []
        angle_bin_index = 0
        while not np.all(vaporized):
            current_angle = angle_bins[angle_bin_index]
            possible = ~vaporized & (rounded_angle == current_angle)
            if np.any(possible):
                possible_asteroids = np.argwhere(possible)
                selected_asteroid = possible_asteroids[np.argmin(distance[possible])]
                order.append(selected_asteroid[0])
                vaporized[selected_asteroid] = True
            angle_bin_index = (angle_bin_index + 1) % angle_bins.shape[0]
        order = np.array(order)
        return order

    @cached
    def get_offset(self):
        left = np.reshape(self.asteroids, [-1, 1, 2])
        right = np.reshape(self.asteroids, [1, -1, 2])
        offset = left - right
        return offset

    @cached
    def get_slope(self):
        offset = self.get_offset()
        denom = np.sqrt(np.square(offset).sum(axis=-1, keepdims=True))
        slope = offset / denom
        return slope

    def detect_unique(self):
        slope = self.get_slope()
        number_unique = []
        for i in range(slope.shape[0]):
            loc = self.asteroids[i]
            unique = np.unique(slope[i].round(decimals=10), axis=0).shape[0] - 1
            number_unique.append(unique)
        return np.array(number_unique)

    @classmethod
    def parse(cls, string):
        asteroids = []
        for y, line in enumerate(string.strip().split("\n")):
            line = line.strip()
            if line:
                for x, character in enumerate(line):
                    if character == "#":
                        asteroids.append((x, y))
        return cls(np.array(asteroids))

if __name__ == "__main__":
    input_value = '''
    .#..#..##.#...###.#............#.
    .....#..........##..#..#####.#..#
    #....#...#..#.......#...........#
    .#....#....#....#.#...#.#.#.#....
    ..#..#.....#.......###.#.#.##....
    ...#.##.###..#....#........#..#.#
    ..#.##..#.#.#...##..........#...#
    ..#..#.......................#..#
    ...#..#.#...##.#...#.#..#.#......
    ......#......#.....#.............
    .###..#.#..#...#..#.#.......##..#
    .#...#.................###......#
    #.#.......#..####.#..##.###.....#
    .#.#..#.#...##.#.#..#..##.#.#.#..
    ##...#....#...#....##....#.#....#
    ......#..#......#.#.....##..#.#..
    ##.###.....#.#.###.#..#..#..###..
    #...........#.#..#..#..#....#....
    ..........#.#.#..#.###...#.....#.
    ...#.###........##..#..##........
    .###.....#.#.###...##.........#..
    #.#...##.....#.#.........#..#.###
    ..##..##........#........#......#
    ..####......#...#..........#.#...
    ......##...##.#........#...##.##.
    .#..###...#.......#........#....#
    ...##...#..#...#..#..#.#.#...#...
    ....#......#.#............##.....
    #......####...#.....#...#......#.
    ...#............#...#..#.#.#..#.#
    .#...#....###.####....#.#........
    #.#...##...#.##...#....#.#..##.#.
    .#....#.###..#..##.#.##...#.#..##
    '''
    belt = AsteroidBelt.parse(input_value)
    _, count = belt.most_unique()
    print(count)

