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








li $t0, 0;


li $t1, 8;
add $t1, $t1, $s0;
sw $t0, ($t1);


    label3:




li $t0, 8;
add $t0, $t0, $s0;
lw $t0, ($t0);


li $t1, 10;



blt $t0, $t1, label1;




add $t0, $zero, $zero;
b label2;
label1:
addi $t0, $zero, 1;
label2:


    beq $t0,$zero,label4;





li $v0, 9;
li $a0, 5;
syscall


li $a0,'a';
sb $a0,0($v0);


li $a0,'h';
sb $a0,1($v0);


li $a0,'a';
sb $a0,2($v0);


li $a0,'n';
sb $a0,3($v0);


lb $a0,end_of_string;
sb $a0,4($v0);


move $a0, $v0;
li $v0, 4;
syscall


li $v0, 4;
la $a0, newline;
syscall





li $t1, 8;
add $t1, $t1, $s0;
lw $t1, ($t1);


li $t2, 1;


add $t1, $t1, $t2



move $t2, $t1;


li $t1, 8;
add $t1, $t1, $s0;
sw $t2, ($t1);


    j label3;
    label4:


li $v0, 10;
syscall;