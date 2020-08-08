

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
        






li.d $f0, 2.55;
                    

li $t0, 8;
add $t0, $t0, $s0;
s.d $f0, ($t0);
                







li $t1, 8;
add $t1, $t1, $s0;
l.d $f0, ($t1)
                    

li $v0, 9;
li $a0, 8;
syscall
round.w.d $f0, $f0;
mfc1 $t0, $f0;
        

li $v0, 1;
move $a0, $t0;
syscall
                        

li $v0, 4;
la $a0, newline;
syscall
        

li $v0, 10;
syscall;
            
