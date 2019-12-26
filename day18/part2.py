import numpy as np
import heapq
import scipy.sparse.csgraph
from collections import defaultdict, deque
import networkx as nx
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class PieceKinds:
    WALL = 0
    EMPTY = 1
    KEY = 2
    DOOR = 3

def build_adjacency(edges):
    adj = defaultdict(set)
    for node1, node2 in edges:
        adj[node1].add(node2)
    return adj

class AdjacencyList:
    def __init__(self):
        self._adj = defaultdict(set)

    def intersect_nodes(self, nodes):
        new_adj = defaultdict(set)
        for node, neighbors in self._adj.items():
            if node not in nodes:
                continue
            for neighbor in neighbors:
                if neighbor not in nodes:
                    continue
                new_adj[node].add(neighbor)
        self._adj = new_adj

    def copy(self):
        copy = AdjacencyList()
        copy._adj.update(self._adj)
        return copy

    def edges(self):
        for node, neighbors in self._adj.items():
            for neighbor in neighbors:
                yield (node, neighbor)

    def __getitem__(self, node):
        return self._adj[node]

    def __len__(self):
        return len(self._adj)

    def items(self):
        return self._adj.items()

    def values(self):
        return self._adj.values()
 
    def keys(self):
        return self._adj.keys()
 
    def __iter__(self):
        return iter(self._adj)

class DijkstraSSSP:
    def __init__(self, nodes, adj, weights, pos):
        index_to_node = sorted(nodes)
        node_to_index = {node: idx for idx, node in enumerate(index_to_node)}
        N = len(node_to_index)

        graph = np.inf * np.ones([N, N])
        for node1, node2 in adj.edges():
            i = node_to_index[node1]
            j = node_to_index[node2]
            w = weights[(node1, node2)]
            graph[i, j] = w

        G = nx.DiGraph()
        for node in nodes:
            i = node_to_index[node]
            G.add_node(i)
        for node1, node2 in adj.edges():
            i = node_to_index[node1]
            j = node_to_index[node2]
            w = weights[(node1, node2)]
            if np.isfinite(w):
                G.add_edge(i, j, weight=w)
        path_lengths = np.infty * np.ones([N])
        sssp, _ = nx.single_source_dijkstra(G, node_to_index[pos])
        for dest, dist in sssp.items():
            path_lengths[dest] = dist
        self.path_lengths = path_lengths
        self.node_to_index = node_to_index

    def shortest_path_distance(self, to_node):
        j = self.node_to_index[to_node]
        return self.path_lengths[j]


def sssp(nodes, adj, weights, pos):
    return DijkstraSSSP(nodes, adj, weights, pos)

class GameStateCommand(ABC):
    @abstractmethod
    def do(self, game_state):
        pass

    @abstractmethod
    def undo(self, game_state):
        pass

    def __str__(self):
        return "<%s>" % (type(self).__name__,)

    def __repr__(self):
        return str(self)

class MoveToKeyCommand(GameStateCommand):
    def __init__(self, robot_index, pos, key_loc, door_loc, label):
        self.robot_index = robot_index
        self.pos = pos
        self.key_loc = key_loc
        self.door_loc = door_loc
        self.label = label

    def __str__(self):
        return "<get key %s>" % (chr(ord('a') + self.label),)

    def __repr__(self):
        return str(self)

    def do(self, game_state):
        game_state.robot_positions[self.robot_index] = self.key_loc
        del game_state.keys[self.key_loc]
        if self.door_loc is not None:
            del game_state.doors[self.door_loc]
            del game_state.reverse_doors[self.label]

    def undo(self, game_state):
        game_state.robot_positions[self.robot_index] = self.pos
        game_state.keys[self.key_loc] = self.label
        if self.door_loc is not None:
            game_state.doors[self.door_loc] = self.label
            game_state.reverse_doors[self.label] = self.door_loc

