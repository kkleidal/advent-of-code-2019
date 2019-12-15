import logging

from .base import ProcessState, Op, Mode

logger = logging.getLogger(__name__)

class ProcessStateRunning(ProcessState):
    def step(self, process):
        pc = process.instruction_pointer
        instruction = process.instruction
        op = Op.registry[instruction.op_code]
        arguments = []
        arguments_desc = []
        for i, arg_spec in enumerate(op.args):
            value = process.memory[process.instruction_pointer + i + 1]
            mode = Mode.registry[instruction.argument_mode(i)]
            original_value = value
            value = mode.resolve_argument(process, arg_spec, value)
            arguments_desc.append(((mode, original_value), value))
            arguments.append(value)
        logger.debug("EXEC %d %s %s", pc, op, " ".join("%r(%r)" % (arg_spec, arg) for arg_spec, arg in arguments_desc))
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
        for hook in process.hooks:
            hook.on_received_input(process, self.dest, input)

class ProcessStateSendingOutput(ProcessState):
    def __init__(self, value):
        self.value = value

    def get_output(self, process):
        process.state = ProcessStateRunning()
        for hook in process.hooks:
            hook.on_sent_output(process, self.value)
        return self.value
