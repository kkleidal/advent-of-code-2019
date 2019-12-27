from intcode import IntCodeProgram

def add(x, y):
    return (x[0] + y[0], x[1] + y[1])

left = {
    (1, 0): (0, 1),
    (0, 1): (-1, 0),
    (-1, 0): (0, -1),
    (-1, 0): (1, 0),
}

right = {
    b: a
    for a, b in left.items()
}

class Tracer:
    def __init__(self, scanner, pos, direction, turns):
        self.scanner = scanner
        self.pos = pos
        self.direction = direction
        self.turns = turns

    @property
    def y(self):
        return self.pos[0]

    @property
    def x(self):
        return self.pos[1]

    def step(self):
        d1 = right if self.turns == 1 else left
        d2 = left if self.turns == 1 else right 

        self.direction = d1[self.direction]
        new_pos = add(self.pos, self.direction)
        if self.scanner.query(*new_pos):
            return new_pos
        self.pos = new_pos

        self.direction = d2[self.direction]
        new_pos = add(self.pos, self.direction)
        if self.scanner.query(*new_pos):
            return new_pos
        self.pos = new_pos

        new_pos = add(self.pos, self.direction)
        if self.scanner.query(*new_pos):
            return new_pos
        self.pos = new_pos

        self.direction = d2[self.direction]
        new_pos = add(self.pos, self.direction)
        assert self.scanner.query(*new_pos)
        return new_pos
        
class TractorScanner:
    def __init__(self):
        with open("input.txt", "r") as f:
            program = IntCodeProgram(list(map(int, f.read().strip().split(","))))
        self._program = program

    def query(self, y, x):
        proc = self._program.process()
        proc.send(x)
        proc.send(y)
        return proc.recv() == 1

    def scan(self, size=10):
        size -= 1
        found = set()

        top_tracer = Tracer(self, (4, 9), (1, 0), turns=-1)
        bottom_tracer = Tracer(self, (5, 8), (0, 1), turns=1)
        bottoms = {}
        tops = {}
        x_start = 10
        x_pos = x_start
        while True:
            print(x_pos)
            while top_tracer.x <= x_pos:
                y, x = top_tracer.step()
                if x not in tops or tops[x] < y:
                    tops[x] = y
            while bottom_tracer.x <= x_pos:
                y, x = bottom_tracer.step()
                if x not in bottoms or bottoms[x] > y:
                    bottoms[x] = y
            if x_pos - x_start >= size:
                right_x = x_pos
                left_x = right_x - size
                for top_y in range(tops[left_x], bottoms[left_x] + 1):
                    bottom_y = top_y + size
                    valid = not (
                        bottom_y > bottoms[right_x]
                        or bottom_y > bottoms[left_x]
                        or top_y < tops[right_x]
                        or top_y < tops[left_x]
                    )
                    if valid:
                        best = None
                        for ry in range(size):
                            for rx in range(size):
                                x = left_x + rx
                                y = top_y + ry
                                dist = x * x + y * y
                                if best is None or dist < best[0]:
                                    best = (dist, (y, x))
                        return best[1][1] * 10000 + best[1][0]
            x_pos += 1

scanner = TractorScanner()
print(scanner.scan(size=100))
