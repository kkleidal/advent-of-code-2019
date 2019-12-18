from part1 import find_intersects, calibration

def test_example():
    intersects = find_intersects('''
        ..#..........
        ..#..........
        #######...###
        #.#...#...#.#
        #############
        ..#...#...#..
        ..#####...^..''')
    assert set(tuple(pair) for pair in intersects.tolist()) == {
        (2, 2),
        (2, 4),
        (6, 4),
        (10, 4),
    }
    assert calibration(intersects) == 76
