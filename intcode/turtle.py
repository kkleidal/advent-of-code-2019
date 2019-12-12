import logging
import numpy as np

from .program import ProgramExitted

logger = logging.getLogger(__name__)

class Vector:
    def __init__(self, dx, dy):
        self.dx = dx
        self.dy = dy

    def rotate_right(self):
        return Vector(self.dy, -self.dx)

    def rotate_left(self):
        return Vector(-self.dy, self.dx)

    def __hash__(self):
        return hash((self.dx, self.dy))

    def __eq__(self, other):
        if isinstance(other, Vector):
            return self.dx == other.dx and self.dy == other.dy
        else:
            return NotImplemented

    def _add(self, other):
        if isinstance(other, Point):
            return Point(other.x + self.dx, other.y + self.dy)
        else:
            return NotImplemented

    def __add__(self, other):
        return self._add(other)

    def __radd__(self, other):
        return self._add(other)

    def __str__(self):
        return "<Vector dx=%d dy=%d>" % (self.dx, self.dy)

    def __repr__(self):
        return str(self)

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y
        else:
            return NotImplemented

    def __str__(self):
        return "<Point x=%d y=%d>" % (self.x, self.y)

    def __repr__(self):
        return str(self)


class TurtleRobot:
    def __init__(self, program, start_panel=0):
        self.process = program.process()
        self.position = Point(0, 0)
        self.direction = Vector(0, 1)
        self.canvas = {self.position: start_panel}

    def step(self):
        logger.debug("START STEP at position %s, direction %s", self.position, self.direction)
        color = self.canvas.get(self.position, 0)
        logger.debug("Observe color %d", color)
        self.process.send(color)
        color = self.process.recv()
        logger.debug("Set color %d", color)
        assert color in (0, 1)
        self.canvas[self.position] = color
        turn = self.process.recv()
        assert turn in (0, 1)
        if turn == 0:
            logger.debug("Turn left")
            self.direction = self.direction.rotate_left()
        else:
            logger.debug("Turn right")
            self.direction = self.direction.rotate_right()
        self.position += self.direction
        logger.debug("END STEP")

    def array(self):
        min_x = min(p.x for p in self.canvas)
        min_y = min(p.y for p in self.canvas)
        max_x = max(p.x for p in self.canvas)
        max_y = max(p.y for p in self.canvas)
        
        out = []
        for y in range(max_y, min_y - 1, -1):
            row = []
            for x in range(min_x, max_x + 1):
                color = self.canvas.get(Point(x, y), 0)
                row.append(color)
            out.append(np.array(row))
        return np.stack(out, axis=0)

    def render(self):
        array = self.array()

        out = []
        for y in range(array.shape[0]):
            for x in range(array.shape[1]):
                out.append("██" if array[y, x] else "  ")
            out.append("\n")
        return "".join(out)

    def irun(self):
        try:
            while True:
                self.step()
                yield
        except ProgramExitted:
            pass

    def run(self):
        for _ in self.irun():
            pass
