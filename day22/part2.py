import argparse
from collections import deque
from abc import ABC, abstractmethod

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--forwards", action="store_true")
parser.add_argument("input")
parser.add_argument("deck_size", type=int)
parser.add_argument("times", type=int)
parser.add_argument("card_of_interest", type=int)

class ASTVisitor(ABC):
    def visit(self, node, up, children):
        kind = type(node).__name__
        attr = "visit_%s" % kind
        if hasattr(self, attr):
            return getattr(self, attr)(node, up, children)
        else:
            return self.generic_visit(node, up, children)

    def generic_visit(self, node, up, children):
        if up:
            return node
        else:
            return True

class PrintVisitor(ASTVisitor):
    def __init__(self, indent=2):
        self.indent = indent
        self.current_indent = 0

    def generic_visit(self, node, up, children):
        if not up:
            print(" " * self.current_indent + str(node))
            self.current_indent += self.indent
        else:
            self.current_indent -= self.indent

def print_ast(root, **kwargs):
    root.visit(PrintVisitor(**kwargs))

class NodeCollectorVisitor(ASTVisitor):
    def __init__(self):
        self.ids_by_node = {}
        self.nodes_by_id = []

    def generic_visit(self, node, up, children):
        if not up and node not in self.ids_by_node:
            self.ids_by_node[node] = len(self.ids_by_node)
            self.nodes_by_id.append(node)

class ASTTransformer(ASTVisitor):
    def visit_AddNode(self, node, up, children):
        if up:
            if len(children) > 0:
                return AddNode(children)
            else:
                return None

    def visit_MultiplyNode(self, node, up, children):
        if up:
            if len(children) > 0:
                return MultiplyNode(children)
            else:
                return None

class DissociateVisitor(ASTTransformer):
    def __init__(self, modN):
        self.modN = modN

    def visit_AddNode(self, node, up, children):
        N = self.modN
        if up:
            addends = []
            for child in children:
                if isinstance(child, AddNode):
                    addends.extend(child.children)
                else:
                    addends.append(child)

            # Combine constants:
            constants = 0
            new_addends = []
            for child in addends:
                if isinstance(child, Constant):
                    constants = (constants + child.value) % N
                else:
                    new_addends.append(child)
            if constants != 0:
                new_addends.insert(0, Constant(constants))

            if len(new_addends) == 0:
                return Constant(0)
            elif len(new_addends) == 1:
                return new_addends[0]
            else:
                return AddNode(new_addends)

    def visit_MultiplyNode(self, node, up, children):
        N = self.modN
        if up:
            factors = []
            for child in children:
                if isinstance(child, MultiplyNode):
                    factors.extend(child.children)
                else:
                    factors.append(child)

            # Combine constants:
            constants = 1
            new_factors = []
            for child in factors:
                if isinstance(child, Constant):
                    constants = multiply_mod_N(constants, child.value, N)
                else:
                    new_factors.append(child)
            if constants != 1:
                new_factors.insert(0, Constant(constants))

            if len(new_factors) == 0:
                return Constant(1)
            elif len(new_factors) == 1:
                return new_factors[0]
            else:
                return MultiplyNode(new_factors)

def multiply_mod_N(a, b, mod):
    # 1)  ll res = 0; // Initialize result
    # 2)  a = a % mod.
    # 3)  While (b > 0)
    #         a) If b is odd, then add 'a' to result.
    #                res = (res + a) % mod
    #         b) Multiply 'a' with 2
    #            a = (a * 2) % mod
    #         c) Divide 'b' by 2
    #            b = b/2  
    # 4)  Return res 
    res = 0
    a = a % mod
    if b < 0:
        a = -a
        b = -b
    while b > 0:
        if b & 1:
            res = (res + a) % mod
        a = (a * 2) % mod
        b = b // 2
    return res

def distribute_multiplies(root, modN, factor=1):
    if isinstance(root, MultiplyNode):
        if len(root.children) == 2 and sum(1 for child in root.children if isinstance(child, Constant)):
            a, b = root.children
            if isinstance(a, Constant):
                const = a
                other = b
            else:
                const = b
                other = a
            factor = multiply_mod_N(factor, const.value, modN)
            return distribute_multiplies(other, modN, factor=factor)
        else:
            children = []
            applied = False
            for child in root.children:
                if isinstance(child, Constant) and not applied:
                    new_value = multiply_mod_N(factor, child.value, modN)
                    children.append(Constant(new_value))
                    applied = True
                else:
                    children.append(distribute_multiplies(child, modN, factor=1))
            if not applied:
                children.insert(0, Constant(factor))
                applied = True
            return MultiplyNode(children)
    elif isinstance(root, AddNode):
        children = []
        for child in root.children:
            children.append(distribute_multiplies(child, modN, factor=factor))
        return AddNode(children)
    elif isinstance(root, Placeholder):
        if factor == 1:
            return root
        else:
            return MultiplyNode([Constant(factor), root])
    elif isinstance(root, Constant):
        new_value = multiply_mod_N(factor, root.value, modN)
        return Constant(new_value)
    else:
        raise NotImplementedError

