
.data
frame_pointer:  .space  1000
true_const:     .asciiz "true"
false_const:    .asciiz "false"

.text
main:
        




li $a0, 44;
li $v0, 9;
syscall
li $t0 , 10;
sw $t0, 0($v0);
li $t0, 4
sw $v0, frame_pointer($t0)
        


li $t0, 4;
lw $t0, frame_pointer($t0);
            

li $t1, 0;
sw $t0, frame_pointer($t1);
                


li $a0, 44;
li $v0, 9;
syscall
li $t1 , 10;
sw $t1, 0($v0);
li $t1, 8
sw $v0, frame_pointer($t1)
        


li $t0, 0;
lw $t0, frame_pointer($t0);
addi $t0, $t0, 4;
            

li $t1, 8;
lw $t1, frame_pointer($t1);
            


sw $t1, ($t0);
                




li $t0, 0;
lw $t0, frame_pointer($t0);
addi $t0, $t0, 4;
            

lw $t1, ($t0);
addi $t1, $t1, 8;
            

li $t2, 3;
            

sw $t2, ($t1);
                

sw $t2, ($t1);
                




li $t1, 0;
lw $t1, frame_pointer($t1);
addi $t1, $t1, 4;
            

lw $t2, ($t1);
addi $t2, $t2, 12;
            

li $v0, 1;
lw $a0, ($t2);
syscall
 