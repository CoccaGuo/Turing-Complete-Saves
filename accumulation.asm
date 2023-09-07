; File: accumulation.asm
; Author: CoccaGuo

; Test prog for adding 1 to 20.
; The result should be (1+20)*20/2 = 210

; C representation:

; uint8_t sum = 0;
; uint8_t i = 1;

; do {
;     sum += i;
;     i++;
; } while (i<21);

imme 0
; sum in s0
mov t0 s0

imme 1
; i in s1
mov t0 s1

label while
mov s0 t1
mov s1 t2
add
mov t3 s0

imme 1
mov t0 t1
mov s1 t2
add
mov t3 s1

mov s1 t1
imme 21
mov t0 t2
sub
while
lt0

mov s0 io
label __final
__final
jmp
