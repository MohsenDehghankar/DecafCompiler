

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
li $t0, 12
add $t0, $t0, $s0;
sw $v0, ($t0)
lw $t0, ($t0)
        



li $t1, 8;
add $t1, $t1, $s0;
sw $t0, ($t1);
                





li $t1, 8;
                

li $t0, 8;
add $t0, $t0, $s0
lw $t0, ($t0);
# calc index
addi $t1, $t1, 1
mul $t1, $t1, 4
mflo $t1;
add $t0, $t0, $t1;
            

li $t1, 9;
            

sw $t1, ($t0);
                    




li $t0, 5;
            

li $t1, 16;
add $t1, $t1, $s0;
sw $t0, ($t1);
                








li $t0, 16;
add $t0, $t0, $s0;
lw $t0, ($t0);
            


li $t1, 3;
                

add $t0, $t0, $t1
        


move $t2, $t0;
                

li $t1, 8;
add $t1, $t1, $s0
lw $t1, ($t1);
# calc index
addi $t2, $t2, 1
mul $t2, $t2, 4
mflo $t2;
add $t1, $t1, $t2;
            

li $v0, 1;
lw $a0, ($t1);
syscall
                        

li $v0, 4;
la $a0, newline;
syscall
        

li $v0, 10;
syscall;
            
