
.data
frame_pointer:  .space  1000

.text
main:
li.d $f10, 3.534;
mov.d $f12, $f10;
li $v0, 3;
syscall    

