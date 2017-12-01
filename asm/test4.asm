TRACE

MOV A, 0
MOV B, 5
MOV AP, @table
loop:
ADD A, [AP]
ADD AP, 1
SUB B, 1
JZ done
JMP loop
done:
OUT [0], A

HALT

table:
.byte 01
.byte 02
.byte 03
.byte 04
.byte 05
