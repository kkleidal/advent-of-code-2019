import logging
from intcode import IntCodeProgram


logging.basicConfig(level=logging.DEBUG)

def compute(program):
    for output in IntCodeProgram(program).process().run():
        print(output)

#compute([3,0,4,0,99])
program = [3,225,1,225,6,6,1100,1,238,225,104,0,1101,33,37,225,101,6,218,224,1001,224,-82,224,4,224,102,8,223,223,101,7,224,224,1,223,224,223,1102,87,62,225,1102,75,65,224,1001,224,-4875,224,4,224,1002,223,8,223,1001,224,5,224,1,224,223,223,1102,49,27,225,1101,6,9,225,2,69,118,224,101,-300,224,224,4,224,102,8,223,223,101,6,224,224,1,224,223,223,1101,76,37,224,1001,224,-113,224,4,224,1002,223,8,223,101,5,224,224,1,224,223,223,1101,47,50,225,102,43,165,224,1001,224,-473,224,4,224,102,8,223,223,1001,224,3,224,1,224,223,223,1002,39,86,224,101,-7482,224,224,4,224,102,8,223,223,1001,224,6,224,1,223,224,223,1102,11,82,225,1,213,65,224,1001,224,-102,224,4,224,1002,223,8,223,1001,224,6,224,1,224,223,223,1001,14,83,224,1001,224,-120,224,4,224,1002,223,8,223,101,1,224,224,1,223,224,223,1102,53,39,225,1101,65,76,225,4,223,99,0,0,0,677,0,0,0,0,0,0,0,0,0,0,0,1105,0,99999,1105,227,247,1105,1,99999,1005,227,99999,1005,0,256,1105,1,99999,1106,227,99999,1106,0,265,1105,1,99999,1006,0,99999,1006,227,274,1105,1,99999,1105,1,280,1105,1,99999,1,225,225,225,1101,294,0,0,105,1,0,1105,1,99999,1106,0,300,1105,1,99999,1,225,225,225,1101,314,0,0,106,0,0,1105,1,99999,1107,677,226,224,1002,223,2,223,1005,224,329,101,1,223,223,8,677,226,224,102,2,223,223,1006,224,344,1001,223,1,223,108,677,677,224,1002,223,2,223,1006,224,359,1001,223,1,223,1108,226,677,224,102,2,223,223,1006,224,374,1001,223,1,223,1008,677,226,224,102,2,223,223,1005,224,389,101,1,223,223,7,226,677,224,102,2,223,223,1005,224,404,1001,223,1,223,1007,677,677,224,1002,223,2,223,1006,224,419,101,1,223,223,107,677,226,224,102,2,223,223,1006,224,434,101,1,223,223,7,677,677,224,1002,223,2,223,1005,224,449,101,1,223,223,108,677,226,224,1002,223,2,223,1006,224,464,101,1,223,223,1008,226,226,224,1002,223,2,223,1006,224,479,101,1,223,223,107,677,677,224,1002,223,2,223,1006,224,494,1001,223,1,223,1108,677,226,224,102,2,223,223,1005,224,509,101,1,223,223,1007,226,677,224,102,2,223,223,1005,224,524,1001,223,1,223,1008,677,677,224,102,2,223,223,1005,224,539,1001,223,1,223,1107,677,677,224,1002,223,2,223,1006,224,554,1001,223,1,223,1007,226,226,224,1002,223,2,223,1005,224,569,1001,223,1,223,7,677,226,224,1002,223,2,223,1006,224,584,1001,223,1,223,108,226,226,224,102,2,223,223,1005,224,599,1001,223,1,223,8,677,677,224,102,2,223,223,1005,224,614,1001,223,1,223,1107,226,677,224,102,2,223,223,1005,224,629,1001,223,1,223,8,226,677,224,102,2,223,223,1006,224,644,1001,223,1,223,1108,226,226,224,1002,223,2,223,1006,224,659,101,1,223,223,107,226,226,224,1002,223,2,223,1006,224,674,1001,223,1,223,4,223,99,226]
compute(program)

