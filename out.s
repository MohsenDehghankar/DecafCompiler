
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
        






li.d $f0, 1.2;
                    

li $t0, 8;
add $t0, $t0, $s0;
s.d $f0, ($t0);
                



li $v0, 2;
li.d $f12, 1.234;
cvt.s.d $f12, $f12
syscall
                

li $v0, 4;
la $a0, newline;
syscall
        

li $v0, 10;
syscall;
