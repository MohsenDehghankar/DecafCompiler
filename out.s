

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
        









li $t0, 3;
                


li $t1, 4;
                

beq $t0, $t1, label1;
        
        


add $t0, $zero, $zero;
b label2;
label1:
addi $t0, $zero, 1;
label2:
        


move $t1, $t0;
                


move $t2, $t1;
                

li $t1, 8;
add $t1, $t1, $s0;
sw $t2, ($t1);
                




li $v0, 1;
li $a0, 8;
add $a0, $a0, $s0;
lw $a0, ($a0);
syscall
                    

li $v0, 4;
la $a0, newline;
syscall
        

li $v0, 10;
syscall;
            