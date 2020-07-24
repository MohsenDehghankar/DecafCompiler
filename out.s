
.data
frame_pointer:  .space  1000
true_const:     .asciiz "true"
false_const:    .asciiz "false"

.text
main:
        




li $v0, 5;
syscall
move $t0, $v0;
        

li $v0, 1;
move $a0, $t0;
syscall
