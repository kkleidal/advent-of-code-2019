import collections
import itertools

class Graph:
    def __init__(self, edges):
        self.nodes = set()
        self.orbits = {}
        self.orbited_by = {}
        for a, b in edges:
            self.nodes.add(a)
            self.nodes.add(b)
            if b not in self.orbits:
                self.orbits[b] = set()
            self.orbits[b].add(a)
            if a not in self.orbited_by:
                self.orbited_by[a] = set()
            self.orbited_by[a].add(b)
        self._toposorted = None

    @classmethod
    def parse(cls, data):
        edges = []
        for line in data.strip().split("\n"):
            line = line.strip()
            if line:
                a, b = line.split(")")
                edges.append((a, b))
        return Graph(edges)

    def toposort(self):
        if self._toposorted is None:
            order = []
            visited = set()
            adj = self.orbits
            for node in sorted(self.nodes):
                if node in visited:
                    continue
                queue = collections.deque([(node, True)])
                while len(queue) > 0:
                    node, fresh = queue.pop()
                    if fresh:
                        if node in visited:
                            continue
                        visited.add(node)
                        queue.append((node, False))
                        for child in sorted(adj.get(node, set())):
                            queue.append((child, True))
                    else:
                        order.append(node)
            self._toposorted = order[::-1]
        return self._toposorted

    def graph_search(self, from_node, to_node):
        queue = collections.deque([(0, from_node)])
        on_queue = {from_node}
        while len(queue) > 0:
            dist, node = queue.pop()
            if node == to_node:
                return dist
            for child in itertools.chain(self.orbits.get(node, []), self.orbited_by.get(node, [])):
                if child not in on_queue:
                    queue.append((dist + 1, child))
                    on_queue.add(child)

    def orbital_transfers(self):
        return self.graph_search(from_node="YOU", to_node="SAN") - 2

    def count_orbits(self):
        total_count = 0
        counts = {}
        for node in self.toposort()[::-1]:
            my_count = 0
            for child in self.orbits.get(node, []):
                my_count += 1 + counts.get(child, 0)
            counts[node] = my_count
            total_count += my_count
        return total_count

print(Graph.parse('''COM)B
        B)C
        C)D
        D)E
        E)F
        B)G
        G)H
        D)I
        E)J
        J)K
        K)L''').count_orbits())
with open("inputs.txt", "r") as f:
    my_input = Graph.parse(f.read())
print(my_input.count_orbits())
print(Graph.parse('''COM)B
    B)C
    C)D
    D)E
    E)F
    B)G
    G)H
    D)I
    E)J
    J)K
    K)L
    K)YOU
    I)SAN''').orbital_transfers())
print(my_input.orbital_transfers())
