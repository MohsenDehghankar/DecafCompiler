

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
            

li $t1, 12;
add $t1, $t1, $s0;
sw $t0, ($t1);
                





li $t0, 1;
            

li $t1, 16;
add $t1, $t1, $s0;
sw $t0, ($t1);
                

label6:
                    


li $t1, 1;
beq $t1,$zero,label7;
                                            





    li $v0, 9;
    li $a0, 19;
    syscall
                                

    li $a0,'P';
    sb $a0,0($v0);
                                

    li $a0,'l';
    sb $a0,1($v0);
                                

    li $a0,'e';
    sb $a0,2($v0);
                                

    li $a0,'a';
    sb $a0,3($v0);
                                

    li $a0,'s';
    sb $a0,4($v0);
                                

    li $a0,'e';
    sb $a0,5($v0);
                                

    li $a0,' ';
    sb $a0,6($v0);
                                

    li $a0,'e';
    sb $a0,7($v0);
                                

    li $a0,'n';
    sb $a0,8($v0);
                                

    li $a0,'t';
    sb $a0,9($v0);
                                

    li $a0,'e';
    sb $a0,10($v0);
                                

    li $a0,'r';
    sb $a0,11($v0);
                                

    li $a0,' ';
    sb $a0,12($v0);
                                

    li $a0,'t';
    sb $a0,13($v0);
                                

    li $a0,'h';
    sb $a0,14($v0);
                                

    li $a0,'e';
    sb $a0,15($v0);
                                

    li $a0,' ';
    sb $a0,16($v0);
                                

    li $a0,'#';
    sb $a0,17($v0);
                                

    lb $a0,end_of_string;
    sb $a0,18($v0);
                                

    move $a0, $v0;
    li $v0, 4;
    syscall
                        


li $v0, 1;
li $a0, 16;
add $a0, $a0, $s0;
lw $a0, ($a0);
syscall
                    


    li $v0, 9;
    li $a0, 9;
    syscall
                                

    li $a0,' ';
    sb $a0,0($v0);
                                

    li $a0,'n';
    sb $a0,1($v0);
                                

    li $a0,'u';
    sb $a0,2($v0);
                                

    li $a0,'m';
    sb $a0,3($v0);
                                

    li $a0,'b';
    sb $a0,4($v0);
                                

    li $a0,'e';
    sb $a0,5($v0);
                                

    li $a0,'r';
    sb $a0,6($v0);
                                

    li $a0,':';
    sb $a0,7($v0);
                                

    lb $a0,end_of_string;
    sb $a0,8($v0);
                                

    move $a0, $v0;
    li $v0, 4;
    syscall
                        

li $v0, 4;
la $a0, newline;
syscall
        


li $v0, 5;
syscall
move $t0, $v0;
        


move $t1, $t0;
                

li $t0, 8;
add $t0, $t0, $s0;
sw $t1, ($t0);
                








li $t0, 8;
add $t0, $t0, $s0;
lw $t0, ($t0);
            


li $t1, 0;
                

blt $t0, $t1, label1;
        
        


add $t0, $zero, $zero;
b label2;
label1:
addi $t0, $zero, 1;
label2:
        

beq $t0, $zero, label4;
            

j label3;
        

b label5;
label4:
        

label5:
        





li $t1, 12;
add $t1, $t1, $s0;
lw $t1, ($t1);
            


li $t2, 8;
add $t2, $t2, $s0;
lw $t2, ($t2);
            

add $t1, $t1, $t2
        


move $t2, $t1;
                

li $t1, 12;
add $t1, $t1, $s0;
sw $t2, ($t1);
                





li $t0, 16;
add $t0, $t0, $s0;
lw $t0, ($t0);
            


li $t1, 1;
                

add $t0, $t0, $t1
        


move $t1, $t0;
                

li $t0, 16;
add $t0, $t0, $s0;
sw $t1, ($t0);
                

j label6;
label7:
                    

label3:
            




    li $v0, 9;
    li $a0, 8;
    syscall
                                

    li $a0,'S';
    sb $a0,0($v0);
                                

    li $a0,'u';
    sb $a0,1($v0);
                                

    li $a0,'m';
    sb $a0,2($v0);
                                

    li $a0,' ';
    sb $a0,3($v0);
                                

    li $a0,'o';
    sb $a0,4($v0);
                                

    li $a0,'f';
    sb $a0,5($v0);
                                

    li $a0,' ';
    sb $a0,6($v0);
                                

    lb $a0,end_of_string;
    sb $a0,7($v0);
                                

    move $a0, $v0;
    li $v0, 4;
    syscall
                        


li $v0, 1;
li $a0, 16;
add $a0, $a0, $s0;
lw $a0, ($a0);
syscall
                    


    li $v0, 9;
    li $a0, 12;
    syscall
                                

    li $a0,' ';
    sb $a0,0($v0);
                                

    li $a0,'i';
    sb $a0,1($v0);
                                

    li $a0,'t';
    sb $a0,2($v0);
                                

    li $a0,'e';
    sb $a0,3($v0);
                                

    li $a0,'m';
    sb $a0,4($v0);
                                

    li $a0,'s';
    sb $a0,5($v0);
                                

    li $a0,' ';
    sb $a0,6($v0);
                                

    li $a0,'i';
    sb $a0,7($v0);
                                

    li $a0,'s';
    sb $a0,8($v0);
                                

    li $a0,':';
    sb $a0,9($v0);
                                

    li $a0,' ';
    sb $a0,10($v0);
                                

    lb $a0,end_of_string;
    sb $a0,11($v0);
                                

    move $a0, $v0;
    li $v0, 4;
    syscall
                        


li $v0, 1;
li $a0, 12;
add $a0, $a0, $s0;
lw $a0, ($a0);
syscall
                    

li $v0, 4;
la $a0, newline;
syscall
        

li $v0, 10;
syscall;
            
