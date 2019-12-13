from part1 import Simulation
import numpy as np

def find_first_repeat(desc):
    simulation = Simulation.parse(desc)
    state_hashes = {simulation.state_hash(): [simulation.t]}
    while True:
        simulation.step()
        state_hash = simulation.state_hash()
        if state_hash in state_hashes:
            possible_ts = state_hashes[state_hash]
            print("COLLISION t=%d and t=%s" % (simulation.t, possible_ts))
            for possible_t in possible_ts:
                side_sim = Simulation.parse(desc)
                for _ in range(possible_t):
                    side_sim.step()
                if np.all(side_sim.pos == simulation.pos) and np.all(side_sim.vel == simulation.vel):
                    return simulation.t
        else:
            state_hashes[state_hash] = []
        state_hashes[state_hash].append(simulation.t)

def test_1():
    with open("test1.in", "r") as f:
        test1_desc = f.read()
    assert find_first_repeat(test1_desc) == 2772

def test_2():
    with open("test2.in", "r") as f:
        test2_desc = f.read()
    print(find_first_repeat(test2_desc))

if __name__ == "__main__":
    desc = '''
        <x=-1, y=7, z=3>
        <x=12, y=2, z=-13>
        <x=14, y=18, z=-8>
        <x=17, y=4, z=-4>'''
    print(find_first_repeat(desc))

#with open("test1.in", "r") as f:
#    test1_desc = f.read()
#simulation = Simulation.parse(test1_desc)
#for _ in range(3000):
#    print(simulation.energy())
#    simulation.step()
