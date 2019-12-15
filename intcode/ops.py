import logging

from .base import Op, ArgSpec
from .process_states import ProcessStateWaitingForInput, ProcessStateSendingOutput, ProcessStateExitted

logger = logging.getLogger(__name__)

class BinaryOp(Op):
    @property
    def args(self):
        return [
            ArgSpec(resolve=True),
            ArgSpec(resolve=True),
            ArgSpec(resolve=False),
        ]

@Op.register(1)
class AddOp(BinaryOp):
    def execute(self, process, x, y, dest):
        logger.debug("%d + %d = %d -> @%d" % (x, y, x + y, dest))
        process.memory[dest] = x + y
        self.incr_pc(process)

@Op.register(2)
class MultiplyOp(BinaryOp):
    def execute(self, process, x, y, dest):
        logger.debug("%d x %d = %d -> @%d" % (x, y, x * y, dest))
        process.memory[dest] = x * y
        self.incr_pc(process)

@Op.register(7)
class LessThanOp(BinaryOp):
    def execute(self, process, x, y, dest):
        logger.debug("%d < %d = %s -> @%d" % (x, y, x < y, dest))
        process.memory[dest] = 1 if x < y else 0
        self.incr_pc(process)

@Op.register(8)
class EqualsOp(BinaryOp):
    def execute(self, process, x, y, dest):
        logger.debug("%d == %d = %s -> @%d" % (x, y, x == y, dest))
        process.memory[dest] = 1 if x == y else 0
        self.incr_pc(process)

@Op.register(3)
class InputOp(Op):
    @property
    def args(self):
        return [
            ArgSpec(resolve=False),
        ]

    def execute(self, process, dest):
        process.state = ProcessStateWaitingForInput(dest)
        for hook in process.hooks:
            hook.on_waiting_for_input(process, dest)
        self.incr_pc(process)

@Op.register(4)
class OutputOp(Op):
    @property
    def args(self):
        return [
            ArgSpec(resolve=True),
        ]

    def execute(self, process, value):
        process.state = ProcessStateSendingOutput(value)
        for hook in process.hooks:
            hook.on_waiting_for_output(process, value)
        self.incr_pc(process)

@Op.register(5)
class JmpIfTrueOp(Op):
    @property
    def args(self):
        return [
            ArgSpec(resolve=True),
            ArgSpec(resolve=True),
        ]

    def execute(self, process, cnd, loc):
        if cnd > 0:
            logger.debug("Jump to @%d" % (loc,))
            process.instruction_pointer = loc
        else:
            logger.debug("Don't jump")
            self.incr_pc(process)

@Op.register(6)
class JmpIfFalseOp(Op):
    @property
    def args(self):
        return [
            ArgSpec(resolve=True),
            ArgSpec(resolve=True),
        ]

    def execute(self, process, cnd, loc):
        if not (cnd > 0):
            logger.debug("Jump to @%d" % (loc,))
            process.instruction_pointer = loc
        else:
            logger.debug("Don't jump")
            self.incr_pc(process)

@Op.register(99)
class ExitOp(Op):
    @property
    def args(self):
        return []

    def execute(self, process):
        process.state = ProcessStateExitted()

@Op.register(9)
class AdjustRelativeBaseOp(Op):
    @property
    def args(self):
        return [
            ArgSpec(resolve=True),
        ]

    def execute(self, process, value):
        process.relative_base += value
        self.incr_pc(process)
