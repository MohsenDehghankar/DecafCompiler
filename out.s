

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
        




li $a0, 32;
li $v0, 9;
syscall
li $t0 , 7;
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
            

li $t1, 12;
            

sw $t1, ($t0);
                    




li $t0, 8;
add $t0, $t0, $s0
lw $t0, ($t0);
addi $t0, $t0, 16;
            

li $v0, 1;
lw $a0, ($t0);
syscall
                        

li $v0, 4;
la $a0, newline;
syscall
        




li $t0, 10;
            

li $t1, 16;
add $t1, $t1, $s0;
sw $t0, ($t1);
                




li $t0, 30;
            

li $t1, 20;
add $t1, $t1, $s0;
sw $t0, ($t1);
                




li $t0, 56;
            

li $t1, 24;
add $t1, $t1, $s0;
sw $t0, ($t1);
                




li $t0, 56;
            

li $t1, 28;
add $t1, $t1, $s0;
sw $t0, ($t1);
                




li $t0, 56;
            

li $t1, 32;
add $t1, $t1, $s0;
sw $t0, ($t1);
                




li $t0, 56;
            

li $t1, 36;
add $t1, $t1, $s0;
sw $t0, ($t1);
                




li $t0, 56;
            

li $t1, 40;
add $t1, $t1, $s0;
sw $t0, ($t1);
                




li $t0, 56;
            

li $t1, 44;
add $t1, $t1, $s0;
sw $t0, ($t1);
                




li $t0, 8;
add $t0, $t0, $s0
lw $t0, ($t0);
addi $t0, $t0, 16;
            

li $v0, 1;
lw $a0, ($t0);
syscall
                        

li $v0, 4;
la $a0, newline;
syscall
        

li $v0, 10;
syscall;
            