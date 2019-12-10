import logging

from .base import ProcessState, Op, Mode

logger = logging.getLogger(__name__)

class ProcessStateRunning(ProcessState):
    def step(self, process):
        instruction = process.instruction
        op = Op.registry[instruction.op_code]
        arguments = []
        for i, arg_spec in enumerate(op.args):
            value = process.memory[process.instruction_pointer + i + 1]
            mode = Mode.registry[instruction.argument_mode(i)]
            value = mode.resolve_argument(process, arg_spec, value)
            arguments.append(value)
        logger.debug("EXEC %s %s", op, " ".join(repr(arg) for arg in arguments))
        op.execute(process, *arguments)

class ProgramExitted(StopIteration):
    pass

class ProcessStateExitted(ProcessState):
    def step(self, process):
        raise ProgramExitted

class ProcessStateWaitingForInput(ProcessState):
    def __init__(self, dest):
        self.dest = dest

    def set_input(self, process, input):
        process.memory[self.dest] = input
        process.state = ProcessStateRunning()

class ProcessStateSendingOutput(ProcessState):
    def __init__(self, value):
        self.value = value

    def get_output(self, process):
        process.state = ProcessStateRunning()
        return self.value
