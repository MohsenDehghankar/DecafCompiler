

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
        





li $t0, 10;
            

li $t1, 8;
add $t1, $t1, $s0;
sw $t0, ($t1);
                







li $t0, 8;
add $t0, $t0, $s0;
lw $t0, ($t0);
            


li $t1, 90;
                

mult $t0, $t1;
mflo $t0;
            



move $t1, $t0;
                


li $t2, 50;
                

add $t1, $t1, $t2
        


move $t0, $t1;
                

li $t1, 12;
add $t1, $t1, $s0;
sw $t0, ($t1);
                



li $t0, 24;
                    

li $t1, -4;
add $t1, $t1, $t0;
            

lw $t2, 12($s0);
add $t1, $t1, $s0;
sw $t2, ($t1);
                    

li $t2, 24;
add $t2, $t2, $s0;
sw $s0, ($t2);
        

move $t2, $s0;
add $t2, $t2, 24
move $s0, $t2;
jal func;
        

move $t2, $v0;
        

li $v0, 10;
syscall;
            

func:

sw $ra, 4($s0);
        





li $v0, 1;
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
        
