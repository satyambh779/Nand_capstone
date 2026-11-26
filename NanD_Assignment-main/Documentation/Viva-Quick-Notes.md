# Viva Quick Notes — Hack Computer Capstone (K=93)

## 1. Hack computer
A 16-bit von Neumann-style computer from Nand2Tetris. It has a CPU, memory, and instruction ROM. Instructions are 16 bits long.

## 2. CPU architecture
The CPU contains the A register, D register, ALU, and program counter (PC). The A register stores addresses/constants, D is a general-purpose data register, and the ALU performs arithmetic and logical operations.

## 3. Fetch–decode–execute
The PC selects an instruction from ROM; the CPU decodes its fields; the ALU/registers/memory perform the operation; jump bits may load a new PC value.

## 4. Hack ISA
- A-instruction: `0vvvvvvvvvvvvvvv`, loads a 15-bit value/address into A.
- C-instruction: `111accccccdddjjj`, contains computation, destination, and jump fields.

## 5. Two-pass assembler
- Pass 1 records labels and their ROM addresses.
- Pass 2 translates instructions and allocates variables from RAM address 16.

## 6. Symbol table
Maps names to numeric addresses. Predefined names include R0–R15, SP, LCL, ARG, THIS, THAT, SCREEN, and KBD. Labels map to ROM addresses; variables map to RAM addresses.

## 7. Memory map
- RAM: 0–16383
- Screen: 16384–24575
- Keyboard: 24576
- One screen word represents 16 horizontal pixels; each row contains 32 words (512 pixels).

## 8. K=93 customizations
- `93 % 3 = 1`: invalid assembler instruction reports its original line number.
- `93 % 4 = 3`: width = `16 × (3+1) = 64` pixels.
- Starting row = 93; height = 20 rows; left edge = x=0.

## 9. Box program
The program continuously reads KBD. If a key is down, it writes nonzero bit masks to the mapped screen words. When no key is down, it writes zero to those same words, erasing the box.

## 10. Testing
Python tests verify instruction encoding, symbol allocation, line-numbered errors, and the box's draw/erase behavior. The HDL chips must additionally be checked with the official Hardware Simulator test files supplied with the course.
