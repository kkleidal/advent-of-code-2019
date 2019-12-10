def compute(program):
    pc = 0
    while True:
        op_code = program[pc]
        if op_code == 99:
            break
        elif op_code == 1 or op_code == 2:
            pos1 = program[pc + 1]
            pos2 = program[pc + 2]
            pos_dest = program[pc + 3]
            val1 = program[pos1]
            val2 = program[pos2]
            if op_code == 1:
                program[pos_dest] = val1 + val2
            elif op_code == 2:
                program[pos_dest] = val1 * val2
        else:
            raise RuntimeError("Illegal op: %d" % op_code)
        pc += 4

def problem(program):
    program[1] = 12
    program[2] = 2
    compute(program)
    return program[0]

tests = [
    ([1,9,10,3,2,3,11,0,99,30,40,50], [3500,9,10,70,2,3,11,0,99,30,40,50]),
    ([1,0,0,0,99], [2,0,0,0,99]),
    ([2,3,0,3,99], [2,3,0,6,99]),
    ([2,4,4,5,99,0], [2,4,4,5,99,9801]),
    ([1,1,1,4,99,5,6,0,99], [30,1,1,4,2,5,6,0,99]),
]
for initial, final in tests:
    output = list(initial)
    compute(output)
    if tuple(output) != tuple(final):
        print("ERROR: %s != %s" % (output, final))

print(problem([1,0,0,3,1,1,2,3,1,3,4,3,1,5,0,3,2,1,10,19,1,19,5,23,2,23,6,27,1,27,5,31,2,6,31,35,1,5,35,39,2,39,9,43,1,43,5,47,1,10,47,51,1,51,6,55,1,55,10,59,1,59,6,63,2,13,63,67,1,9,67,71,2,6,71,75,1,5,75,79,1,9,79,83,2,6,83,87,1,5,87,91,2,6,91,95,2,95,9,99,1,99,6,103,1,103,13,107,2,13,107,111,2,111,10,115,1,115,6,119,1,6,119,123,2,6,123,127,1,127,5,131,2,131,6,135,1,135,2,139,1,139,9,0,99,2,14,0,0]))
