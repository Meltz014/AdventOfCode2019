
from copy import deepcopy

class HandHeld():
    """
    CPU emulator for "Hand Held gaming device"
    """
    valid_opcodes = ['acc', 'nop', 'jmp']
    def __init__(self, raw_instructions):
        self.callback = None
        self._pc = 0
        self._acc = 0
        self.go = True
        self.finished = False
        # parse raw instructions
        self.program = []
        for line in raw_instructions:
            (instr, i_arg) = line.strip().split(' ')
            self.program.append((instr, int(i_arg)))
        self.original_program = deepcopy(self.program)

        self.pc_hist = []

    def reset(self):
        self._pc = 0
        self._acc = 0
        self.go = True
        self.pc_hist = []
        self.finished = False
        self.program = deepcopy(self.original_program)

    def run(self, callback=None):
        if callback:
            self.callback = callback
        while self.go:
            if self.callback:
                self.callback(self)
            (instr, i_arg) = self.program[self._pc]
            # keep track of instr calls
            self.pc_hist.append(self._pc)
            # run op func
            if instr in self.valid_opcodes:
                getattr(self, instr)(i_arg)
            else:
                print(f'invalid opcode: {instr, i_arg}')
                self.halt()
                break
            if self._pc == len(self.program):
                self.finished = True
                self.halt()

    def halt(self):
        self.go = False

    def acc(self, amt):
        self._acc += amt
        self._pc += 1

    def nop(self, *args):
        # no op; do nothing
        self._pc += 1

    def jmp(self, offset):
        self._pc += offset


def part1(hh):
    def part1_cb(hh):
        if hh._pc in hh.pc_hist:
            print(f'Inst. being run twice: {hh.program[hh._pc]}')
            print(f'Part1: Acc val: {hh._acc}')
            hh.halt()

    hh.reset()
    hh.run(callback=part1_cb)

def part2(hh):
    """
    Attempt to rewrite program to fix execution.  Exactly one NOP or JMP instruction needs to be switched to JMP or NOP
    """
    flipped_inst = []
    new_inst = []
    def part2_cb(hh):
        nonlocal flipped_inst, new_inst
        if hh._pc in hh.pc_hist:
            # instr has been run already (i.e. stuck in a loop)
            # look in the hist for most recent jmp or nop, flip it, and run again
            while True:
                if hh.pc_hist:
                    pc = hh.pc_hist.pop()
                    if pc in flipped_inst:
                        # already tried this one.  Move on
                        continue
                    (inst, i_arg) = hh.program[pc]
                    if inst == 'nop':
                        inst = 'jmp'
                    elif inst == 'jmp':
                        inst = 'nop'
                    else:
                        continue

                    flipped_inst.append(pc)
                    new_inst.append((pc, (inst, i_arg)))
                    break
                else:
                    raise Exception('Couldnt find any more nop or jmp opcodes')
            hh.halt()

    while not hh.finished:
        hh.reset()
        if new_inst:
            (pc, instruction) = new_inst.pop()
            hh.program[pc] = instruction
        hh.run(callback = part2_cb)

    print(f'Part 2: acc value: {hh._acc}')

def main():
    with open('day8\input.txt') as fid:
        instructions = fid.readlines()

    hh = HandHeld(instructions)
    part1(hh)
    part2(hh)

if __name__ == '__main__':
    main()