from part1 import Simulation
import numpy as np
from collections import defaultdict

def find_overlap(series):
    if len(series) == 2:
        counters = np.array([start for start, period in series])
        if np.all(counters == 0):
            print("HERE")
            return (0, np.lcm(*[period for start, period in series]))
        overlaps = 0
        first = None
        while True:
            if np.unique(counters).shape[0] == 1:
                if first is None:
                    print("first")
                    first = counters[0]
                else:
                    return first, counters[0] - first
            i = np.argmin(counters)
            counters[i] += max(1, (counters[i ^ 1] - counters[i]) // series[i][1]) * series[i][1]
    else:
        series = sorted(series)
        current = series[0]
        for other in series[1:]:
            current = find_overlap([current, other])
        return current

def first_intersect(series):
    overlap = find_overlap(series)
    if overlap[0] not in {start for start, period in series}:
        return overlap[0]
    return overlap[1]

def _find_first_repeat(pos, vel, ignore=False):
    if pos.shape[1] == 1 or ignore:
        simulation = Simulation(pos, vel)
        state_hashes = {simulation.state_hash(): [simulation.t]}
        while True:
            simulation.step()
            state_hash = simulation.state_hash()
            if state_hash in state_hashes:
                possible_ts = state_hashes[state_hash]
                print("COLLISION t=%d and t=%s" % (simulation.t, possible_ts))
                for possible_t in possible_ts:
                    side_sim = Simulation(pos, vel)
                    for _ in range(possible_t):
                        side_sim.step()
                    if np.all(side_sim.pos == simulation.pos) and np.all(side_sim.vel == simulation.vel):
                        return possible_t, simulation.t - possible_t
            else:
                state_hashes[state_hash] = []
            state_hashes[state_hash].append(simulation.t)
    else:
        first_repeats = []
        for d in range(pos.shape[1]):
            first_repeats.append(_find_first_repeat(pos[:,d:d+1], vel[:,d:d+1]))
        return first_intersect(first_repeats)
        #counters = np.array([start + period for start, period in first_repeats])
        #while True:
        #    i = np.argmin(counters)
        #    counters[i] += first_repeats[i][1]
        #    if np.unique(counters).shape[0] == 1:
        #        return counters[i]

def find_first_repeat(desc):
    sim = Simulation.parse(desc)
    return _find_first_repeat(sim.pos, sim.vel)

def test_find_overlap():
    assert first_intersect([[0, 3], [1, 7]]) == 15
    assert first_intersect([[0, 3], [0, 6]]) == 6

def test_1():
    with open("test1.in", "r") as f:
        test1_desc = f.read()
    assert find_first_repeat(test1_desc) == 2772

def test_2():
    with open("test2.in", "r") as f:
        test2_desc = f.read()
    assert find_first_repeat(test2_desc) == 4686774924

if __name__ == "__main__":
    desc = '''
        <x=-1, y=7, z=3>
        <x=12, y=2, z=-13>
        <x=14, y=18, z=-8>
        <x=17, y=4, z=-4>'''
    out = find_first_repeat(desc)
    assert out != 756679196970672

#with open("test1.in", "r") as f:
#    test1_desc = f.read()
#simulation = Simulation.parse(test1_desc)
#for _ in range(3000):
#    print(simulation.energy())
#    simulation.step()
