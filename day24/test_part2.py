from part2 import BugWorld

def test_example1():
    initial_world = BugWorld.parse('''
        ....#
        #..#.
        #.?##
        ..#..
        #....
        ''')
    initial_world.display()
    
    test_world = initial_world.copy()
    for i in range(10):
        test_world.step()
    test_world.display()
