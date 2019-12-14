from part1 import Simulation
import numpy as np
from collections import defaultdict
import itertools

class TupleCycle:
    def __init__(self, two_ago, one_ago):
        self.two_ago = two_ago
        self.one_ago = one_ago

    def update(self, x):
        self.two_ago = self.one_ago
        self.one_ago = x

    def __getitem__(self, idx):
        if idx == -1:
            return self.one_ago
        elif idx == -2:
            return self.two_ago
        else:
            raise KeyError(idx)

class GCDResult:
    def __init__(self, a, b, gcd, a_bezout, b_bezout):
        self.a = a
        self.b = b
        self.gcd = gcd
        self.a_bezout = a_bezout
        self.b_bezout = b_bezout
        self.lcm = self.a * self.b // self.gcd

def extended_euclids(a, b):
    x = max(a, b)
    y = min(a, b)
    R = TupleCycle(x, y)
    S = TupleCycle(1, 0)
    T = TupleCycle(0, 1)
    while R[-1] != 0:
        q = R[-2] // R[-1]
        R.update(R[-2] - q * R[-1])
        S.update(S[-2] - q * S[-1])
        T.update(T[-2] - q * T[-1])
    factor = -1 if T[-2] < 0 else 1
    return GCDResult(
        a = a,
        b = b,
        gcd=R[-2], 
        a_bezout=factor * (-S[-2] if a == x else T[-2]),
        b_bezout=factor * (-S[-2] if b == x else T[-2]))

def find_overlap(a, b, c, d):
    '''
    finds k1 and k2 such that
    k1 * a + b = k2 * c + d
    where a, c  > 0
    and b, d >= 0

    Returns (k1 * a + b, lcm(a, c)) aka offset, period
    '''
    assert a > 0
    assert c > 0
    assert b >= 0
    assert d >= 0
    offset = min(b, d)
    b -= offset
    d -= offset

    result = extended_euclids(a, c)
    assert max(b, d) % result.gcd == 0

    num = (d - b)
    if num == 0:
        k = 0
    else:
        denom = (result.a_bezout * a - result.b_bezout * c)
        assert (num != 0)
        assert (denom != 0)
        assert (num > 0) == (denom > 0)
        assert (num % denom == 0)
        k = num // denom

    k1 = k * result.a_bezout
    k2 = k * result.b_bezout
    assert k1 >= 0
    assert k2 >= 0
    assert k1 * a + b == k2 * c + d

    lowest_value = max(offset + b, offset + d)
    best_found = offset + k1 * a + b
    period = result.lcm
    best_found -= ((best_found - lowest_value) // period) * period
    return (best_found, period)
    
def reduce_overlaps(series):
    '''
    Expects [(offset, period), ...]
    Returns (offset, period) for all series
    '''
    result = series[0]
    for next_series in series[1:]:
        b, a = result
        d, c = next_series
        new_b, new_a = find_overlap(a, b, c, d)
        result = (new_b, new_a)
    return result

def test_find_overlap():
    assert find_overlap(15, 3, 9, 0) == (18, 45)
    assert find_overlap(9, 0, 15, 3) == (18, 45)
    assert find_overlap(9, 42, 15, 45) == (60, 45)
    assert find_overlap(6, 0, 9, 0) == (0, 18)
    assert find_overlap(45, 18, 7, 0) == (63, 315)
    assert find_overlap(6, 0, 12, 12) == (12, 12)

    series = [(3, 15), (0, 9), (0, 7)]
    assert reduce_overlaps(series) == (63, 315)
    encountered_series = []
    for start, period in series:
        encountered = {start}
        pos = start
        while pos < 63:
            pos += period
            encountered.add(pos)
        assert pos == 63
        encountered_series.append(encountered)
    encountered_in_all = encountered_series[0]
    for encountered in encountered_series[1:]:
        encountered_in_all &= encountered
    assert encountered_in_all == {63}
   
def _find_first_repeat(pos, vel, ignore=False):
    if pos.shape[1] == 1 or ignore:
        simulation = Simulation(pos, vel)
        state_hashes = {simulation.state_hash(): [simulation.t]}
        while True:
            simulation.step()
            state_hash = simulation.state_hash()
            if state_hash in state_hashes:
                possible_ts = state_hashes[state_hash]
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
        offset, period = reduce_overlaps(first_repeats)
        return offset + period

def find_first_repeat(desc):
    sim = Simulation.parse(desc)
    return _find_first_repeat(sim.pos, sim.vel)

def test_1():
    with open("test1.in", "r") as f:
        test1_desc = f.read()
    assert find_first_repeat(test1_desc) == 2772

def test_2():
    with open("test2.in", "r") as f:
        test2_desc = f.read()
    assert find_first_repeat(test2_desc) == 4686774924

def test_3():
    desc = '''
        <x=-1, y=7, z=3>
        <x=12, y=2, z=-13>
        <x=14, y=18, z=-8>
        <x=17, y=4, z=-4>'''
    out = find_first_repeat(desc)
    assert out == 402951477454512

if __name__ == "__main__":
    desc = '''
        <x=-1, y=7, z=3>
        <x=12, y=2, z=-13>
        <x=14, y=18, z=-8>
        <x=17, y=4, z=-4>'''
    out = find_first_repeat(desc)
    print(out)
