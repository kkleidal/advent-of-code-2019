from part1 import find_shortest_path
import pytest

import logging
logging.basicConfig(level=logging.DEBUG)

def test_example1():
    assert find_shortest_path('''
        #########
        #b.A.@.a#
        #########''') == 8

def test_example2():
    assert find_shortest_path('''
        ########################
        #...............b.C.D.f#
        #.######################
        #.....@.a.B.c.d.A.e.F.g#
        ########################''') == 132

@pytest.mark.skip
def test_example3():
    assert find_shortest_path('''
        #################
        #i.G..c...e..H.p#
        ########.########
        #j.A..b...f..D.o#
        ########@########
        #k.E..a...g..B.n#
        ########.########
        #l.F..d...h..C.m#
        #################''') == 136

def test_example4():
    assert find_shortest_path('''
        ########################
        #@..............ac.GI.b#
        ###d#e#f################
        ###A#B#C################
        ###g#h#i################
        ########################
        ''') == 81
