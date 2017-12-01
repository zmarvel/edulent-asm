TRACE
MOV A, 5
MOV B, 6
MOV AP, 0x0d
MOV A, [AP]       
MOV A, [0x0e] 
MOV AP, [0x0f]
HALT
.byte 0x0e
.byte 0x13
.byte 0x14
