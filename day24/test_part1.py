from part1 import BugWorld

def test_example1():
    initial_world = BugWorld.parse('''
        ....#
        #..#.
        #..##
        ..#..
        #....
        ''')
    t_first, t_second, world = initial_world.find_repeat()
    assert world.biodiversity == 2129920
