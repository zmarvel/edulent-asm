.text
TRACE
MOV A, 5
MOV B, 6
MOV AP, @table    
MOV A, [AP]       
MOV A, [@table+1] 
MOV AP, [@table+2]
HALT

.data
table:
.byte 0x0e
.byte 0x13
.byte 0x14
