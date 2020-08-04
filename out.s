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






li $v0, 9;
li $a0, 6;
syscall


li $a0,'s';
sb $a0,0($v0);


li $a0,'a';
sb $a0,1($v0);


li $a0,'l';
sb $a0,2($v0);


li $a0,'a';
sb $a0,3($v0);


li $a0,'m';
sb $a0,4($v0);


lb $a0,end_of_string;
sb $a0,5($v0);


li $t1, 12;
add $t1, $t1, $s0;
sw $v0, ($t1);




li $v0, 4;
li $a0, 12;
add $a0, $a0, $s0;
lw $a0, ($a0);
syscall


li $v0, 4;
la $a0, newline;
syscall


li $v0, 10;
syscall;
