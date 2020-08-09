

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
        







li.d $f0, -1.2;
                    

li.d $f2, 0.0
c.le.d $f0, $f2
round.w.d $f0, $f0
mfc1  $t0,$f0
bc1f label1 
sub $t0, $t0, 1
label1:
        


move $t1, $t0;
                

li $t0, 8;
add $t0, $t0, $s0;
sw $t1, ($t0);
                




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
            
