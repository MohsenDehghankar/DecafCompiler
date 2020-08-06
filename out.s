

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
        





li $t0, 4;
            

li $t1, 8;
add $t1, $t1, $s0;
sw $t0, ($t1);
                




li $t0, 7;
            

li $t1, 12;
add $t1, $t1, $s0;
sw $t0, ($t1);
                





li $t0, 8;
add $t0, $t0, $s0;
lw $t0, ($t0);
            

li $t1, 12;
add $t1, $t1, $s0;
lw $t1, ($t1);
            



bgt $t0, $t1, label1;
        
        


add $t0, $zero, $zero;
b label2;
label1:
addi $t0, $zero, 1;
label2:
        


beq $t0, $zero, label3;
move $t0, $zero;
j label4;
label3:
li $t0, 1;
label4:
                

beq $t0, $zero, label5;
la $a0, true_const;
j label6;
label5:
la $a0, false_const;
label6:
li $v0, 4;
syscall
                    

li $v0, 4;
la $a0, newline;
syscall
        

li $v0, 10;
syscall;
  