

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
        




li $t0, 1;
            

li $t1, 8;
add $t1, $t1, $s1;
sb $t0, ($t1);
                



li $t0, 8;
add $t0, $t0, $s1;
lw $t0, ($t0);
beq $t0, $zero, label1;
            





    li $v0, 9;
    li $a0, 5;
    syscall
                                

    li $a0,'t';
    sb $a0,0($v0);
                                

    li $a0,'r';
    sb $a0,1($v0);
                                

    li $a0,'u';
    sb $a0,2($v0);
                                

    li $a0,'e';
    sb $a0,3($v0);
                                

    lb $a0,end_of_string;
    sb $a0,4($v0);
                                

    move $a0, $v0;
    li $v0, 4;
    syscall
                        

li $v0, 4;
la $a0, newline;
syscall
        

b label2;
label1:
        

label2:
        

li $v0, 10;
syscall;
            