def collapse_graph(nodes, adj, weights, poi):
    new_adj = adj.copy()
    new_weights = dict(weights)

    nodes_by_index = sorted(nodes)
    index_by_node = {node: i for i, node in enumerate(nodes)}

    G = nx.Graph()
    for i, node in enumerate(nodes_by_index):
        if node not in poi:
            G.add_node(i)
            for neighbor in adj[node]:
                if neighbor not in poi:
                    j = index_by_node[neighbor]
                    G.add_edge(i, j)

    drop_nodes = set()
    for component in nx.connected_components(G):
        adjacent_pois = set()
        adjacent_poi_indices = set()
        for node in poi:
            adjacent_to_component = False
            for neighbor in adj[node]:
                j = index_by_node[neighbor]
                if j in component:
                    adjacent_to_component = True
                    break
            if adjacent_to_component:
                adjacent_pois.add(node)
                adjacent_poi_indices.add(index_by_node[node])
        drop_nodes.update(nodes_by_index[idx] for idx in component)
        if len(adjacent_pois) >= 2:
            G2 = nx.Graph()
            my_nodes = adjacent_poi_indices | component
            for i in my_nodes:
                G2.add_node(i)
                for neighbor in adj[nodes_by_index[i]]:
                    j = index_by_node[neighbor]
                    if j in my_nodes:
                        G2.add_edge(i, j)
            paths = dict(nx.all_pairs_shortest_path(G2))
            for i in adjacent_poi_indices:
                n1 = nodes_by_index[i]
                for j in adjacent_poi_indices:
                    if j == i:
                        continue
                    n2 = nodes_by_index[j]
                    w = len(paths[i][j]) - 1
                    # Add direct edge between POIs
                    new_weights[(n1, n2)] = w
                    new_weights[(n2, n1)] = w
                    new_adj[n1].add(n2)
                    new_adj[n2].add(n1)

    new_nodes = set(nodes) - drop_nodes
    new_adj.intersect_nodes(new_nodes)
    real_new_weights = defaultdict(lambda: np.infty)
    real_new_weights.update({edge: weight for edge, weight in new_weights.items()
                             if edge[0] in new_nodes and edge[1] in new_nodes})
    return new_nodes, new_adj, real_new_weights


class GameState:
    _idx = 0
    def __init__(self, nodes, adj, weights, robot_positions, keys, doors, reverse_doors):
        self._idx = GameState._idx
        GameState._idx += 1

        self.nodes = nodes
        self.adj = adj
        self.weights = weights
        self.keys = keys
        self.robot_positions = robot_positions
        self.keys = keys
        self.doors = doors
        self.reverse_doors = reverse_doors
        self._moves_cache = {}

    def key(self):
        return (tuple(self.robot_positions), tuple(sorted(self.keys)))


    def get_weights(self):
        weights = defaultdict(lambda: np.infty)
        for (n1, n2), w in self.weights.items():
            if not (n1 in self.doors or n2 in self.doors):
                weights[(n1, n2)] = w
        return weights

    def moves(self):
        key = self.key()
        if key in self._moves_cache:
            return self._moves_cache[key]
        moves = []
        paths = [sssp(self.nodes, self.adj, self.get_weights(), pos)
                 for pos in self.robot_positions]
        for key_loc in self.keys:
            for ridx, robot_path in enumerate(paths):
                distance = robot_path.shortest_path_distance(key_loc)
                if np.isfinite(distance):
                    distance = int(distance)
                    command = self.move_to_key(ridx, key_loc)
                    moves.append((distance, command))
        self._moves_cache[key] = moves
        return moves

    def __lt__(self, other):
        if isinstance(other, GameState):
            return self._idx < other._idx
        else:
            return NotImplemented


    def move_to_key(self, robot_index, key_loc):
        keys = self.keys
        doors = self.doors
        reverse_doors = self.reverse_doors
        weights = self.weights

        door_loc = None

        label = keys[key_loc]
        if label in reverse_doors:
            door_loc = reverse_doors[label]

        return MoveToKeyCommand(robot_index, self.robot_positions[robot_index],
                                key_loc, door_loc, label)

    @classmethod
    def parse(cls, game_map):
        lines = game_map.strip().split("\n")
        H = len(lines)
        W = len(lines[0].strip())

        entrances = []
        kinds = np.zeros([H, W], dtype=np.uint8)
        ids = np.zeros([H, W], dtype=np.uint8)
        keys = {}
        doors = {}
        for y, line in enumerate(lines):
            for x, char in enumerate(line.strip()):
                if char == "#":
                    kinds[y, x] = PieceKinds.WALL
                elif char == ".":
                    kinds[y, x] = PieceKinds.EMPTY
                elif char == "@":
                    kinds[y, x] = PieceKinds.EMPTY
                    entrances.append((y, x))
                elif char.islower():
                    kinds[y, x] = PieceKinds.KEY
                    ids[y, x] = ord(char) - ord('a')
                    keys[(y, x)] = ids[y, x]
                elif char.isupper():
                    kinds[y, x] = PieceKinds.DOOR
                    ids[y, x] = ord(char.lower()) - ord('a')
                    doors[(y, x)] = ids[y, x]

        y, x = np.nonzero(kinds)
        nodes = list(zip(y.tolist(), x.tolist()))

        adj = AdjacencyList()
        weights = defaultdict(lambda: np.infty)
        for y, x in nodes:
            node = (y, x)
            for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = (y + dy, x + dx)
                if neighbor in nodes:
                    adj[node].add(neighbor)
                    adj[neighbor].add(node)
                    weights[(node, neighbor)] = 1
                    weights[(neighbor, node)] = 1

        nodes, adj, weights = collapse_graph(nodes, adj, weights,
                                             set(entrances) | set(keys) | set(doors))
        reverse_doors = {label: pos for pos, label in doors.items()}
        return GameState(nodes, adj, weights, entrances,
                         keys, doors,
                         reverse_doors)

