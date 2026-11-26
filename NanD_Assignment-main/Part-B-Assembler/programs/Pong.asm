// Minimal keyboard polling example: RAM[0] mirrors whether a key is down.
(LOOP)
@KBD
D=M
@PRESSED
D;JGT
@0
M=0
@LOOP
0;JMP
(PRESSED)
@0
M=1
@LOOP
0;JMP
