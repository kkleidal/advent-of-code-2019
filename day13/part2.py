from intcode.ops import Op
from intcode.arg_modes import Mode
from game import IntCodeProgram, ProgramExitted, ArcadeGame, GameHook
import json
import re

def game_factory(hooks=[]):
    with open("input.txt", "r") as f:
        program = IntCodeProgram(list(map(int, f.read().strip().split(","))))
        game = ArcadeGame(program, hooks=hooks)
        game.insert_quarters()
    return game

def parse_command(cmd):
    m = re.match(r"^(\d*)([hjk])$", cmd)
    if m is None:
        return None
    count = m.group(1)
    if len(count) == 0:
        count = "1"
    count = int(count)
    action = {"h": -1, "j": 0, "k": 1}[m.group(2)]
    return count, action


def run_game(game_factory=game_factory, hooks=[]):
    game = game_factory(hooks=hooks)
    buf = []
    try:
        game.step()
        while True:
            game.step()
            game.terminal_render()
            while True:
                if len(buf) > 0:
                    direction = buf.pop(0)
                    break
                print("Left (h) center (j) or right (k)? ", end="", flush=True)
                inp = parse_command(input())
                if inp is None:
                    continue
                count, direction = inp
                buf.extend(count * [direction])
            game.send(direction)
    except ProgramExitted:
        game.terminal_render()

def get_state(game):
    if isinstance(game, ArcadeGame):
        process = game.process
    else:
        process = game
    pc = process.instruction_pointer
    instruction = process.instruction
    op = Op.registry[instruction.op_code]
    args = []
    arg_values = []
    for i, arg_spec in enumerate(op.args):
        value = process.memory[process.instruction_pointer + i + 1]
        args.append(value)
        mode = Mode.registry[instruction.argument_mode(i)]
        value = mode.resolve_argument(process, arg_spec, value)
        arg_values.append(value)
    return (pc, instruction.code, tuple(args), tuple(arg_values))

#def decompile_game(writer):
#    game = game_factory()
#    try:
#        while True:
#            if game.process.waiting_for_input():
#                game.terminal_render()
#                while True:
#                    print("Left (h) center (j) or right (l)? ", end="", flush=True)
#                    directions = {"h": -1, "j": 0, "k": 1}
#                    inp = input()
#                    if inp not in directions:
#                        continue
#                    direction = directions[inp]
#                    break
#                game.send(direction)
#            elif game.process.waiting_for_output():
#                game.step()
#                game.terminal_render()
#            else:
#                state = get_state(game)
#                writer.write_state(state)
#                game.process.step()
#    except ProgramExitted:
#        game.terminal_render()

class WriterHook(GameHook):
    def __init__(self, writer):
        self.writer = writer

    def _write_to_ledger(self, value):
        self.writer.write_event(value)

    def on_game_screen_updated(self, game, pos, tile):
        self._write_to_ledger((0, (pos, tile.code)))

    def on_game_score_updated(self, game, score):
        self._write_to_ledger((1, (score,)))

    def on_waiting_for_input(self, process, dest):
        self._write_to_ledger((2, (dest,)))

    def on_received_input(self, process, dest, input):
        self._write_to_ledger((3, (dest, input)))

    def on_waiting_for_output(self, process, value):
        self._write_to_ledger((4, (value,)))

    def on_sent_output(self, process, value):
        self._write_to_ledger((5, (value,)))

    def before_step(self, process):
        state = get_state(process)
        self._write_to_ledger((6, state))

    def after_step(self, process):
        self._write_to_ledger((7, ()))

    def on_halt(self, process):
        self._write_to_ledger((8, ()))

    def on_memory_write(self, address, value):
        self._write_to_ledger((9, (address, value)))

    def on_memory_read(self, address, value):
        self._write_to_ledger((10, (address, value)))

class GameStateWriter:
    def __init__(self, filename):
        self.filename = filename
        self.fileobj = None

    def __enter__(self):
        self.fileobj = open(self.filename, "w")
        return self

    def __exit__(self, *args):
        self.fileobj.close()

    def write_event(self, event):
        self.fileobj.write(json.dumps(event))
        self.fileobj.write("\n")

    def hook(self):
        return WriterHook(self)

def hacked_game_factory(hooks=[]):
    with open("input.txt", "r") as f:
        program = IntCodeProgram(list(map(int, f.read().strip().split(","))))
        game = ArcadeGame(program, hooks=hooks)
        y = 24
        for x in range(40):
            game.process.memory[639 + y * 40 + x] = 1
        game.insert_quarters()
    return game

with GameStateWriter("game-states.json") as writer:
    run_game(game_factory=hacked_game_factory, hooks=[writer.hook()])