class RecursiveFinderStrategy(ABC):
    @abstractmethod
    def recursive_find(self, finder, state, steps):
        pass

class PruneStrategy(RecursiveFinderStrategy):
    def recursive_find(self, finder, state, steps):
        key = state.key()
        if key not in finder.best_to_node or steps < finder.best_to_node[key]:
            finder.best_to_node[key] = steps
        else:
            return np.infty
        if finder.best_found and finder.best_found < steps:
            return np.infty
        best = None if len(state.keys) > 0 else 0
        for cost, next_cmd in sorted(state.moves(), key=lambda x: x[0]):
            next_cmd.do(state)
            downstream_cost = cost + self.recursive_find(finder, state, steps+cost)
            if best is None or downstream_cost < best:
                best = downstream_cost
            next_cmd.undo(state)
        finder.found_path(finder.best_to_node[key] + best)
        return best

class CacheStrategy(RecursiveFinderStrategy):
    def recursive_find(self, finder, state, steps):
        key = state.key()
        if key not in finder.best_to_node or steps < finder.best_to_node[key]:
            finder.best_to_node[key] = steps
        if key not in finder.best_from_node:
            best = None if len(state.keys) > 0 else 0
            for cost, next_cmd in sorted(state.moves(), key=lambda x: x[0]):
                next_cmd.do(state)
                downstream_cost = cost + self.recursive_find(finder, state, steps+cost)
                if best is None or downstream_cost < best:
                    best = downstream_cost
                next_cmd.undo(state)
            assert key not in finder.best_from_node
            finder.best_from_node[key] = best
        finder.found_path(finder.best_from_node[key] + finder.best_to_node[key])
        return finder.best_from_node[key]

class RecursiveFinder:
    def __init__(self, strategy, cb=None):
        self.best_found = None
        self.cb = cb
        self.best_to_node = {}
        self.best_from_node = {}
        self.strategy = strategy

    def found_path(self, dist):
        if self.cb:
            self.cb.found_path(dist)
        if self.best_found is None or dist < self.best_found:
            self.best_found = dist

    def recursively_find_path(self, state, steps=0):
        return self.strategy.recursive_find(self, state, steps)

def find_shortest_path(input_string, strategy=PruneStrategy(), cb=None):
    state = GameState.parse(input_string)

    return RecursiveFinder(strategy, cb=cb).recursively_find_path(state)

class Report:
    def __init__(self):
        self.best = None

    def found_path(self, length):
        if self.best is None or length < self.best:
            self.best = length
            logger.info("Found new best path: %d", self.best)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    with open("input2.txt", "r") as f:
        input_map = f.read().strip()
    print(find_shortest_path(input_map, strategy=PruneStrategy(), cb=Report()))
