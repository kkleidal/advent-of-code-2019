from .base import Mode

@Mode.register(0)
class ReferenceMode(Mode):
    def resolve_argument(self, process, arg_spec, value):
        if arg_spec.resolve:
            return process.memory[value]
        else:
            return value

@Mode.register(1)
class ValueMode(Mode):
    def resolve_argument(self, process, arg_spec, value):
        if arg_spec.resolve:
            return value
        else:
            raise NotImplementedError

@Mode.register(2)
class RelativeMode(Mode):
    def resolve_argument(self, process, arg_spec, value):
        value = process.relative_base + value
        if arg_spec.resolve:
            return process.memory[value]
        else:
            return value
