from abc import ABC, abstractmethod

class StateError(RuntimeError):
    pass

class ProcessState(ABC):
    def set_input(self, process, input):
        raise StateError("Cannot set input at this state: %s" % self.__class__.__name__)

    def get_output(self, process):
        raise StateError("Cannot get output at this state: %s" % self.__class__.__name__)

    def step(self, process):
        raise StateError("Cannot step at this state: %s" % self.__class__.__name__)

class Op(ABC):
    registry = {}
    @staticmethod
    def register(op_code):
        def register(cls):
            assert issubclass(cls, Op)
            assert op_code not in Op.registry
            Op.registry[op_code] = cls()
            return cls
        return register

    def render(self, instruction, args):
        name = self.__class__.__name__
        out = []
        for arg_values in args:
            line = []
            for i, arg in enumerate(self.args):
                mode = Mode.registry[instruction.argument_mode(i)]
                line.append(mode.render(arg_values[i]))
            out.append("[%s]" % " ".join(line))
        args_repr = " ".join(out)
        return "%s %s" % (name, args_repr)

    @property
    @abstractmethod
    def args(self):
        pass

    def incr_pc(self, process):
        process.instruction_pointer += len(self.args) + 1

    @abstractmethod
    def execute(self, process, *args):
        pass

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return "<%s>" % self

class ProcessHook:
    def on_waiting_for_input(self, process, dest):
        pass

    def on_received_input(self, process, dest, input):
        pass

    def on_waiting_for_output(self, process, value):
        pass

    def on_sent_output(self, process, value):
        pass

    def before_step(self, process):
        pass

    def after_step(self, process):
        pass

    def on_halt(self, process):
        pass

    def on_memory_write(self, address, value):
        pass

    def on_memory_read(self, address, value):
        pass


class ArgSpec:
    def __init__(self, resolve=True):
        self.resolve = resolve

class Mode(ABC):
    registry = {}
    @staticmethod
    def register(mode):
        def register(cls):
            assert issubclass(cls, Mode)
            assert mode not in Mode.registry
            Mode.registry[mode] = cls()
            return cls
        return register

    @abstractmethod
    def resolve_argument(self, process, arg_spec, value):
        pass

    @abstractmethod
    def render(self, value):
        pass

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return str(self)
