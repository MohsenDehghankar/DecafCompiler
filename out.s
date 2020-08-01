
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
                



li.d $f0, 1.2;
li.d $f2, 2.3;
mul.d $f0, $f0, $f2
            


li $t0, 0;
lw $t0, frame_pointer($t0);
addi $t0, $t0, 24;
        


s.d $f0, ($t0);
                    



li $t1, 0;
lw $t1, frame_pointer($t1);
addi $t1, $t1, 24;
        

li $v0, 3;
l.d $f12, ($t1);
syscall
