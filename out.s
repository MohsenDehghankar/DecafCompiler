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


li $t1, 8;
add $t1, $t1, $s0;
sw $v0, ($t1);



li $v0, 9;
li $a0, 4;
syscall


li $a0,'H';
sb $a0,0($v0);


li $a0,'e';
sb $a0,1($v0);


li $a0,'y';
sb $a0,2($v0);


lb $a0,end_of_string;
sb $a0,3($v0);


move $t1,$v0;


li $v0, 9;
li $a0, 4;
syscall


li $a0,'h';
sb $a0,0($v0);


li $a0,'e';
sb $a0,1($v0);


li $a0,'y';
sb $a0,2($v0);


lb $a0,end_of_string;
sb $a0,3($v0);


move $t0,$v0;


li $t2, 0
label1:
lb $t3, 0($t0)
lb $t4, 0($t1)
add $t0, $t0, 1
add $t1, $t1, 1
beqz $t3, label2
beqz $t4, label2
bne $t3, $t4, label3
beq $t3, $t4, label1
label3:
li $t2, 1
j label4
label5:
li $t2, 0
j label4
label2:
beq $t3, $t4, label5
label4:



move $t0, $t2;


li $t1, 12;
add $t1, $t1, $s0;
sb $t0, ($t1);




li $t0, 12;
add $t0, $t0, $s0;
lb $t0, ($t0);
li $v0, 4;
beq $t0, $zero, label6;
la $a0, true_const;
j label7;
label6:
la $a0, false_const;
label7:
syscall


li $v0, 4;
la $a0, newline;
syscall


li $v0, 10;
syscall;