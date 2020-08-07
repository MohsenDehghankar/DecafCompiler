

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
        





li $t0, 5;
            

li $t1, 8;
add $t1, $t1, $s0;
sw $t0, ($t1);
                







li $t0, 8;
add $t0, $t0, $s0;
lw $t0, ($t0);
                    


li $t1, 5;
                

div $t0, $t1;
mfhi $t0;
            




move $t1, $t0;
            

li $t2, 0;
            

beq $t1, $t2, label1;
        
        


add $t1, $zero, $zero;
b label2;
label1:
addi $t1, $zero, 1;
label2:
        

beq $t1, $zero, label3;
        





    li $v0, 9;
    li $a0, 4;
    syscall
                                

    li $a0,'Y';
    sb $a0,0($v0);
                                

    li $a0,'e';
    sb $a0,1($v0);
                                

    li $a0,'s';
    sb $a0,2($v0);
                                

    lb $a0,end_of_string;
    sb $a0,3($v0);
                                

    move $a0, $v0;
    li $v0, 4;
    syscall
                        

li $v0, 4;
la $a0, newline;
syscall
        

b label4;
label3:
        





    li $v0, 9;
    li $a0, 3;
    syscall
                                

    li $a0,'N';
    sb $a0,0($v0);
                                

    li $a0,'o';
    sb $a0,1($v0);
                                

    lb $a0,end_of_string;
    sb $a0,2($v0);
                                

    move $a0, $v0;
    li $v0, 4;
    syscall
                        

li $v0, 4;
la $a0, newline;
syscall
        

label4:
        

li $v0, 10;
syscall;
            