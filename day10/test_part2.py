from part1 import *

def test_part2_simple():
    belt = AsteroidBelt.parse('''
        .#....#####...#..
        ##...##.#####..##
        ##...#...#.#####.
        ..#.....#...###..
        ..#.#.....#....##
        ''')
    point, _ = belt.most_unique()
    assert tuple(point) == (8, 3)
    order = belt.laser_order()
    
    positions = belt.asteroids[order]
    assert tuple(positions[0]) == (8, 1)
    assert tuple(positions[1]) == (9, 0)
    assert tuple(positions[2]) == (9, 1)
    assert tuple(positions[3]) == (10, 0)
    assert tuple(positions[4]) == (9, 2)
    assert tuple(positions[5]) == (11, 1)
    assert tuple(positions[6]) == (12, 1)
    assert tuple(positions[7]) == (11, 2)
    assert tuple(positions[8]) == (15, 1)

    assert tuple(positions[-9]) == (6, 1)
    assert tuple(positions[-8]) == (6, 0)
    assert tuple(positions[-7]) == (7, 0)
    assert tuple(positions[-6]) == (8, 0)
    assert tuple(positions[-5]) == (10, 1)
    assert tuple(positions[-4]) == (14, 0)
    assert tuple(positions[-3]) == (16, 1)
    assert tuple(positions[-2]) == (13, 3)
    assert tuple(positions[-1]) == (14, 3)

def test_part2_large():
    belt = AsteroidBelt.parse('''
        .#..##.###...#######
        ##.############..##.
        .#.######.########.#
        .###.#######.####.#.
        #####.##.#.##.###.##
        ..#####..#.#########
        ####################
        #.####....###.#.#.##
        ##.#################
        #####.##.###..####..
        ..######..##.#######
        ####.##.####...##..#
        .#####..#.######.###
        ##...#.##########...
        #.##########.#######
        .####.#.###.###.#.##
        ....##.##.###..#####
        .#.#.###########.###
        #.#.#.#####.####.###
        ###.##.####.##.#..##
        ''')
    order = belt.laser_order()
    positions = belt.asteroids[order]
    for pos, coords in [
        (1, (11,12)),
        (2, (12,1)),
        (3, (12,2)),
        (10, (12,8)),
        (20, (16,0)),
        (50, (16,9)),
        (100, (10,16)),
        (199, (9,6)),
        (200, (8,2)),
        (201, (10,9)),
        (299, (11,1))]:
        assert tuple(positions[pos - 1]) == coords

