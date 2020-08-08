

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
        





li $t0, 1;
            

li $t1, 8;
add $t1, $t1, $s0;
sb $t0, ($t1);
                





li $t0, 8;
add $t0, $t0, $s0;
lb $t0, ($t0);
            


move $t1, $t0;
                

li $t0, 12;
add $t0, $t0, $s0;
sw $t1, ($t0);
                







li $t0, 12;
add $t0, $t0, $s0;
lw $t0, ($t0);
            


li $t1, 1;
                

add $t0, $t0, $t1
        

li $v0, 1;
move $a0, $t0;
syscall
                        

li $v0, 4;
la $a0, newline;
syscall
        

li $v0, 10;
syscall;
            

