; Demo script for shift left logical.

imme 3
mov t0 t1

imme 4
mov t0 t2

; start of pseudo cmd sll

label __asm_sll_start
mov t2 t3
__asm_sll_pass
; if shift times is zero, pass
lteq0
mov t2 t0
mov t1 t2
add
mov t0 t1
imme 1
mov t0 t2
mov t3 t0
sub
mov t0 t1
mov t3 t2
__asm_sll_start
gt0
label __asm_sll_pass
mov t1 t3

; end of sll

mov t3 io