#!/usr/bin/env python3
"""Small Hack CPU emulator with optional Tkinter screen/keyboard window."""
from __future__ import annotations
import argparse
from pathlib import Path

MASK = 0xFFFF
COMP = {
 '0101010':lambda d,a,m:0, '0111111':lambda d,a,m:1, '0111010':lambda d,a,m:-1,
 '0001100':lambda d,a,m:d, '0110000':lambda d,a,m:a, '1110000':lambda d,a,m:m,
 '0001101':lambda d,a,m:~d, '0110001':lambda d,a,m:~a, '1110001':lambda d,a,m:~m,
 '0001111':lambda d,a,m:-d, '0110011':lambda d,a,m:-a, '1110011':lambda d,a,m:-m,
 '0011111':lambda d,a,m:d+1, '0110111':lambda d,a,m:a+1, '1110111':lambda d,a,m:m+1,
 '0001110':lambda d,a,m:d-1, '0110010':lambda d,a,m:a-1, '1110010':lambda d,a,m:m-1,
 '0000010':lambda d,a,m:d+a, '1000010':lambda d,a,m:d+m, '0010011':lambda d,a,m:d-a,
 '1010011':lambda d,a,m:d-m, '0000111':lambda d,a,m:a-d, '1000111':lambda d,a,m:m-d,
 '0000000':lambda d,a,m:d&a, '1000000':lambda d,a,m:d&m, '0010101':lambda d,a,m:d|a,
 '1010101':lambda d,a,m:d|m,
}

def signed(x):
    x &= MASK
    return x - 65536 if x & 0x8000 else x

class HackMachine:
    def __init__(self, program):
        self.rom = [int(line.strip(), 2) for line in program if line.strip()]
        self.ram = [0] * 32768
        self.a = self.d = self.pc = 0
        self.keyboard = 0
        self.steps = 0

    def read(self, address):
        if address == 24576: return self.keyboard
        return self.ram[address & 0x7FFF]

    def write(self, address, value):
        address &= 0x7FFF
        if address != 24576: self.ram[address] = value & MASK

    def step(self):
        if not (0 <= self.pc < len(self.rom)): return False
        instruction = self.rom[self.pc]
        old_a = self.a
        self.pc += 1
        if instruction & 0x8000 == 0:
            self.a = instruction & 0x7FFF
        else:
            bits = f'{instruction:016b}'
            comp = bits[3:10]
            y = self.read(old_a) if bits[3] == '1' else old_a
            out = COMP[comp](signed(self.d), signed(old_a), signed(y)) & MASK
            dest = bits[10:13]
            if dest[2] == '1': self.write(old_a, out)
            if dest[1] == '1': self.d = out
            if dest[0] == '1': self.a = out
            jump = bits[13:16]
            value = signed(out)
            take = [False, value > 0, value == 0, value >= 0, value < 0, value != 0, value <= 0, True][int(jump, 2)]
            if take: self.pc = old_a & 0x7FFF
        self.steps += 1
        return True

    def run(self, max_steps=1000000):
        for _ in range(max_steps):
            if not self.step(): break
        return self.steps

def run_gui(machine, scale=2):
    try:
        import tkinter as tk
    except ImportError as exc:
        raise SystemExit('Tkinter is unavailable. Use --steps for headless execution.') from exc
    root = tk.Tk(); root.title('Hack Computer Emulator — Box Capstone')
    canvas = tk.Canvas(root, width=512*scale, height=256*scale, bg='white', highlightthickness=0)
    canvas.pack()
    status = tk.Label(root, text='Hold any key to draw the box; release to erase. Close window to stop.')
    status.pack()
    def down(_event): machine.keyboard = 1
    def up(_event): machine.keyboard = 0
    root.bind('<KeyPress>', down); root.bind('<KeyRelease>', up)
    def refresh():
        for _ in range(3000): machine.step()
        canvas.delete('pixel')
        for word_index in range(8192):
            word = machine.ram[16384 + word_index]
            if word:
                row, col = divmod(word_index, 32)
                for bit in range(16):
                    if word & (1 << (15-bit)):
                        x = (col*16+bit)*scale; y = row*scale
                        canvas.create_rectangle(x, y, x+scale, y+scale, fill='black', outline='black', tags='pixel')
        root.after(30, refresh)
    refresh(); root.mainloop()

def main():
    p=argparse.ArgumentParser(); p.add_argument('program', nargs='?', type=Path, default=Path(__file__).with_name('Box.hack'))
    p.add_argument('--steps', type=int, default=100000); p.add_argument('--key', action='store_true'); p.add_argument('--gui', action='store_true')
    args=p.parse_args(); machine=HackMachine(args.program.read_text().splitlines())
    if args.key: machine.keyboard=1
    if args.gui: run_gui(machine); return
    machine.run(args.steps)
    print(f'Executed {machine.steps} instructions; PC={machine.pc}, A={machine.a}, D={machine.d}')
    print('Non-zero screen words:', sum(1 for x in machine.ram[16384:24576] if x))

if __name__=='__main__': main()
