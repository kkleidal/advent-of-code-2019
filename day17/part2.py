from intcode import IntCodeProgram

with open("input.txt", "r") as f:
    code = list(map(int, f.read().strip().split(",")))
    code[0] = 2
    program = IntCodeProgram(code)


video = False

with open("program.txt", "r") as f:
    vaccuum_program = []
    i = 0
    for line in f:
        line = line.strip()
        if line.startswith("#") or len(line) == 0:
            continue
        if line == "video":
            video = True
            continue
        line = [x.strip() for x in line.strip().split(",")]
        if i == 0:
            for operator in line:
                assert operator in {"A", "B", "C"}
        elif i > 0 and i < 4:
            for j, operator in enumerate(line):
                assert operator in ({"R", "L"} | set(map(str, range(10))))
        line = [ord(c) for c in (",".join(line) + "\n")]
        assert len(line) <= 20, "Line %d of program has too many characters (max: 20)" % (i + 1)
        vaccuum_program.extend(line)
        i += 1

process = program.process()
last_out = None
buf = []
for out in process.run(inputs=vaccuum_program + [ord("y" if video else "n"), ord("\n")]):
    try:
        out = chr(out)
    except ValueError:
        print("Final output: %d" % out)
        break
    if last_out == out == "\n":
        print(chr(27) + "[2J")
        print("".join(buf), end="", flush=True)
        buf = []
    else:
        buf.append(out)
    last_out = out
