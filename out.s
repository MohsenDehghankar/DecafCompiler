

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
        

li $a0,'a';
sb $a0,0($v0);
                            

li $a0,'b';
sb $a0,1($v0);
                            

li $a0,'c';
sb $a0,2($v0);
                            

lb $a0,end_of_string;
sb $a0,3($v0);
                            

move $t1, $v0;
        

sw $t1, ($t0);
                    




li $t2, 32;
        





li $t0, 35;
                


li $t1, 2;
                

add $t0, $t0, $t1
        

li $t3, -4;
add $t3, $t3, $t2;
            

move $t4, $t0;
add $t3, $t3, $s0;
sw $t4, ($t3);
                    


li $t1, 12;
add $t1, $t1, $s0
lw $t1, ($t1);
addi $t1, $t1, 16;
            

li $t3, -8;
add $t3, $t3, $t2;
            

lw $t4, ($t1);
add $t3, $t3, $s0;
sw $t4, ($t3);
                    

li $t4, 32;
add $t4, $t4, $s0;
sw $s0, ($t4);
        

move $t4, $s0;
add $t4, $t4, 32
move $s0, $t4;
jal adde;
        

move $t4, $v0;
        

li $v0, 1;
move $a0, $t4;
syscall
                        

li $v0, 4;
la $a0, newline;
syscall
        

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