; sample demo of mem operation.

imme 0x1d
mov t0 t3
imme 0x10
sw

imme 0x0c
mov t0 t3
imme 0x11
sw

imme 0x10
lw
mov t3 io