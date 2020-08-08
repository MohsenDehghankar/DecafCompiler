

.data
frame_pointer:  .space  10000
global_pointer: .space  10000
input:          .space  16384
true_const:     .asciiz "true"
false_const:    .asciiz "false"
end_of_string:  .byte   0
newline:        .asciiz "\n"

.text
main:
la $s0, frame_pointer;
la $s1, global_pointer;
        






li $v0, 9;
li $a0, 3;
syscall
        

li $a0,',';
sb $a0,0($v0);
                            

li $a0,' ';
sb $a0,1($v0);
                            

lb $a0,end_of_string;
sb $a0,2($v0);
                            

move $t0, $v0;
        

li $t1, 12;
add $t1, $t1, $s0;
sw $v0, ($t1);
                    





li $t0, 0;
            

li $t1, 8;
add $t1, $t1, $s0;
sw $t0, ($t1);
                

label8:
                    






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
        

beq $t0,$zero,label9;
                                





li $v0, 1;
li $a0, 8;
add $a0, $a0, $s0;
lw $a0, ($a0);
syscall
                    

li $v0, 4;
la $a0, newline;
syscall
        








li $t1, 8;
add $t1, $t1, $s0;
lw $t1, ($t1);
            


li $t2, 5;
                

beq $t1, $t2, label3;
        
        


add $t1, $zero, $zero;
b label4;
label3:
addi $t1, $zero, 1;
label4:
        

beq $t1, $zero, label6;
        

j label5;
        

b label7;
label6:
        

label7:
        





li $t1, 8;
add $t1, $t1, $s0;
lw $t1, ($t1);
            


li $t2, 1;
                

add $t1, $t1, $t2
        


move $t2, $t1;
                

li $t1, 8;
add $t1, $t1, $s0;
sw $t2, ($t1);
                

j label8;
label9:
                    

label5:
            

li $v0, 10;
syscall;
            
