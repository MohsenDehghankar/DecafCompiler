

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
        




li $a0, 52;
li $v0, 9;
syscall
li $t0 , 12;
sw $t0, 0($v0);
li $t0, 12
add $t0, $t0, $s0;
sw $v0, ($t0)
        


li $t0, 12;
add $t0, $t0, $s0;
lw $t0, ($t0);
            

li $t1, 8;
add $t1, $t1, $s0;
sw $t0, ($t1);
                



li $t0, 8;
add $t0, $t0, $s0
lw $t0, ($t0);
addi $t0, $t0, 16;
            


li.d $f0, 2.33456;
                    

s.d $f0, ($t0);
                    








li.d $f0, 14.4567;
                    



li $t2, 8;
add $t2, $t2, $s0
lw $t2, ($t2);
addi $t2, $t2, 16;
            

l.d $f2, ($t2);
            

mul.d $f0, $f0, $f2
            



li $t3, 8;
add $t3, $t3, $s0
lw $t3, ($t3);
addi $t3, $t3, 24;
            

l.d $f6, ($t3);
            

add.d $f0, $f0, $f6
            



li $t4, 8;
add $t4, $t4, $s0
lw $t4, ($t4);
addi $t4, $t4, 16;
            

l.d $f10, ($t4);
            

add.d $f0, $f0, $f10
            


li $t1, 8;
add $t1, $t1, $s0
lw $t1, ($t1);
addi $t1, $t1, 24;
            


s.d $f0, ($t1);
                    




li $t5, 8;
add $t5, $t5, $s0
lw $t5, ($t5);
addi $t5, $t5, 24;
            

li $v0, 2;
l.d $f12, ($t5);
cvt.s.d $f12, $f12
syscall
                        

li $v0, 4;
la $a0, newline;
syscall
        

li $v0, 10;
syscall;
