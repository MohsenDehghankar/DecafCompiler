
.data
frame_pointer:  .space  1000
true_const:     .asciiz "true"
false_const:    .asciiz "false"

.text
main:
        






li.d $f0, 2.3;
li.d $f2, 1.2;
mul.d $f0, $f0, $f2 
            


li $t0, 8;
s.d $f0, frame_pointer($t0);
                



li $v0, 3;
li $t0, 8;
l.d $f12, frame_pointer($t0);
syscall
