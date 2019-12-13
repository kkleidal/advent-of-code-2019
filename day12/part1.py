import re
import numpy as np
import itertools

class GravityStrategy:
    def compute(self, pos):
        raise NotImplementedError

class DefaultGravityStrategy:
    def compute(self, pos):
        N, D = pos.shape
        return np.sum(-np.sign(
            np.reshape(pos, [N, 1, D]) - np.reshape(pos, [1, N, D])), axis=1)

class ExperimentalGravityStrategy:
    def compute(self, pos):
        N, D = pos.shape
        gravity = np.zeros([N, D], dtype=np.int32)
        for dim in range(D):
            arr = pos[:,dim]
            order = np.argsort(arr)
            values = arr[order]

            lesser = 0
            equal = 0
            current = None
            for i in range(N):
                idx = order[i]
                if current is None:
                    current = values[i]
                    equal += 1
                elif current == values[i]:
                    equal += 1
                elif current != values[i]:
                    lesser += equal
                    equal = 1
                    current = values[i]
                gravity[idx, dim] -= lesser

            greater = 0
            equal = 0
            current = None
            for i in range(N-1, -1, -1):
                idx = order[i]
                if current is None:
                    current = values[i]
                    equal += 1
                elif current == values[i]:
                    equal += 1
                elif current != values[i]:
                    greater += equal
                    equal = 1
                    current = values[i]
                gravity[idx, dim] += greater
        return gravity

class Simulation:
    _base_vec = r"<x=\s*(-?\d+),\s*y=\s*(-?\d+),\s*z=\s*(-?\d+)>"
    _pattern = re.compile("^" + _base_vec + "$")
    _timestep = re.compile(r"^After (\d+) steps?:$")
    _state = re.compile("^pos=" + _base_vec + ", vel=" + _base_vec + "$")

    def __init__(self, pos, vel):
        self.pos = pos
        self.vel = vel
        self.t = 0

    def step(self):
        N, D = self.pos.shape
        
        #gravity1 = ExperimentalGravityStrategy().compute(self.pos)
        gravity2 = DefaultGravityStrategy().compute(self.pos)
        #assert np.all(gravity1 == gravity2)

        gravity = gravity2
        self.vel += gravity
        self.pos += self.vel
        self.t += 1

    def state(self):
        N, D = self.pos.shape
        assert D == 3
        out = ["After %d step%s:" % (self.t, "s" if self.t != 1 else "")]
        for i in range(N):
            out.append('pos=<x=%d, y=%d, z=%d>, vel=<x=%d, y=%d, z=%d>' % (tuple(self.pos[i].tolist()) +
                                                                           tuple(self.vel[i].tolist())))
        return '\n'.join(out)

    def energy(self):
        return np.sum(np.sum(np.abs(self.pos), axis=-1) * np.sum(np.abs(self.vel), axis=-1))

    def state_hash(self):
        return hash(tuple(itertools.chain(self.pos.reshape([-1]).tolist(), self.vel.reshape([-1]).tolist())))

    @classmethod
    def parse(cls, desc):
        pos = []
        for line in desc.strip().split("\n"):
            m = cls._pattern.match(line.strip())
            pos.append(np.array(list(map(int, m.groups()))))
        pos = np.stack(pos, 0)
        vel = np.zeros(pos.shape, dtype=pos.dtype)
        return cls(pos, vel)

    @classmethod
    def parse_results(cls, desc):
        state = 0
        t = None
        values = []
        for line in desc.strip().split("\n"):
            line = line.strip()
            if state == 0:
                m = cls._timestep.match(line)
                if m:
                    t = int(m.group(1))
                    values = []
                    state = 1
                else:
                    raise ValueError(line)
            elif state == 1:
                if len(line) == 0:
                    values = np.array(values)
                    yield t, values[:, :3], values[:, 3:]
                    state = 0
                else:
                    m = cls._state.match(line)
                    if m:
                        values.append(list(map(int, m.groups())))
                    else:
                        raise ValueError(line)
        if state == 1:
            values = np.array(values)
            yield t, values[:, :3], values[:, 3:]


def make_test_case(input_file, output_file, energy_file):
    with open(input_file, "r") as f:
        input_desc = f.read()
    with open(output_file, "r") as f:
        output_desc = f.read()
    with open(energy_file, "r") as f:
        energy = int(f.read().strip())
    def test_function():
        simulation = Simulation.parse(input_desc)
        for t, pos, vel in Simulation.parse_results(output_desc):
            while simulation.t < t:
                simulation.step()
            assert np.all(simulation.pos == pos)
            assert np.all(simulation.vel == vel)
        assert energy == simulation.energy()
    return test_function

test_1 = make_test_case("test1.in", "test1.out", "test1.energy")
test_2 = make_test_case("test2.in", "test2.out", "test2.energy")

if __name__ == "__main__":
    simulation = Simulation.parse('''
        <x=-1, y=7, z=3>
        <x=12, y=2, z=-13>
        <x=14, y=18, z=-8>
        <x=17, y=4, z=-4>''')
    for _ in range(1000):
        simulation.step()
    print(simulation.energy())

