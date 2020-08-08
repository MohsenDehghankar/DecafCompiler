

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
        




li $a0, 56;
li $v0, 9;
syscall
li $t0 , 13;
sw $t0, 0($v0);
li $t0, 12
add $t0, $t0, $s0;
sw $v0, ($t0)
lw $t0, ($t0)
        



li $t1, 8;
add $t1, $t1, $s0;
sw $t0, ($t1);
                



li $t0, 8;
add $t0, $t0, $s0
lw $t0, ($t0);
addi $t0, $t0, 16;
            

li $t1, 21;
            

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
jal fun;
        

move $t2, $v0;
        


move $t0, $t2;
                

li $t1, 16;
add $t1, $t1, $s0;
sw $t0, ($t1);
                




li $v0, 1;
li $a0, 16;
add $a0, $a0, $s0;
lw $a0, ($a0);
syscall
                    

li $v0, 4;
la $a0, newline;
syscall
        

li $v0, 10;
syscall;
            

fun:

sw $ra, 4($s0);
        



li $t0, -4;
add $t0, $t0, $s0
lw $t0, ($t0);
addi $t0, $t0, 16;
            
lw $ra, 4($s0);
lw $v0, ($t0)
lw $s0, ($s0);
jr $ra;
                
