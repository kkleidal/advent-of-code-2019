import pdb
import math
from abc import ABC, abstractmethod
from collections import defaultdict

class Reaction:
    def __init__(self, requires, produces):
        self.requires = requires
        self.produces = produces

    @classmethod
    def parse(cls, line):
        line = line.strip()
        if not line:
            return None
        lhs, rhs = line.split("=>")
        requires = {}
        produces = {}
        for reagent in lhs.strip().split(","):
            amount, element = reagent.strip().split(" ")
            amount = int(amount)
            requires[element] = amount
        for reagent in rhs.strip().split(","):
            amount, element = reagent.strip().split(" ")
            amount = int(amount)
            produces[element] = amount
        return cls(requires, produces)

    def __str__(self):
        return "<Reaction requires=%r produces=%r>" % (self.requires, self.produces)

    def __repr__(self):
        return str(self)


def get_reactions(input):
    for line in input.split("\n"):
        reaction = Reaction.parse(line)
        if reaction:
            yield reaction


class Strategy(ABC):
    @abstractmethod
    def request(self, plant, requires, has={}, level=0, visualize=False):
        pass


class BruteForceStrategy(Strategy):
    def __init__(self):
        self._cache = {}

    def request(self, plant, requires, has={}, level=0, visualize=False):
        key = (tuple(sorted(requires.items())), tuple(sorted(has.items())))
        if key in self._cache:
            return self._cache[key]
        if len(requires) == 0:
            return 0, []
        best = None
        argbest = None
        for reaction in plant.reactions:
            if set(reaction.produces.keys()) & set(requires):
                still_requires = dict(requires)
                still_has = dict(has)
                # Process prerequisites
                my_ores = 0
                for element, amount in reaction.requires.items():
                    required = amount
                    remaining = 0
                    if element in still_has:
                        remaining = still_has[element]
                        new_required = max(0, required - remaining)
                        remaining = max(0, remaining - required)
                        required = new_required
                        if remaining == 0:
                            del still_has[element]
                        else:
                            still_has[element] = remaining
                    if required > 0:
                        if element == "ORE":
                            my_ores += required
                        else:
                            still_requires[element] = still_requires.get(element, 0) + required
                # Process produced
                for element, amount in reaction.produces.items():
                    required = still_requires.get(element, 0)
                    remaining = amount
                    if required > 0:
                        new_required = max(0, required - amount)
                        remaining = max(0, remaining - required)
                        required = new_required
                    if required == 0:
                        del still_requires[element]
                    else:
                        still_requires[element] = required
                if visualize:
                    print(" " * (2 * level) + str(reaction))
                ores, reactions = self.request(plant, still_requires, still_has, level=(level+1), visualize=visualize)
                ores += my_ores
                if best is None or ores < best:
                    best = ores
                    argbest = reactions + [reaction]
        if best is None:
            pdb.set_trace()
            raise RuntimeError("No rule")
        self._cache[key] = (best, argbest)
        return best, argbest


class TopoSortStrategy(Strategy):
    dot = 0
    def __init__(self):
        self._cache = {}
        self._element_to_reaction = None
        self._graph = None

    def plot_dot(self, nodes, adjacency):
        d = TopoSortStrategy.dot
        with open("%d.dot" % d, "w") as f:
            print("digraph mygraph {", file=f)
            for node in nodes:
                print("  n%s;" % node, file=f)
            for node in adjacency:
                for child in adjacency[node]:
                    print("  n%s -> n%s;" % (node, child), file=f)
            print("}", file=f)
        TopoSortStrategy.dot += 1

    def make_graph(self, plant):
        nodes = set()
        adjacency = defaultdict(set)
        for reaction in plant.reactions:
            from_node = list(reaction.produces.keys())[0]
            to_nodes = set(reaction.requires.keys())
            adjacency[from_node].update(to_nodes)
            nodes.update(to_nodes)
            nodes.add(from_node)

        reverse_adjacency = defaultdict(set)
        for product in adjacency:
            for dependency in adjacency[product]:
                reverse_adjacency[dependency].add(product)

        q = [("FUEL", False)]
        enqueued = {"FUEL"}
        topo_order = []
        while q:
            node, last = q.pop(-1)
            if last:
                topo_order.append(node)
            else:
                q.append((node, True))
                for child in adjacency[node]:
                    if child not in enqueued:
                        enqueued.add(child)
                        q.append((child, False))

        ancestors_graph = defaultdict(set)
        for node in topo_order[::-1]:
            ancestors = set()
            for parent in reverse_adjacency[node]:
                ancestors.update(ancestors_graph[parent])
                ancestors.add(parent)
            ancestors_graph[node] = ancestors

        descendants_graph = defaultdict(set)
        for node in topo_order[::-1]:
            descendants = set()
            for child in adjacency[node]:
                descendants.update(descendants_graph[child])
                descendants.add(child)
            descendants_graph[node] = descendants

        return nodes, adjacency, reverse_adjacency, descendants_graph, ancestors_graph

    def request(self, plant, requires, has={}, level=0, visualize=False, hit=set()):
        assert len(has) == 0
        if len(requires) == 0:
            return 0, []

        if self._element_to_reaction is None:
            e2r = {}
            for reaction in plant.reactions:
                assert len(reaction.produces) == 1
                for element, amount in reaction.produces.items():
                    assert element not in e2r
                    e2r[element] = reaction
            self._element_to_reaction = e2r
        e2r = self._element_to_reaction

        if self._graph is None:
            self._graph = self.make_graph(plant)
            nodes, products_graph, _, _, _ = self._graph
        nodes, _, _, _, products_transitive_graph = self._graph

        best_element = None
        for element in requires.keys():
            if not (products_transitive_graph[element] - hit):
                best_element = element
                break
        if best_element is None:
            pdb.set_trace()
        assert best_element is not None

        new_hit = set(hit)
        new_hit.add(element)

        element = best_element
        amount = requires[element]

        assert element in e2r
        reaction = e2r[element]
        n_times = int(math.ceil(amount / reaction.produces[element]))
        assert n_times >= 1

        now_requires = dict(requires)
        del now_requires[element]

        my_ores = 0
        for required_element, required_amount in reaction.requires.items():
            required_amount *= n_times
            if required_element == "ORE":
                my_ores += required_amount
            else:
                now_requires[required_element] = now_requires.get(required_element, 0) + required_amount

        if visualize:
            print(" " * (2 * level) + str(reaction))
        ores, reactions = self.request(plant, now_requires, {},
                                       hit=new_hit,
                                       level=(level+1), visualize=visualize)
        ores += my_ores
        reactions = reactions + [reaction]

        return ores, reactions


class Plant:
    def __init__(self, reactions):
        self.reactions = list(reactions)
        self.strategy = TopoSortStrategy()

    def request(self, requires, has={}, level=0, visualize=False):
        return self.strategy.request(self, requires, has, level, visualize)

    def fuel_given_ore(self, total_ore):
        ores = 0

        # Doubling to get a range
        factor = 0
        while ores < total_ore:
            current = (1 << factor)
            ores = self.request({"FUEL": current})[0]
            factor += 1
        high = 1 << (factor - 1)
        low = 1 << (factor - 2)

        # Binary search to get a specific value
        while high > low + 1:
            mid = (high + low) // 2
            ores = self.request({"FUEL": mid})[0]
            if ores > total_ore:
                high = mid
            else:
                low = mid

        return low

    @classmethod
    def parse(cls, input):
        return cls(get_reactions(input))
