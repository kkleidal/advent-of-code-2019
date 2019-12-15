import argparse
import json
import pdb
import logging

from intcode.ops import Op
from intcode.program import Instruction

logger = logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument("input_file", type=argparse.FileType("r"))
args = parser.parse_args()

class Run:
    def __init__(self, command, t, instruction, args, arg_values):
        self.command = command
        self.t = t
        self.instruction = instruction
        self.args = args
        self.arg_values = arg_values
        self.next_op = None
        self.prev_op = None
        self.game_score_update_value = None
        self.game_screen_update_pos = None
        self.game_screen_update_tile = None
        self.addresses_read = {}
        self.addresses_written = {}

    def read_address(self, addr, value):
        self.addresses_read[addr] = value
        self.command.addresses_read.add(addr)

    def write_address(self, addr, value):
        self.addresses_written[addr] = value
        self.command.addresses_written.add(addr)

    def set_game_screen_update(self, pos, tile):
        self.game_screen_update_pos = pos
        self.game_screen_update_tile = tile
        self.command.game_screen_update_positions.add(pos)
        self.command.game_screen_update_tiles.add(tile.__class__)

    def set_game_score_update(self, score):
        self.game_score_update_value = score
        self.command.game_score_update = True

    def set_next_op(self, run):
        self.next_op = run
        run.prev_op = self
        run.command.sources.add(self.command)
        self.command.branches.add(run.command)

class Command:
    def __init__(self, pc):
        self.pc = pc
        self.code = set()
        self.sources = set()
        self.branches = set()
        self.runs = []
        self.game_screen_update_positions = set()
        self.game_screen_update_tiles = set()
        self.game_score_update = False
        self.addresses_written = set()
        self.addresses_read = set()
        self.comments = []

    def add_comment(self, comment):
        self.comments.append(comment)

    def render(self):
        codes = set(code[0] for code in self.code)
        if len(codes) > 1:
            logger.warn("Multiple codes for op at PC %d", self.pc)
        code = next(iter(codes))
        instruction = Instruction(code)
        op = Op.registry[instruction.op_code]
        args = set(code[1] for code in self.code)
        lines = []
        for comment in self.comments:
            lines.append("  # Comment: %s" % comment)
        if self.game_score_update:
            lines.append("  # Game score update")
        lines.append("  # Jumps from %s, jumps to %s" % ({x.pc for x in self.sources},
                                                         {x.pc for x in self.branches}))
        if self.game_screen_update_positions:
            lines.append("  # Screen update (%d positions, %d tile types)" % (len(self.game_screen_update_positions),
                                                                              len(self.game_screen_update_tiles)))

        lines.append("%d: %s" % (self.pc, op.render(instruction, args)))
        return lines

    def run(self, t, instruction, args, arg_values):
        self.code.add((instruction, args))
        run = Run(self, t, instruction, args, arg_values)
        self.runs.append(run)
        return run

    def set_next_op(self, run):
        self.runs[-1].set_next_op(run)

    def __str__(self):
        return "<Command pc=%d codes=%r runs=%d branches=%r sources=%r>" % (self.pc, self.code, len(self.runs),
                                                                           {cmd.pc for cmd in self.branches},
                                                                           {cmd.pc for cmd in self.sources})

    def __repr__(self):
        return str(self)

class Events:
    GAME_SCREEN_UPDATE = 0
    GAME_SCORE_UPDATE = 1
    WAITING_FOR_INPUT = 2
    RECEIVED_INPUT = 3
    WAITING_FOR_OUTPUT = 4
    SENT_OUTPUT = 5
    BEFORE_STEP = 6
    AFTER_STEP = 7
    HALT = 8
    MEMORY_WRITE = 9
    MEMORY_READ = 10

cfg = {}
t = 0
run = None
last_run = None
in_step = False
for line in args.input_file:
    event = json.loads(line)
    if event[0] == Events.MEMORY_READ:
        if in_step and run is not None:
            run.read_address(event[1][0], event[1][1])
        continue
    elif event[0] == Events.MEMORY_WRITE:
        if in_step and run is not None:
            run.write_address(event[1][0], event[1][1])
        continue
    elif event[0] == Events.BEFORE_STEP:
        pc, instruction, args, arg_values = event[1]
        args = tuple(args)
        if pc not in cfg:
            cfg[pc] = Command(pc)
        run = cfg[pc].run(t, instruction, args, arg_values)
        in_step = True
        if last_run is not None:
            last_run.set_next_op(run)
        continue
    elif event[0] == Events.AFTER_STEP:
        last_run = run
        in_step = False
        continue
    elif event[0] == Events.WAITING_FOR_OUTPUT:
        continue
    elif event[0] == Events.SENT_OUTPUT:
        continue
    elif event[0] == Events.WAITING_FOR_INPUT:
        continue
    elif event[0] == Events.RECEIVED_INPUT:
        continue
    elif event[0] == Events.GAME_SCREEN_UPDATE:
        run.set_game_screen_update(tuple(event[1][0]), event[1][1])
        continue
    elif event[0] == Events.GAME_SCORE_UPDATE:
        run.set_game_score_update(event[1][0])
        continue
    elif event[0] == Events.HALT:
        continue
    raise NotImplementedError("Event: %r" % (event,))

branches = []
for pc, cmd in cfg.items():
    if len(cmd.sources) > 1 or pc == 0 or len(cfg[next(iter(cmd.sources)).pc].branches) > 1:
        branches.append(pc)
branches_set = set(branches)
print(branches)

def add_comment(memory, comment):
    cfg[memory].add_comment(comment)

add_comment(578, "function(y, x) -> memory[693 + y * 40 + x]")
add_comment(578, "this is like moving the stack pointer")
add_comment(580, "y (arg[0]) * 40 -> cell (@593)")
add_comment(584, "x (arg[1]) + cell -> cell (@593)")
add_comment(584, "639 (memory offset) + cell -> cell (@593)")
add_comment(592, "@cell -> (arg[1])")
add_comment(596, "return")

add_comment(0, "Quarter logic. Probably add -> multiply when you 'add quarters'")
add_comment(12, "Stack base @2640")
add_comment(14, "Set y = 0")
add_comment(18, "Set x = 0")
add_comment(22, "Set x -> arg[1] of future call")
add_comment(26, "Set y -> arg[0] of future call")
add_comment(30, "Set return pointer for future call")
add_comment(34, "Make call")
add_comment(37, "Output x")
add_comment(39, "Output y")
add_comment(41, "Output return value from call (the tile there)")

for branch in branches:
    print("branch%d:" % branch)
    pc = branch
    while True:
        cmd = cfg[pc]

        for line in cmd.render():
            print("  ", line)

        remaining = set(n.pc for n in cmd.branches) - branches_set
        assert len(remaining) <= 1
        if len(remaining) == 1:
            pc = next(iter(remaining))
        else:
            break
    print()
print(branches)


