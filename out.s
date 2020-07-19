
.data
frame_pointer:  .space  1000

.text
main:
        

li $t0, 3;
            

li $t1, 3;
            

beq $t0, $t1, label1;
        

add $t0, $zero, $zero;
b label2;
label1:
addi $t0, $zero, 1;
label2:
        

li $t1, 4;
            

li $t2, 3;
            

bne $t1, $t2, label3;
        

add $t1, $zero, $zero;
b label4;
label3:
addi $t1, $zero, 1;
label4:
        

or $t0, $t0, $t1;
        

ble $t0, $zero, label5;
        

b label6 ;
label5:
        

label6:
