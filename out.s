
.data
frame_pointer:  .space  1000
true_const:     .asciiz "true"
false_const:    .asciiz "false"

.text
main:
        







li.d $f0, 2.2;
                    



li.d $f2, 2.2;
                    

c.eq.d $f0, $f2;
bc1f label1
            

add $t0, $zero, $zero;
b label2;
label1:
addi $t0, $zero, 1;
label2:
        

move $t1, $t0;
                

li $t0, 1;
sb $t1, frame_pointer($t0);
                



li $t0, 1;
lb $t0, frame_pointer($t0);
li $v0, 4;
beq $t0, $zero, label3;
la $a0, true_const;
j label4;
label3:
la $a0, false_const;
label4:
syscall