def combine_like_terms(root, modN):
    if isinstance(root, MultiplyNode):
        children = []
        for child in root.children:
            children.append(combine_like_terms(child, modN))
        return MultiplyNode(children)
    elif isinstance(root, AddNode):
        children = []
        for child in root.children:
            children.append(combine_like_terms(child, modN))
        
        x_coeff = 0
        new_children = []
        for child in children:
            if isinstance(child, MultiplyNode) and len(child.children) == 2 \
               and sum(1 for c in child.children if isinstance(c, Placeholder)) == 1 \
               and sum(1 for c in child.children if isinstance(c, Constant)) == 1:
                c, _ = extract_constant(child)
                x_coeff = (x_coeff + c) % modN
            else:
                new_children.append(child)
        if x_coeff != 0:
            new_children.append(MultiplyNode([Constant(x_coeff), Placeholder("x")]))

        if len(new_children) == 0:
            return None
        elif len(new_children) == 1:
            return new_children[0]
        else:
            return AddNode(new_children)
    elif isinstance(root, Placeholder):
        return root
    elif isinstance(root, Constant):
        return root
    else:
        raise NotImplementedError

def dissociate_ast(root, modN):
    return root.visit(DissociateVisitor(modN))

def simplify_ast(ast, deck_size):
    ast = dissociate_ast(ast, deck_size)
    ast = distribute_multiplies(ast, deck_size)
    ast = dissociate_ast(ast, deck_size)
    ast = combine_like_terms(ast, deck_size)
    return ast

class ASTNode(ABC):
    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def children(self):
        raise NotImplementedError

    def __str__(self):
        return "<%s name=%r>" % (type(self).__name__, self.name)

    def __repr__(self):
        return str(self)

    def visit(self, visitor):
        out = []
        q = deque([(False, self, out, None)])
        while q:
            up, node, children, my_children = q.pop()
            output = visitor.visit(node, up, my_children)
            if up:
                if output is not None:
                    children.append(output)
            else:
                if output != False:
                    my_new_children = []
                    q.append((True, node, children, my_new_children))
                    for child in node.children:
                        q.append((False, child, my_new_children, None))
                else:
                    children.append(node)
        if len(out) == 0:
            return None
        return out[0]

    def _adapt(self, other):
        if isinstance(other, int):
            other = Constant(other)
        if not isinstance(other, ASTNode):
            return NotImplemented
        return other

    def __add__(self, other):
        other = self._adapt(other)
        return AddNode([self, other])

    def __radd__(self, other):
        other = self._adapt(other)
        return AddNode([other, self])

    def __sub__(self, other):
        other = self._adapt(other)
        return AddNode([self, -1 * other])

    def __rsub__(self, other):
        other = self._adapt(other)
        return AddNode([other, -1 * self])

    def __mul__(self, other):
        other = self._adapt(other)
        return MultiplyNode([self, other])

    def __rmul__(self, other):
        other = self._adapt(other)
        return MultiplyNode([other, self])

    def __neg__(self):
        return -1 * self

class Placeholder(ASTNode):
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def children(self):
        return []

class OpNode(ASTNode):
    def __init__(self, inputs, name):
        self._inputs = inputs
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def children(self):
        return self._inputs

class AddNode(OpNode):
    def __init__(self, nodes):
        super().__init__(nodes, "add")

class MultiplyNode(OpNode):
    def __init__(self, nodes):
        super().__init__(nodes, "multiply")

class Constant(ASTNode):
    def __init__(self, value):
        self.value = value

    @property
    def name(self):
        return repr(self.value)

    @property
    def children(self):
        return []


class ShuffleOp(ABC):
    @abstractmethod
    def run(self, card_of_interest, deck_size):
        pass

    @abstractmethod
    def build_ast(self, input_node):
        pass

    @abstractmethod
    def inverse(self, deck_size):
        pass

    def __repr__(self):
        return "<%s>" % (self,)

class Cut(ShuffleOp):
    def __init__(self, cut):
        self.cut = cut

    def run(self, card_of_interest, deck_size):
        cut = self.cut
        if cut < 0:
            cut += deck_size
        if card_of_interest < cut:
            return deck_size - (cut - card_of_interest)
        else:
            return card_of_interest - cut

    def build_ast(self, input_node):
        return input_node - self.cut

    def inverse(self, deck_size):
        return Cut(-self.cut)
    
    def __str__(self):
        return "cut %d" % self.cut

