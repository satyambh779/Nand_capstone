// Computes RAM[2] = RAM[0] + RAM[1]
@2
M=0
@0
D=M
@1
D=D+M
@2
M=D
(END)
@END
0;JMP
