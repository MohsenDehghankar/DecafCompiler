

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
        



# create object for A
li $v0, 9;
li $a0, 8;
syscall
# move address to t1
move $t1, $v0;
        


move $t2, $t1;
                

li $t1, 8;
add $t1, $t1, $s0;
sw $t2, ($t1);
                


# get address of obj
li $t1, 8;
add $t1, $t1, $s0;
lw $t1, ($t1)

# now $t1 has the address of obj
li $t2, 0;
add $t1, $t1, $t2;

            


li.d $f0, 3.4;
                    

s.d $f0, ($t1);
                    



li $t2, 32;
                    

li $t3, -4;
add $t3, $t3, $t2;
            

lw $t4, 8($s0);
add $t3, $t3, $s0;
sw $t4, ($t3);
                    


li $t2, 32;
                    

li $t3, -16;
add $t3, $t3, $t2;
            

li.d $f0, 20.5;
add $t3, $t3, $s0;
s.d $f0, ($t3);
                    

li $t4, 32;
add $t4, $t4, $s0;
sw $s0, ($t4);
        

move $t4, $s0;
add $t4, $t4, 32
move $s0, $t4;
jal A.func;
        

move $t4, $v0;
        



# get address of obj
li $t2, 8;
add $t2, $t2, $s0;
lw $t2, ($t2)

# now $t2 has the address of obj
li $t3, 0;
add $t2, $t2, $t3;

            

li $v0, 2;
l.d $f12, ($t2);
cvt.s.d $f12, $f12
syscall
	                

li $v0, 4;
la $a0, newline;
syscall
        

li $v0, 10;
syscall;
            



A.func:

sw $ra, 4($s0);
        



# get address of obj
li $t0, -4;
add $t0, $t0, $s0;
lw $t0, ($t0)

# now $t0 has the address of obj
li $t1, 0;
add $t0, $t0, $t1;

            


li $t1, -16;
add $t1, $t1, $s0;
l.d $f0, ($t1)
                    

s.d $f0, ($t0);
                    
lw $ra, 4($s0);
lw $s0, ($s0)
jr $ra;
        