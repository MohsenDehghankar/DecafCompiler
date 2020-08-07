

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
        




li $a0, 32;
li $v0, 9;
syscall
li $t0 , 7;
sw $t0, 0($v0);
li $t0, 12
add $t0, $t0, $s0;
sw $v0, ($t0)
        



li $t1, 8;
add $t1, $t1, $s0;
sw $t0, ($t1);
                



li $t0, 8;
add $t0, $t0, $s0
lw $t0, ($t0);
addi $t0, $t0, 16;
            

li $t1, 12;
            

sw $t1, ($t0);
                    




li $t0, 24;
        


li $t1, -4;
add $t1, $t1, $t0;
            

lw $t2, 8($s0);
add $t1, $t1, $s0;
sw $t2, ($t1);
                    

li $t2, 24;
add $t2, $t2, $s0;
sw $s0, ($t2);
        

move $t2, $s0;
add $t2, $t2, 24
move $s0, $t2;
jal arr;
        

move $t2, $v0;
        

move $a0, $v0;
li $v0, 4;
syscall
                    

li $v0, 4;
la $a0, newline;
syscall
        

li $v0, 10;
syscall;
            

arr:

sw $ra, 4($s0);
        


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
                            

move $t0, $v0;
        
lw $ra, 4($s0);
move $v0, $t0;
lw $s0, ($s0);
jr $ra;
                    