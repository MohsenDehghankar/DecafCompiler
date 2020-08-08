.data
frame_pointer:  .space  10000
global_pointer: .space  10000
input:          .space  16384
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
move $t0,$v0
        


move $v0,$t0;
                

li $t0, 8;
add $t0, $t0, $s0;
sw $v0, ($t0);
                    


li $v0, 9
li $a0, 16384
syscall
move $a0, $v0
li $v0, 8
li $a1, 16384
syscall
move $v0, $a0
addi $t1, $t1, 0
label3:
lb $t2, ($a0)
lb $t3, newline
beq $t2, $t3, label4
addi $a0, $a0, 1
b label3   
label4:
sb $zero, ($a0)
move $t0,$v0
        


move $v0,$t0;
                

li $t0, 12;
add $t0, $t0, $s0;
sw $v0, ($t0);
                    




li $v0, 4;
li $a0, 8;
add $a0, $a0, $s0;
lw $a0, ($a0);
syscall
                    

li $v0, 4;
la $a0, newline;
syscall
        




li $v0, 4;
li $a0, 12;
add $a0, $a0, $s0;
lw $a0, ($a0);
syscall
                    

li $v0, 4;
la $a0, newline;
syscall
        







li $t1, 12;
add $t1, $t1, $s0;
lw $t1, ($t1);
            



li $t0, 8;
add $t0, $t0, $s0;
lw $t0, ($t0);
            

li $t2, 0
label5:
lb $t3, 0($t0)
lb $t4, 0($t1)
add $t0, $t0, 1
add $t1, $t1, 1
beqz $t3, label6
beqz $t4, label6
bne $t3, $t4, label7
beq $t3, $t4, label5
label7:
li $t2, 0
j label8
label9:
li $t2, 1
j label8
label6:
beq $t3, $t4, label9
label8:
                

beq $t2, $zero, label10;
la $a0, true_const;
j label11;
label10:
la $a0, false_const;
label11:
li $v0, 4;
syscall
                    

li $v0, 4;
la $a0, newline;
syscall
        

li $v0, 10;
syscall;