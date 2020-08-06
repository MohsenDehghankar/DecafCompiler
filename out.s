
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
        





li $a0, 44;
li $v0, 9;
syscall
li $t0 , 10;
sw $t0, 0($v0);
li $t0, 16
add $t0, $t0, $s0;
sw $v0, ($t0)
        


li $t0, 16;
add $t0, $t0, $s0;
lw $t0, ($t0);
            

li $t1, 12;
add $t1, $t1, $s0;
sw $t0, ($t1);
                



li $t0, 12;
add $t0, $t0, $s0
lw $t0, ($t0);
addi $t0, $t0, 16;
            

li $v0, 9;
li $a0, 4;
syscall
        

li $a0,'A';
sb $a0,0($v0);
                            

li $a0,'b';
sb $a0,1($v0);
                            

li $a0,'c';
sb $a0,2($v0);
                            

lb $a0,end_of_string;
sb $a0,3($v0);
                            

move $t1, $v0;
        

sw $t1, ($t0);
                    



li $v0, 9;
li $a0, 4;
syscall
        

li $a0,'A';
sb $a0,0($v0);
                            

li $a0,'b';
sb $a0,1($v0);
                            

li $a0,'c';
sb $a0,2($v0);
                            

lb $a0,end_of_string;
sb $a0,3($v0);
                            

move $t0, $v0;
        

li $t1, 8;
add $t1, $t1, $s0;
sw $v0, ($t1);
                    





li $t0, 12;
add $t0, $t0, $s0
lw $t0, ($t0);
addi $t0, $t0, 16;
            

li $v0, 9;
li $a0, 4;
syscall
        

li $a0,'A';
sb $a0,0($v0);
                            

li $a0,'b';
sb $a0,1($v0);
                            

li $a0,'c';
sb $a0,2($v0);
                            

lb $a0,end_of_string;
sb $a0,3($v0);
                            

move $t2, $v0;
        

lw $t1, ($t0);
        

li $t3, 0
label1:
lb $t4, 0($t1)
lb $t5, 0($t2)
add $t1, $t1, 1
add $t2, $t2, 1
beqz $t4, label2
beqz $t5, label2
bne $t4, $t5, label3
beq $t4, $t5, label1
label3:
li $t3, 0
j label4
label5:
li $t3, 1
j label4
label2:
beq $t4, $t5, label5
label4:
                

beq $t3, $zero, label6;
        





    li $v0, 1;
    li $a0, 2;
    syscall
                    

li $v0, 4;
la $a0, newline;
syscall
        

b label7;
label6:
        

label7:
        

li $v0, 10;
syscall;
            


adde:

sw $ra, 4($s0);
        





li $v0, 4;
li $a0, -8;
add $a0, $a0, $s0;
lw $a0, ($a0);
syscall
                    

li $v0, 4;
la $a0, newline;
syscall
        

lw $ra, 4($s0);
lw $v0, -4($s0);
lw $s0, ($s0)
jr $ra;
