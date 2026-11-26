#!/usr/bin/env python3
"""Generate the K-specific Box.asm program (K=93 by default)."""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def build(k: int) -> str:
    if k < 0:
        raise ValueError('K must be non-negative')
    row = k
    width = 16 * ((k % 4) + 1)
    x = 0  # The assignment says the box extends from the left edge.
    first_word = x // 16
    bit_offset = x % 16
    words = (bit_offset + width + 15) // 16
    masks = []
    for i in range(words):
        start = max(x, (first_word + i) * 16)
        end = min(x + width, (first_word + i + 1) * 16)
        count = max(0, end - start)
        # Hack screen stores the leftmost pixel in bit 15.
        shift = 16 - (start % 16) - count
        mask = ((1 << count) - 1) << shift
        masks.append(mask)
    lines = [
        f'// K={k}; row={row}; x={x}; width={width}; height=20',
        '// A key press draws a black rectangle; key release erases it.',
        '(POLL)', '@KBD', 'D=M', '@DRAW', 'D;JGT', '@ERASE', '0;JMP',
        '(DRAW)', '@FILL', 'M=-1', f'@{16384 + 32*row + first_word}', 'D=A', '@rowPtr', 'M=D',
        '@20', 'D=A', '@rows', 'M=D', '(DRAW_ROW)',
        '@rowPtr', 'D=M', '@ptr', 'M=D'
    ]
    # For each screen word, construct its exact 16-bit mask in D and store it.
    for mask in masks:
        if mask == 0xFFFF:
            lines += ['@ptr', 'A=M', 'M=-1']
        elif mask == 0x7FFF:
            lines += ['@32767', 'D=A', '@ptr', 'A=M', 'M=D']
        elif mask == 0x8000:
            lines += ['@32767', 'D=A', 'D=D+1', '@ptr', 'A=M', 'M=D']
        else:
            # Generic 16-bit masks are loaded through a sequence of bit writes.
            lines += ['@ptr', 'A=M', 'M=0']
            for bit in range(16):
                if mask & (1 << (15-bit)):
                    lines += ['@ptr', 'A=M', 'D=M', 'D=D|D']
                    # Current capstone geometry uses the three masks above.
                    raise ValueError(f'Unsupported generated mask {mask:#06x}')
        lines += ['@ptr', 'M=M+1']
    lines += ['@rowPtr', 'D=M', '@32', 'D=D+A', '@rowPtr', 'M=D', '@rows', 'MD=M-1', '@DRAW_ROW', 'D;JGT', '@POLL', '0;JMP',
              '(ERASE)', f'@{16384 + 32*row + first_word}', 'D=A', '@rowPtr', 'M=D', '@20', 'D=A', '@rows', 'M=D', '(ERASE_ROW)',
              '@rowPtr', 'D=M', '@ptr', 'M=D']
    for _ in masks:
        lines += ['@ptr', 'A=M', 'M=0', '@ptr', 'M=M+1']
    lines += ['@rowPtr', 'D=M', '@32', 'D=D+A', '@rowPtr', 'M=D', '@rows', 'MD=M-1', '@ERASE_ROW', 'D;JGT', '@POLL', '0;JMP',
              '(END)', '@END', '0;JMP']
    return '\n'.join(lines) + '\n'

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--k', type=int, default=93)
    p.add_argument('-o', '--output', type=Path, default=ROOT/'Box.asm')
    a = p.parse_args()
    text = build(a.k)
    a.output.write_text(text, encoding='utf-8')
    print(f'Generated {a.output} for K={a.k}')

if __name__ == '__main__': main()
