from part2 import find_shortest_path
import pytest

import logging
logging.basicConfig(level=logging.DEBUG)

def test_example1():
    assert find_shortest_path('''
        #######
        #a.#Cd#
        ##@#@##
        #######
        ##@#@##
        #cB#Ab#
        #######''') == 8

def test_example2():
    assert find_shortest_path('''
        ###############
        #d.ABC.#.....a#
        ######@#@######
        ###############
        ######@#@######
        #b.....#.....c#
        ###############''') == 24

def test_example3():
    assert find_shortest_path('''
        #############
        #DcBa.#.GhKl#
        #.###@#@#I###
        #e#d#####j#k#
        ###C#@#@###J#
        #fEbA.#.FgHi#
        #############''') == 32

def test_example4():
    assert find_shortest_path('''
        #############
        #g#f.D#..h#l#
        #F###e#E###.#
        #dCba@#@BcIJ#
        #############
        #nK.L@#@G...#
        #M###N#H###.#
        #o#m..#i#jk.#
        #############
        ''') == 72
