

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
        



# create object for A
li $v0, 9;
li $a0, 12;
syscall
# move address to t1
move $t0, $v0;
        


move $t1, $t0;
                

li $t0, 8;
add $t0, $t0, $s0;
sw $t1, ($t0);
                


# get address of obj
li $t1, 8;
add $t1, $t1, $s0;
lw $t1, ($t1)

# now $t1 has the address of obj
li $t0, 8;
add $t1, $t1, $t0;

# now $t1 has address of field
lw $t0, ($t1);
# field moved to $t0
            

li $t1, 10;
            
li $t2, 8;
add $t2, $t2, $s0;
lw $t2, ($t2);
# now address of obj is in $t2
li $t0, 8;
add $t0, $t0, $t2;
# now $t0 has fld offset
sw $t1, ($t0);
                


# get address of obj
li $t2, 8;
add $t2, $t2, $s0;
lw $t2, ($t2)

# now $t2 has the address of obj
li $t1, 8;
add $t2, $t2, $t1;

# now $t2 has address of field
lw $t1, ($t2);
# field moved to $t1
            



move $t2, $t1;
                


li $t3, 2;
                

add $t2, $t2, $t3
        

# get address of obj
li $t1, 8;
add $t1, $t1, $s0;
lw $t1, ($t1)

# now $t1 has the address of obj
li $t0, 8;
add $t1, $t1, $t0;

# now $t1 has address of field
lw $t0, ($t1);
# field moved to $t0
            

move $t1, $t2;
                
li $t2, 8;
add $t2, $t2, $s0;
lw $t2, ($t2);
# now address of obj is in $t2
li $t0, 8;
add $t0, $t0, $t2;
# now $t0 has fld offset
sw $t1, ($t0);
                


# get address of obj
li $t1, 8;
add $t1, $t1, $s0;
lw $t1, ($t1)

# now $t1 has the address of obj
li $t0, 4;
add $t1, $t1, $t0;

# now $t1 has address of field
lw $t0, ($t1);
# field moved to $t0
            

li $t1, 90;
            
li $t2, 8;
add $t2, $t2, $s0;
lw $t2, ($t2);
# now address of obj is in $t2
li $t0, 4;
add $t0, $t0, $t2;
# now $t0 has fld offset
sw $t1, ($t0);
                


# get address of obj
li $t2, 8;
add $t2, $t2, $s0;
lw $t2, ($t2)

# now $t2 has the address of obj
li $t1, 4;
add $t2, $t2, $t1;

# now $t2 has address of field
lw $t1, ($t2);
# field moved to $t1
            

# get address of obj
li $t3, 8;
add $t3, $t3, $s0;
lw $t3, ($t3)

# now $t3 has the address of obj
li $t2, 8;
add $t3, $t3, $t2;

# now $t3 has address of field
lw $t2, ($t3);
# field moved to $t2
            


move $t3, $t1;
                


move $t4, $t2;
                

mult $t3, $t4;
mflo $t3;
            

# get address of obj
li $t1, 8;
add $t1, $t1, $s0;
lw $t1, ($t1)

# now $t1 has the address of obj
li $t0, 0;
add $t1, $t1, $t0;

# now $t1 has address of field
lw $t0, ($t1);
# field moved to $t0
            

move $t1, $t3;
                
li $t2, 8;
add $t2, $t2, $s0;
lw $t2, ($t2);
# now address of obj is in $t2
li $t0, 0;
add $t0, $t0, $t2;
# now $t0 has fld offset
sw $t1, ($t0);
                



# get address of obj
li $t1, 8;
add $t1, $t1, $s0;
lw $t1, ($t1)

# now $t1 has the address of obj
li $t0, 0;
add $t1, $t1, $t0;

# now $t1 has address of field
lw $t0, ($t1);
# field moved to $t0
            

li $v0, 1;
move $a0, $t0;
syscall
                        

li $v0, 4;
la $a0, newline;
syscall
        


# create object for B
li $v0, 9;
li $a0, 8;
syscall
# move address to t1
move $t0, $v0;
        


move $t1, $t0;
                

li $t0, 12;
add $t0, $t0, $s0;
sw $t1, ($t0);
                


# get address of obj
li $t1, 12;
add $t1, $t1, $s0;
lw $t1, ($t1)

# now $t1 has the address of obj
li $t0, 0;
add $t1, $t1, $t0;

# now $t1 has address of field
lw $t0, ($t1);
# field moved to $t0
            

li $t1, 100;
            
li $t2, 12;
add $t2, $t2, $s0;
lw $t2, ($t2);
# now address of obj is in $t2
li $t0, 0;
add $t0, $t0, $t2;
# now $t0 has fld offset
sw $t1, ($t0);
                


# get address of obj
li $t2, 12;
add $t2, $t2, $s0;
lw $t2, ($t2)

# now $t2 has the address of obj
li $t1, 0;
add $t2, $t2, $t1;

# now $t2 has address of field
lw $t1, ($t2);
# field moved to $t1
            

# get address of obj
li $t3, 8;
add $t3, $t3, $s0;
lw $t3, ($t3)

# now $t3 has the address of obj
li $t2, 0;
add $t3, $t3, $t2;

# now $t3 has address of field
lw $t2, ($t3);
# field moved to $t2
            


move $t3, $t1;
                


move $t4, $t2;
                

add $t3, $t3, $t4
        

# get address of obj
li $t1, 12;
add $t1, $t1, $s0;
lw $t1, ($t1)

# now $t1 has the address of obj
li $t0, 4;
add $t1, $t1, $t0;

# now $t1 has address of field
lw $t0, ($t1);
# field moved to $t0
            

move $t1, $t3;
                
li $t2, 12;
add $t2, $t2, $s0;
lw $t2, ($t2);
# now address of obj is in $t2
li $t0, 4;
add $t0, $t0, $t2;
# now $t0 has fld offset
sw $t1, ($t0);
                



# get address of obj
li $t1, 12;
add $t1, $t1, $s0;
lw $t1, ($t1)

# now $t1 has the address of obj
li $t0, 4;
add $t1, $t1, $t0;

# now $t1 has address of field
lw $t0, ($t1);
# field moved to $t0
            

li $v0, 1;
move $a0, $t0;
syscall
                        

li $v0, 4;
la $a0, newline;
syscall
        

li $v0, 10;
syscall;
            


