.data
frame_pointer:  .space  1000
true_const:     .asciiz "true"
false_const:    .asciiz "false"
end_of_string:  .byte   0

.text
main:





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


li $t1, 0;
sw $v0, frame_pointer($t1);




li $v0, 4;
li $a0, 0;
lw $a0, frame_pointer($a0);
syscall