

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
        















li $t0, 9;
                


li $t1, 10;
                

mult $t0, $t1;
mflo $t0;
            





li $t1, 200;
                


li $t2, 8;
                

mult $t1, $t2;
mflo $t1;
            


move $t2, $t0;
                


move $t3, $t1;
                

add $t2, $t2, $t3
        





li $t0, 1;
                


li $t1, 6;
                

add $t0, $t0, $t1
        


move $t1, $t2;
                


move $t3, $t0;
                

sub $t1, $t1, $t3
        





li $t0, 90;
                


li $t2, 2;
                

mult $t0, $t2;
mflo $t0;
            


move $t2, $t1;
                


move $t3, $t0;
                

add $t2, $t2, $t3
        





li $t0, 4;
                


li $t1, 2;
                

div $t0, $t1;
mflo $t0;
        


move $t1, $t2;
                


move $t3, $t0;
                

add $t1, $t1, $t3
        





li $t0, 76;
                


li $t2, 90;
                

add $t0, $t0, $t2
        


move $t2, $t1;
                


move $t3, $t0;
                

add $t2, $t2, $t3
        







li $t0, 12;
                


li $t1, 13;
                

add $t0, $t0, $t1
        



move $t1, $t0;
                


li $t3, 14;
                

add $t1, $t1, $t3
        



move $t0, $t1;
                


li $t3, 15;
                

add $t0, $t0, $t3
        


move $t1, $t2;
                


move $t3, $t0;
                

mult $t1, $t3;
mflo $t1;
            



move $t0, $t1;
                


li $t2, 1;
                

mult $t0, $t2;
mflo $t0;
            



move $t1, $t0;
                


li $t2, 1;
                

mult $t1, $t2;
mflo $t1;
            


move $t0, $t1;
                

li $t1, 8;
add $t1, $t1, $s0;
sw $t0, ($t1);
                




li $v0, 1;
li $a0, 8;
add $a0, $a0, $s0;
lw $a0, ($a0);
syscall
                    

li $v0, 4;
la $a0, newline;
syscall
        

li $v0, 10;
syscall;
            
