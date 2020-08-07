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
        





li $v0, 9;
li $a0, 6;
syscall
        

li $a0,'s';
sb $a0,0($v0);
                            

li $a0,'a';
sb $a0,1($v0);
                            

li $a0,'l';
sb $a0,2($v0);
                            

li $a0,'a';
sb $a0,3($v0);
                            

li $a0,'m';
sb $a0,4($v0);
                            

lb $a0,end_of_string;
sb $a0,5($v0);
                            

move $t0, $v0;
        

li $t1, 8;
add $t1, $t1, $s0;
sw $v0, ($t1);
                    





la $a0, input
li $v0, 8
li $a1, 16384
syscall
addi $t0, $t0, 0
label1:
lb $t0, ($a0)
lb $t1, newline
beq $t0, $t1, label2
addi $a0, $a0, 1
b label1   
label2:
sb $zero, ($a0)
la $a0, input
move $t0,$a0
        



li $t1, 8;
add $t1, $t1, $s0;
lw $t1, ($t1);
            

move $t0,$t0;
        

li $t2, 0
label3:
lb $t3, 0($t0)
lb $t4, 0($t1)
add $t0, $t0, 1
add $t1, $t1, 1
beqz $t3, label4
beqz $t4, label4
bne $t3, $t4, label5
beq $t3, $t4, label3
label5:
li $t2, 0
j label6
label7:
li $t2, 1
j label6
label4:
beq $t3, $t4, label7
label6:
                

beq $t2, $zero, label8;
la $a0, true_const;
j label9;
label8:
la $a0, false_const;
label9:
li $v0, 4;
syscall
                    

li $v0, 4;
la $a0, newline;
syscall
        

li $v0, 10;
syscall;