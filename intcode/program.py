from .process_states import ProcessStateRunning, ProcessStateWaitingForInput, ProcessStateSendingOutput, \
        ProgramExitted

def default_get_input():
    while True:
        print("Input:  ", end="", flush=True)
        yield int(input())

class EarlyEndOfInputError(ValueError):
    pass

class Memory:
    def __init__(self, program):
        self._memory = {}
        for i, value in enumerate(program):
            self._memory[i] = value

    def _check_index(self, idx):
        if not isinstance(idx, int) or idx < 0:
            raise KeyError("memory addresses must be non-negative integers, was: %r" % idx)

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            return [self[index] for index in idx.indices(max(self._memory))]
        self._check_index(idx)
        return self._memory.get(idx, 0)

    def __setitem__(self, idx, value):
        if isinstance(idx, slice):
            raise NotImplementedError
        self._check_index(idx)
        self._memory[idx] = value

class Process:
    def __init__(self, program):
        self.program = program
        self.memory = Memory(self.program.program)
        self.instruction_pointer = 0
        self.state = ProcessStateRunning()
        self.relative_base = 0

    @property
    def instruction(self):
        return Instruction(self.memory[self.instruction_pointer])

    def set_input(self, input):
        return self.state.set_input(self, input)

    def get_output(self):
        return self.state.get_output(self)

    def step(self):
        return self.state.step(self)

    def waiting_for_input(self):
        return isinstance(self.state, ProcessStateWaitingForInput)

    def waiting_for_output(self):
        return isinstance(self.state, ProcessStateSendingOutput)

    def send(self, input):
        self.step_until_interrupt()
        self.set_input(input)

    def recv(self):
        self.step_until_interrupt()
        return self.get_output()

    def step_until_interrupt(self):
        while True:
            if self.waiting_for_input():
                return
            elif self.waiting_for_output():
                return
            else:
                self.step()

    def run(self, inputs=None):
        try:
            if inputs is None:
                inputs = default_get_input()
            inputs = iter(inputs)
            while True:
                if self.waiting_for_input():
                    try:
                        input_value = next(inputs)
                    except StopIteration:
                        raise EarlyEndOfInputError
                    self.set_input(input_value)
                elif self.waiting_for_output():
                    yield self.get_output()
                else:
                    self.step()
        except ProgramExitted:
            pass

class Instruction:
    def __init__(self, code):
        self.code = code
        
    @property
    def op_code(self):
        return self.code % 100
    
    def argument_mode(self, i):
        return (self.code // (100 * 10**i)) % 10

class IntCodeProgram:
    def __init__(self, program):
        self.program = program

    def process(self):
        return Process(self)
