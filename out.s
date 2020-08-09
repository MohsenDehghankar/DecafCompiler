

.data
frame_pointer:  .space  10000
global_pointer: .space  10000
true_const:     .asciiz "true"
false_const:    .asciiz "false"
end_of_string:  .byte   0
newline:        .asciiz "\n"

.text
main:
la $s0, frame_pointer;
la $s1, global_pointer;
        




li $v0, 9
li $a0, 16384
syscall
move $a0, $v0
li $v0, 8
li $a1, 16384
syscall
move $v0, $a0
addi $t1, $t1, 0
label1:
lb $t2, ($a0)
lb $t3, newline
beq $t2, $t3, label2
addi $a0, $a0, 1
b label1
label2:
sb $zero, ($a0)
lb $t2, ($v0)
beq $t2, '0', label3
li $t2, 10
li $t0, 0
label5:
lb $t1, ($v0)
beq $t1, $0, label6 
blt $t1, 48, label7
bgt $t1, 57, label7 
addi $t1, $t1, -48
mul $t0, $t0, $t2  
add $t0, $t0, $t1 
addi $v0, $v0, 1  
j label5 
label3:
addi $v0, $v0, 1
lb $t2, ($v0)
beq $t2, 'x', label4
beq $t2, 'X', label4
li $t2, 10
li $t0, 0
j label5
label4:
addi $v0, $v0, 1
li $t2, 16
li $t0, 0
label10:
lb $t1, ($v0)   
beq $t1, $0, label6 
blt $t1, 48, label7  
bgt $t1, 102, label7  
bgt $t1, 96, label13
blt $t1, 97, label12
label13:
addi $t1, $t1, -87
j label8
label12:
blt $t1, 58, label9
bgt $t1, 57, label11
label9:
addi $t1, $t1, -48
j label8
label11:
blt $t1, 65, label7
bgt $t1, 70, label7
addi $t1, $t1, -55 
label8:
mul $t0, $t0, $t2  
add $t0, $t0, $t1   
addi $v0, $v0, 1    
j label10
label7:
li $t0, 0
label6:
        


move $t1, $t0;
                

li $t0, 8;
add $t0, $t0, $s0;
sw $t1, ($t0);
                




li $v0, 1;
li $a0, 8;
add $a0, $a0, $s0;
lw $a0, ($a0);
syscall
                    

li $v0, 4;
la $a0, newline;
syscall
        




    li $v0, 1;
    li $a0, 4659;
    syscall
                    

li $v0, 4;
la $a0, newline;
syscall
        

li $v0, 10;
syscall;
            
