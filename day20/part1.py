from collections import defaultdict
import itertools
import networkx as nx
import matplotlib.pyplot as plt
import heapq

def get_horizontal(lines, y, xs, top):
    for x in xs:
        if lines[y][x].isalpha() and lines[y+1][x].isalpha():
            marker = "".join([lines[y][x], lines[y+1][x]])
            if top:
                loc = (y + 2, x)
            else:
                loc = (y - 1, x)
            yield loc, marker

def get_vertical(lines, x, ys, left):
    for y in ys:
        if lines[y][x].isalpha() and lines[y][x+1].isalpha():
            marker = "".join([lines[y][x], lines[y][x+1]])
            if left:
                loc = (y, x + 2)
            else:
                loc = (y, x - 1)
            yield loc, marker

class PriorityQueue:
    def __init__(self, lst=[]):
        self._lst = list(lst)
        heapq.heapify(self._lst)

    def pop(self):
        return heapq.heappop(self._lst)

    def push(self, x):
        return heapq.heappush(self._lst, x)

    def __len__(self):
        return len(self._lst)

    def __iter__(self):
        while self:
            yield self.pop()

class Maze:
    @classmethod
    def parse(cls, input_string):
        input_string = input_string.strip("\n")
        lines = input_string.split("\n")
        H = len(lines)
        W = len(lines[0])
        assert all(len(line) == W for line in lines)

        torus_width = 0
        x = W // 2
        for y in range(H):
            if lines[y][x] in ("#", "."):
                torus_width += 1
        torus_width //= 2

        outer_top_bottom = (list(get_horizontal(lines, 0, range(W), True))
                            + list(get_horizontal(lines, H - 2, range(W), False)))
        outer_left_right = (list(get_vertical(lines, 0, range(H), True))
                            + list(get_vertical(lines, W - 2, range(H), False)))
        inner_top_bottom_span = range(2+torus_width, W-2-torus_width)
        inner_top_bottom = (list(get_horizontal(lines, 2+torus_width, inner_top_bottom_span, False))
                            + list(get_horizontal(lines, H - 4 - torus_width, inner_top_bottom_span, True)))
        inner_left_right_span = range(2+torus_width, H-2-torus_width)
        inner_left_right = (list(get_vertical(lines, 2+torus_width, inner_left_right_span, False))
                            + list(get_vertical(lines, W - 4 - torus_width, inner_left_right_span, True)))

        markers = defaultdict(set)
        points_to_markers = defaultdict(set)
        for point, marker in itertools.chain(outer_top_bottom, outer_left_right, inner_top_bottom,
                                             inner_left_right):
            markers[marker].add(point)
            points_to_markers[point].add(marker)

        nodes = set()
        for y in range(2, H - 2):
            for x in range(2, W - 2):
                if lines[y][x] == ".":
                    nodes.add((y, x))

        nodes_by_index = sorted(nodes)
        index_by_node = {node: i for i, node in enumerate(nodes_by_index)}

        G = nx.Graph()
        labels = {}
        pos = {}
        for marker, points in markers.items():
            for point in points:
                if point not in index_by_node:
                    import pdb
                    pdb.set_trace()
                i = index_by_node[point]
                labels[i] = marker
                G.add_node(i)
        for i, node in enumerate(nodes_by_index):
            G.add_node(i)
            pos[i] = (node[1], -node[0])
            for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = (node[0] + dy, node[1] + dx)
                if neighbor in nodes:
                    j = index_by_node[neighbor]
                    G.add_edge(i, j)
        for marker, points in markers.items():
            if len(points) >= 2:
                for point1 in points:
                    for point2 in points:
                        if point1 != point2:
                            i = index_by_node[point1]
                            j = index_by_node[point2]
                            G.add_edge(i, j)

        inward_portal_leaps = set()
        outward_portal_leaps = set()
        for marker, points in markers.items():
            if len(points) == 2:
                points = sorted(points)
                i, j = [index_by_node[node] for node in points]
                first_in_torus = (points[0][0] > 2 and points[0][0] < H - 3
                        and points[0][1] > 2 and points[0][1] < W - 3)
                if first_in_torus:
                    outward_portal_leaps.add((j, i))
                    inward_portal_leaps.add((i, j))
                else:
                    outward_portal_leaps.add((i, j))
                    inward_portal_leaps.add((j, i))

        return Maze(G, labels, pos, nodes_by_index, index_by_node, markers, points_to_markers,
                    inward_portal_leaps, outward_portal_leaps)
        
    def __init__(self, G, labels, pos, nodes_by_index, index_by_node, markers, points_to_markers,
                 inward_portal_leaps, outward_portal_leaps):
        self.G = G
        self.labels = labels
        self.pos = pos
        self.nodes_by_index = nodes_by_index
        self.index_by_node = index_by_node
        self.markers = markers
        self.points_to_markers = points_to_markers
        self.inward_portal_leaps = inward_portal_leaps
        self.outward_portal_leaps = outward_portal_leaps

    def plot_graph(self, font_size=16):
        nx.draw(self.G, self.pos)
        nx.draw_networkx_labels(self.G, self.pos, self.labels, font_size=font_size)

    def save_graph_image(self, to_file, font_size=16):
        plt.clf()
        self.plot_graph(font_size=font_size)
        plt.axis('off')
        plt.savefig(to_file)
        plt.gcf().set_size_inches((10, 10))
        plt.clf()
        
    def shortest_path(self, from_marker="AA", to_marker="ZZ"):
        start = self.markers[from_marker]
        assert len(start) == 1
        start = next(iter(start))

        end = self.markers[to_marker]
        assert len(end) == 1
        end = next(iter(end))

        i = self.index_by_node[start]
        j = self.index_by_node[end]
        return nx.shortest_path_length(self.G, source=i, target=j)

    def recursive_shortest_path(self, from_marker="AA", to_marker="ZZ"):
        start = self.markers[from_marker]
        assert len(start) == 1
        start = next(iter(start))

        end = self.markers[to_marker]
        assert len(end) == 1
        end = next(iter(end))

        i = self.index_by_node[start]
        j = self.index_by_node[end]

        heuristics = dict(nx.single_target_shortest_path_length(self.G, target=j))
        pq = PriorityQueue([(
            heuristics[i], # priority
            0,             # steps
            (
                0,             # level
                i,             # node
            ),
        )])
        popped = set()
        best_so_far_for_state = {}
        while pq:
            _, steps, state = pq.pop()
            popped.add(state)
            if state in best_so_far_for_state:
                del best_so_far_for_state[state]
            level, node_idx = state
            if node_idx == j and level == 0:
                return steps
            for neighbor in self.G.neighbors(node_idx):
                edge = (node_idx, neighbor)
                level_change = 0
                if edge in self.inward_portal_leaps:
                    level_change = 1
                elif edge in self.outward_portal_leaps:
                    level_change = -1
                new_state = (level + level_change, neighbor)
                if new_state[0] < 0:
                    # Cannot go beyond outer most level
                    #TODO: confirm
                    continue
                new_steps = steps + 1
                new_heuristic = new_steps + heuristics[neighbor]
                if new_state in popped:
                    continue
                if new_state in best_so_far_for_state and best_so_far_for_state[new_state] < new_heuristic:
                    continue
                pq.push((new_heuristic, new_steps, new_state))
                best_so_far_for_state[new_state] = new_heuristic
        return None

if __name__ == "__main__":
    with open("input.txt", "r") as f:
        maze = Maze.parse(f.read())
    maze.save_graph_image("my-graph.png")
    print(maze.shortest_path())
