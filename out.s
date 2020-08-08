

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
        



li $t1, 16;
        


la $a0, input
li $v0, 8
li $a1, 16384
syscall
addi $t1, $t1, 0
label1:
lb $t2, ($a0)
lb $t3, newline
beq $t2, $t3, label2
addi $a0, $a0, 1
b label1   
label2:
sb $zero, ($a0)
la $a0, input
move $t0,$a0
        

li $t2, -4;
add $t2, $t2, $t1;
            

move $t3, $t0;
add $t2, $t2, $s0;
sw $t3, ($t2);
                    

li $t3, 16;
add $t3, $t3, $s0;
sw $s0, ($t3);
        

move $t3, $s0;
add $t3, $t3, 16
move $s0, $t3;
jal fun;
        

move $t3, $v0;
        

li $v0, 10;
syscall;
            

fun:

sw $ra, 4($s0);
        





li $v0, 4;
li $a0, -4;
add $a0, $a0, $s0;
lw $a0, ($a0);
syscall
                    

li $v0, 4;
la $a0, newline;
syscall
        
lw $ra, 4($s0);
lw $s0, ($s0)
jr $ra;
        
