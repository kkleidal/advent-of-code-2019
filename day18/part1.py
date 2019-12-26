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

def display(arr):
    for y in range(arr.shape[0]):
        for cell in arr[y]:
            print(cell, end="")
        print()

def add_door_constraint(nodes, adj, weights, doors):
    new_weights = {}
    for edge in adj.edges():
        node1, node2 = edge
        if node1 in doors or node2 in doors:
            new_weights[edge] = np.inf
        else:
            new_weights[edge] = weights[edge]
    return new_weights

def build_adjacency(edges):
    adj = defaultdict(set)
    for node1, node2 in edges:
        adj[node1].add(node2)
    return adj

class AdjacencyList:
    def __init__(self):
        self._adj = defaultdict(set)

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
        for node1, node2 in adj.edges():
            i = node_to_index[node1]
            j = node_to_index[node2]
            w = weights[(node1, node2)]
            if np.isfinite(w):
                G.add_edge(i, j, weight=w)
        path_lengths = np.infty * np.ones([N])
        for dest, path in nx.single_source_shortest_path(G, node_to_index[pos]).items():
            path_lengths[dest] = len(path) - 1
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

class NoopCommand(GameStateCommand):
    def do(self, game_state):
        pass

    def undo(self, game_state):
        pass

class MoveToKeyCommand(GameStateCommand):
    def __init__(self, pos, key_loc, door_loc, label, changed_weights):
        self.pos = pos
        self.key_loc = key_loc
        self.door_loc = door_loc
        self.label = label
        self.changed_weights = changed_weights

    def __str__(self):
        return "<get key %s>" % (chr(ord('a') + self.label),)

    def __repr__(self):
        return str(self)

    def do(self, game_state):
        game_state.pos = self.key_loc
        del game_state.keys[self.key_loc]
        if self.door_loc is not None:
            del game_state.doors[self.door_loc]
            del game_state.reverse_doors[self.label]
        for edge, (_, to_value) in self.changed_weights.items():
            if np.isfinite(to_value):
                game_state.weights[edge] = to_value
            elif edge in game_state.weights:
                del game_state.weights[edge]

    def undo(self, game_state):
        game_state.pos = self.pos
        game_state.keys[self.key_loc] = self.label
        if self.door_loc is not None:
            game_state.doors[self.door_loc] = self.label
            game_state.reverse_doors[self.label] = self.door_loc
        for edge, (from_value, _) in self.changed_weights.items():
            if np.isfinite(from_value):
                game_state.weights[edge] = from_value
            elif edge in game_state.weights:
                del game_state.weights[edge]

class GameState:
    _idx = 0
    def __init__(self, nodes, adj, weights, pos, keys, doors, reverse_doors):
        self._idx = GameState._idx
        GameState._idx += 1

        self.nodes = nodes
        self.adj = adj
        self.weights = weights
        self.keys = keys
        self.pos = pos
        self.keys = keys
        self.doors = doors
        self._key = (self.keys, self.doors, self.pos)
        self.reverse_doors = reverse_doors
        self._moves_cache = {}

    def key(self):
        return (self.pos, tuple(sorted(self.keys)))

    def moves(self):
        key = self.key()
        if key in self._moves_cache:
            return self._moves_cache[key]
        moves = []
        paths = sssp(self.nodes, self.adj, self.weights, self.pos)
        for key_loc in self.keys:
            distance = paths.shortest_path_distance(key_loc)
            if np.isfinite(distance):
                distance = int(distance)
                command = self.move_to_key(key_loc)
                moves.append((distance, command))
        self._moves_cache[key] = moves
        return moves

    def __lt__(self, other):
        if isinstance(other, GameState):
            return self._idx < other._idx
        else:
            return NotImplemented


    def move_to_key(self, key_loc):
        keys = self.keys
        doors = self.doors
        reverse_doors = self.reverse_doors
        weights = self.weights

        door_loc = None
        changed_weights = {}

        label = keys[key_loc]
        if label in reverse_doors:
            door_loc = reverse_doors[label]

            for edge in self.adj.edges():
                node1, node2 = edge
                if node1 == door_loc or node2 == door_loc:
                    changed_weights[edge] = (weights[edge], 1)

        return MoveToKeyCommand(self.pos, key_loc, door_loc, label, changed_weights)

    @classmethod
    def parse(cls, game_map):
        lines = game_map.strip().split("\n")
        H = len(lines)
        W = len(lines[0].strip())

        entrance = None
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
                    entrance = (y, x)
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
                    if not (node in doors or neighbor in doors):
                        weights[(node, neighbor)] = 1
                        weights[(neighbor, node)] = 1

        reverse_doors = {label: pos for pos, label in doors.items()}
        return GameState(nodes, adj, weights, entrance,
                         keys, doors,
                         reverse_doors)

class PriorityQueue:
    def __init__(self, collection=[]):
        self._collection = list(collection)
        if len(self._collection) > 0:
            heapq.heapify(self._collection)

    def push(self, cost, value):
        heapq.heappush(self._collection, (cost, value))

    def pop(self):
        cost, value = heapq.heappop(self._collection)
        return cost, value

    def __len__(self):
        return len(self._collection)

    def __bool__(self):
        return bool(self._collection)

    def __iter__(self):
        while self:
            yield self.pop()

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
        for cost, next_cmd in sorted(state.moves()):
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
            for cost, next_cmd in sorted(state.moves()):
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
        self.best_found = None # 5291
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

    # stack = deque([(True, 0, NoopCommand())])
    # best_found = None
    # while stack:
    #     logger.debug("Stack size: %d. Best found: %s", len(stack), best_found)
    #     down, steps, cmd = stack.pop()
    #     if down:
    #         cmd.do(state)
    #         stack.append((False, None, cmd))
    #         if len(state.keys) == 0:
    #             if best_found is None or best_found > steps:
    #                 best_found = steps
    #         else:
    #             for cost, next_cmd in state.moves():
    #                 stack.append((True, steps + cost, next_cmd))
    #     else:
    #         cmd.undo(state)
    # return best_found

class Report:
    def __init__(self):
        self.best = None

    def found_path(self, length):
        if self.best is None or length < self.best:
            self.best = length
            logger.info("Found new best path: %d", self.best)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    with open("input.txt", "r") as f:
        input_map = f.read().strip()
    print(find_shortest_path(input_map, strategy=CacheStrategy(), cb=Report()))
