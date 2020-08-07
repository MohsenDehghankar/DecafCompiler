

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
        





li $v0, 5;
syscall
move $t0, $v0;
        


move $t1, $t0;
                

li $t0, 8;
add $t0, $t0, $s0;
sw $t1, ($t0);
                


li $v0, 5;
syscall
move $t0, $v0;
        


move $t1, $t0;
                

li $t0, 12;
add $t0, $t0, $s0;
sw $t1, ($t0);
                




li $t0, 24;
        


li $t1, -4;
add $t1, $t1, $t0;
            

lw $t2, 8($s0);
add $t1, $t1, $s0;
sw $t2, ($t1);
                    


li $t1, -8;
add $t1, $t1, $t0;
            

lw $t2, 12($s0);
add $t1, $t1, $s0;
sw $t2, ($t1);
                    

li $t2, 24;
add $t2, $t2, $s0;
sw $s0, ($t2);
        

move $t2, $s0;
add $t2, $t2, 24
move $s0, $t2;
jal abs_mult;
        

move $t2, $v0;
        

li $v0, 1;
move $a0, $t2;
syscall
                        

li $v0, 4;
la $a0, newline;
syscall
        

li $v0, 10;
syscall;
            

abs_mult:

sw $ra, 4($s0);
        









li $t0, -4;
add $t0, $t0, $s0;
lw $t0, ($t0);
            

li $t1, -8;
add $t1, $t1, $s0;
lw $t1, ($t1);
            

bgt $t0, $t1, label1;
        
        


add $t0, $zero, $zero;
b label2;
label1:
addi $t0, $zero, 1;
label2:
        

beq $t0, $zero, label3;
        





li $t1, -4;
add $t1, $t1, $s0;
lw $t1, ($t1);
                    


li $t2, -8;
add $t2, $t2, $s0;
lw $t2, ($t2);
                    

sub $t1, $t1, $t2
        


move $t2, $t1;
                

li $t1, 8;
add $t1, $t1, $s0;
sw $t2, ($t1);
                

b label4;
label3:
        





li $t1, -8;
add $t1, $t1, $s0;
lw $t1, ($t1);
                    


li $t2, -4;
add $t2, $t2, $s0;
lw $t2, ($t2);
                    

sub $t1, $t1, $t2
        


move $t2, $t1;
                

li $t1, 8;
add $t1, $t1, $s0;
sw $t2, ($t1);
                

label4:
        






li $t1, 8;
add $t1, $t1, $s0;
lw $t1, ($t1);
                    


li $t2, -4;
add $t2, $t2, $s0;
lw $t2, ($t2);
                    

mult $t1, $t2;
mflo $t1;
            



move $t2, $t1;
                


li $t3, -8;
add $t3, $t3, $s0;
lw $t3, ($t3);
                    

mult $t2, $t3;
mflo $t2;
            
lw $ra, 4($s0);
move $v0, $t2;
lw $s0, ($s0);
jr $ra;
                