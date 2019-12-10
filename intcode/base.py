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
