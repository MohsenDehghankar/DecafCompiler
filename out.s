

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
        





li $t0, 5;
            

li $t1, 8;
add $t1, $t1, $s0;
sw $t0, ($t1);
                






li $t0, 16;
        


li $t1, -4;
add $t1, $t1, $t0;
            

lw $t2, 8($s0);
add $t1, $t1, $s0;
sw $t2, ($t1);
                    

li $t2, 16;
add $t2, $t2, $s0;
sw $s0, ($t2);
        

move $t2, $s0;
add $t2, $t2, 16
move $s0, $t2;
jal fnc;
        

move $t2, $v0;
        



li.d $f2, 2.5;
                    

add.d $f2, $f2, $f2
            

li $v0, 2;
mov.d $f12, $f2;
cvt.s.d $f12, $f12
syscall
                    

li $v0, 4;
la $a0, newline;
syscall
        

li $v0, 10;
syscall;
            

fnc:

sw $ra, 4($s0);
        


lw $ra, 4($s0);
l.d $f0, None($s0);
lw $s0, ($s0)
jr $ra;
                        