#def compute(program, input_value=None, verbose=False, get_input=default_get_input, output=default_output):
#    program = list(program)
#    if input_value is not None:
#        program[1] = input_value
#    pc = 0
#    while True:
#        full_op_code = program[pc]
#        op_code = full_op_code % 100
#        if op_code == 99:
#            break
#        if op_code == 1 or op_code == 2 or op_code == 7 or op_code == 8:
#            if verbose:
#                print("=> RUN", program[pc:pc+4])
#            mode1 = (full_op_code // 100) % 10
#            mode2 = (full_op_code // 1000) % 10
#            mode3 = (full_op_code // 10000) % 10
#            if mode3 != 0:
#                raise NotImplementedError("OP: %d" % op_code)
#            pos1 = program[pc + 1]
#            pos2 = program[pc + 2]
#            pos_dest = program[pc + 3]
#            val1 = program[pos1] if mode1 == 0 else pos1
#            val2 = program[pos2] if mode2 == 0 else pos2
#            if verbose:
#                if mode1 == 0:
#                    print("  - DEREF @%d -> %d" % (pos1, val1))
#                else:
#                    print("  - USE ARG %d" % (pos1,))
#                if mode2 == 0:
#                    print("  - DEREF @%d -> %d" % (pos2, val2))
#                else:
#                    print("  - USE ARG %d" % (pos2,))
#            if op_code == 1:
#                if verbose:
#                    print("  - ADD AND STORE IN @%d" % pos_dest)
#                program[pos_dest] = val1 + val2
#            elif op_code == 2:
#                if verbose:
#                    print("  - MULTIPLY AND STORE IN @%d" % pos_dest)
#                program[pos_dest] = val1 * val2
#            elif op_code == 7:
#                program[pos_dest] = 1 if val1 < val2 else 0
#            elif op_code == 8:
#                program[pos_dest] = 1 if val1 == val2 else 0
#            else:
#                raise NotImplementedError("OP: %d" % op_code)
#            pc += 4
#        elif op_code == 3:
#            if verbose:
#                print("=> RUN", program[pc:pc+2])
#            pos_dest = program[pc + 1]
#            mode1 = (full_op_code // 100) % 10
#            if mode1 != 0:
#                raise NotImplementedError("OP: %d" % op_code)
#            input_value = int(get_input().strip())
#            program[pos_dest] = input_value
#            pc += 2
#        elif op_code == 4:
#            if verbose:
#                print("=> RUN", program[pc:pc+2])
#            mode1 = (full_op_code // 100) % 10
#            pos = program[pc + 1]
#            val = program[pos] if mode1 == 0 else pos
#            output(val)
#            pc += 2
#        elif op_code == 5 or op_code == 6:
#            mode1 = (full_op_code // 100) % 10
#            mode2 = (full_op_code // 1000) % 10
#            pos1 = program[pc + 1]
#            pos2 = program[pc + 2]
#            val1 = program[pos1] if mode1 == 0 else pos1
#            val2 = program[pos2] if mode2 == 0 else pos2
#            cond = val1 > 0
#            if op_code == 6:
#                cond = not cond
#            if cond:
#                pc = val2
#            else:
#                pc += 3
#        else:
#            raise NotImplementedError("OP: %d" % op_code)
#
#def compute_with_inputs(program, inputs):
#    def get_input():
#        return str(inputs.pop(0))
#    outputs = []
#    def make_output(output):
#        outputs.append(output)
#    compute(program, get_input=get_input, output=make_output)
#    assert len(inputs) == 0
#    return outputs
#
#def get_phase_seqs(to_choose=set(range(5))):
#    for option in to_choose:
#        rest = to_choose - {option}
#        if len(rest) == 0:
#            yield (option,)
#        else:
#            for others in get_phase_seqs(rest):
#                yield (option,) + others
#
#def optimize_amps(program):
#    best = None
#    argbest = None
#    for option in get_phase_seqs():
#        input_signal = 0
#        for phase in option:
#            input_signal, = compute_with_inputs(program, [phase, input_signal])
#        if best is None or best < input_signal:
#            best = input_signal
#            argbest = option
#    return argbest, best
#
#class Amplifier:
#    def __init__(self, program, phase):
#        self._program = list(program)
#        self._phase = phase
#        self._pc = 0
#        self._inputs = [phase]
#        self._output = None
#        self.last_output = None
#
#    def _advance(self, verbose=False):
#        program = self._program
#        pc = self._pc
#
#        try:
#            full_op_code = program[pc]
#            op_code = full_op_code % 100
#            if op_code == 99:
#                raise StopIteration
#            if op_code == 1 or op_code == 2 or op_code == 7 or op_code == 8:
#                if verbose:
#                    print("=> RUN", program[pc:pc+4])
#                mode1 = (full_op_code // 100) % 10
#                mode2 = (full_op_code // 1000) % 10
#                mode3 = (full_op_code // 10000) % 10
#                if mode3 != 0:
#                    raise NotImplementedError("OP: %d" % op_code)
#                pos1 = program[pc + 1]
#                pos2 = program[pc + 2]
#                pos_dest = program[pc + 3]
#                val1 = program[pos1] if mode1 == 0 else pos1
#                val2 = program[pos2] if mode2 == 0 else pos2
#                if verbose:
#                    if mode1 == 0:
#                        print("  - DEREF @%d -> %d" % (pos1, val1))
#                    else:
#                        print("  - USE ARG %d" % (pos1,))
#                    if mode2 == 0:
#                        print("  - DEREF @%d -> %d" % (pos2, val2))
#                    else:
#                        print("  - USE ARG %d" % (pos2,))
#                if op_code == 1:
#                    if verbose:
#                        print("  - ADD AND STORE IN @%d" % pos_dest)
#                    program[pos_dest] = val1 + val2
#                elif op_code == 2:
#                    if verbose:
#                        print("  - MULTIPLY AND STORE IN @%d" % pos_dest)
#                    program[pos_dest] = val1 * val2
#                elif op_code == 7:
#                    program[pos_dest] = 1 if val1 < val2 else 0
#                elif op_code == 8:
#                    program[pos_dest] = 1 if val1 == val2 else 0
#                else:
#                    raise NotImplementedError("OP: %d" % op_code)
#                pc += 4
#            elif op_code == 3:
#                if verbose:
#                    print("=> RUN", program[pc:pc+2])
#                pos_dest = program[pc + 1]
#                mode1 = (full_op_code // 100) % 10
#                if mode1 != 0:
#                    raise NotImplementedError("OP: %d" % op_code)
#                input_value = self._inputs.pop(0)
#                program[pos_dest] = input_value
#                pc += 2
#            elif op_code == 4:
#                if verbose:
#                    print("=> RUN", program[pc:pc+2])
#                mode1 = (full_op_code // 100) % 10
#                pos = program[pc + 1]
#                val = program[pos] if mode1 == 0 else pos
#                assert self._output is None
#                self._output = val
#                pc += 2
#            elif op_code == 5 or op_code == 6:
#                mode1 = (full_op_code // 100) % 10
#                mode2 = (full_op_code // 1000) % 10
#                pos1 = program[pc + 1]
#                pos2 = program[pc + 2]
#                val1 = program[pos1] if mode1 == 0 else pos1
#                val2 = program[pos2] if mode2 == 0 else pos2
#                cond = val1 > 0
#                if op_code == 6:
#                    cond = not cond
#                if cond:
#                    pc = val2
#                else:
#                    pc += 3
#            else:
#                raise NotImplementedError("OP: %d" % op_code)
#
#        finally:
#            self._pc = pc
#
#    def step(self, input_signal):
#        self._inputs.append(input_signal)
#        while self._output is None:
#            self._advance()
#        out = self._output
#        self._output = None
#        self.last_output = out
#        return out
#
#def optimize_amps_feedback(program):
#    best = None
#    argbest = None
#    for option in get_phase_seqs(set(range(5, 10))):
#        input_signal = 0
#        amps = [Amplifier(program, phase) for phase in option]
#        try:
#            for amp in itertools.cycle(amps):
#                input_signal = amp.step(input_signal)
#        except StopIteration:
#            input_signal = amps[-1].last_output
#        if best is None or best < input_signal:
#            best = input_signal
#            argbest = option
#    return argbest, best
#
#my_input = [3,8,1001,8,10,8,105,1,0,0,21,46,55,76,89,106,187,268,349,430,99999,3,9,101,4,9,9,1002,9,2,9,101,5,9,9,1002,9,2,9,101,2,9,9,4,9,99,3,9,1002,9,5,9,4,9,99,3,9,1001,9,2,9,1002,9,4,9,101,2,9,9,1002,9,3,9,4,9,99,3,9,1001,9,3,9,1002,9,2,9,4,9,99,3,9,1002,9,4,9,1001,9,4,9,102,5,9,9,4,9,99,3,9,101,1,9,9,4,9,3,9,102,2,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,101,2,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,101,1,9,9,4,9,3,9,102,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,1,9,9,4,9,99,3,9,102,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,1,9,9,4,9,3,9,101,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,101,2,9,9,4,9,3,9,1002,9,2,9,4,9,99,3,9,101,1,9,9,4,9,3,9,101,1,9,9,4,9,3,9,101,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,1001,9,2,9,4,9,3,9,1001,9,1,9,4,9,3,9,1001,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,102,2,9,9,4,9,99,3,9,101,1,9,9,4,9,3,9,102,2,9,9,4,9,3,9,101,2,9,9,4,9,3,9,101,1,9,9,4,9,3,9,102,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,101,1,9,9,4,9,99,3,9,1001,9,1,9,4,9,3,9,1001,9,1,9,4,9,3,9,102,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,1001,9,1,9,4,9,3,9,1001,9,1,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,2,9,9,4,9,3,9,101,1,9,9,4,9,99]
#
##print(optimize_amps([3,15,3,16,1002,16,10,16,1,16,15,15,4,15,99,0,0]))
##print(optimize_amps([3,23,3,24,1002,24,10,24,1002,23,-1,23,101,5,23,23,1,24,23,23,4,23,99,0,0]))
##print(optimize_amps([3,31,3,32,1002,32,10,32,1001,31,-2,31,1007,31,0,33,1002,33,7,33,1,33,31,31,1,32,31,31,4,31,99,0,0,0]))
##print(optimize_amps(my_input))
#
#print(optimize_amps_feedback([3,26,1001,26,-4,26,3,27,1002,27,2,27,1,27,26, 27,4,27,1001,28,-1,28,1005,28,6,99,0,0,5]))
#print(optimize_amps_feedback([3,52,1001,52,-5,52,3,53,1,52,56,54,1007,54,5,55,1005,55,26,1001,54,
#    -5,54,1105,1,12,1,53,54,53,1008,54,0,55,1001,55,1,55,2,53,55,53,4,
#    53,1001,56,-1,56,1005,56,6,99,0,0,0,0,10]))
#print(optimize_amps_feedback(my_input))
