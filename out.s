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


li $t1, 4;
sw $v0, frame_pointer($t1);





li $t0, 0;
lw $t0, frame_pointer($t0);




li $t1, 4;
lw $t1, frame_pointer($t1);


li $t2, 0
label1:
lb $t3, 0($t1)
lb $t4, 0($t0)
add $t1, $t1, 1
add $t0, $t0, 1
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


li $t1, 8;
sb $t0, frame_pointer($t1);




li $t0, 8;
lb $t0, frame_pointer($t0);
li $v0, 4;
beq $t0, $zero, label6;
la $a0, true_const;
j label7;
label6:
la $a0, false_const;
label7:
syscall