class DealIntoNewStack(ShuffleOp):
    def run(self, card_of_interest, deck_size):
        return deck_size - card_of_interest - 1

    def inverse(self, deck_size):
        return DealIntoNewStack()

    def build_ast(self, input_node):
        return -input_node - 1
    
    def __str__(self):
        return "deal into new stack"

def inverse_mod_n(x, N):
    q = [0, 0]
    r = [N, x]
    t = [0, 1]
    while r[1] != 0:
        tmp = r[0] // r[1]
        q[0] = q[1]
        q[1] = tmp

        tmp = r[0] - q[1] * r[1]
        r[0] = r[1]
        r[1] = tmp

        tmp = t[0] - q[1] * t[1]
        t[0] = t[1]
        t[1] = tmp

    if r[0] != 1:
        raise ValueError("%d and %d are not co-prime. No multiplicative inverse exists." % (x, N))
    out = t[0]
    while out < 0:
        out += N
    return out % N

class DealWithIncrement(ShuffleOp):
    def __init__(self, increment):
        self.increment = increment

    def run(self, card_of_interest, deck_size):
        return ((card_of_interest % deck_size) * (self.increment % deck_size)) % deck_size

    def build_ast(self, input_node):
        return input_node * self.increment

    def inverse(self, deck_size):
        return DealWithIncrement(inverse_mod_n(self.increment, deck_size))
    
    def __str__(self):
        return "deal with increment %d" % self.increment

def extract_constant(node):
    assert len(node.children) == 2
    assert any(isinstance(child, Constant) for child in node.children)
    constant = None
    other = None
    for child in node.children:
        if isinstance(child, Constant) and constant is None:
            constant = child
        else:
            other = child
    return constant.value, other

def msb(x):
    if x == 0:
        return 0;
    msb = 0;
    while x > 0:
        x = x >> 1
        msb += 1
    return msb

class PlaceholderReplacement(ASTTransformer):
    def __init__(self, replace_with):
        self.replace_with = replace_with

    def visit_Placeholder(self, node, up, children):
        if up:
            return self.replace_with

def compose_asts(outer, inner):
    # replace placeholder in outer with inner
    return outer.visit(PlaceholderReplacement(inner))

def extract_modular_constants(instructions, deck_size, times):
    input_x = Placeholder(name="x")
    x = input_x
    for inst in instructions:
        x = inst.build_ast(x)
    root = simplify_ast(x, deck_size)

    print_ast(root)

    # Duplicate transform multiple times
    result_transform_terms = []
    current_transform = root
    max_bit_pos = msb(times)
    for bit_pos in range(0, max_bit_pos + 1):
        if (1 << bit_pos) & times:
            result_transform_terms.append(current_transform)
        current_transform = simplify_ast(compose_asts(current_transform, current_transform), deck_size)
    if len(result_transform_terms) == 0:
        result_transform_terms.append(input_x)
    result_transform = None
    for transform in result_transform_terms:
        if result_transform is None:
            result_transform = transform
        else:
            result_transform = simplify_ast(compose_asts(result_transform, transform), deck_size)
    root = result_transform

    print_ast(root)

    assert isinstance(root, AddNode)
    const_b, other = extract_constant(root)
    assert isinstance(other, MultiplyNode)
    const_a, other = extract_constant(other)
    assert isinstance(other, Placeholder)
    return const_a, const_b
        

if __name__ == "__main__":
    args = parser.parse_args()
    with open(args.input, "r") as f:
        instructions = []
        for line in f:
            line = line.strip().split(" ")
            if line[0] == "cut":
                instructions.append(Cut(int(line[-1])))
            elif line[1] == "with":
                instructions.append(DealWithIncrement(int(line[-1])))
            else:
                instructions.append(DealIntoNewStack())

    N = args.deck_size
    if not args.forwards:
        instructions = [instr.inverse(N) for instr in reversed(instructions)]
    for instr in instructions:
        print(instr)
    a, b = extract_modular_constants(instructions, N, args.times)

    out = (multiply_mod_N(a, args.card_of_interest, N) + b) % N
    print("%dx + %d (mod %d) = %d" % (a, b, N, out))

    # card = args.card_of_interest
    # previous_states = {}
    # history = []
    # for t in range(args.times):
    #     if t % 100000 == 0:
    #         print("Time: %d / %d" % (t, args.times))
    #     if t == 260702:
    #         print(t, card)
    #     if t == 431501:
    #         print(t, card)
    #     history.append(card)
    #     if card in previous_states:
    #         print("Found overlap at time %d" % t)
    #         offset = previous_states[card]
    #         period = (t - offset)
    #         equivalent = (args.times - offset) % period + offset
    #         card = history[equivalent]
    #         break
    #     else:
    #         previous_states[card] = t
    #     for inst in backwards_instructions:
    #         card = inst.run(card, N)
    # print("Card at that position by end: %d" % card)
