
.data
frame_pointer:  .space  1000
true_const:     .asciiz "true"
false_const:    .asciiz "false"

.text
main:
        





li $t0, 2;
            

li $t1, 5;
sw $t0, frame_pointer($t1);
