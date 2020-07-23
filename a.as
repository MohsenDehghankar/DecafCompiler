.data
frame_pointer:  .space  1000
true_const:     .asciiz "true"
false_const:    .asciiz "false"

.text
main:







li $t0, 0;


li $t1, 0;
sw $t0, frame_pointer($t1);




li $t1, 0;
lw $t1, frame_pointer($t1);


li $t2, 1;


add $t1, $t1, $t2


move $t2, $t1;


li $t1, 0;
sw $t2, frame_pointer($t1);


label3:





li $t0, 0;
lw $t0, frame_pointer($t0);


li $t1, 10;



blt $t0, $t1, label1;




add $t0, $zero, $zero;
b label2;
label1:
addi $t0, $zero, 1;
label2:


beq $t0,$zero,label4;




li $t0, 0;


li $t1, 0;
sw $t0, frame_pointer($t1);




li $t1, 0;
lw $t1, frame_pointer($t1);


li $t2, 1;


add $t1, $t1, $t2


move $t2, $t1;


li $t1, 0;
sw $t2, frame_pointer($t1);


j label3;
label4:
