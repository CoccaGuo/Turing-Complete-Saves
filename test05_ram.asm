imme 1
mov t0 t1
mov t0 t2
add
; t3 = 2

imme 30 
; addr = 30
sw

mov t3 t1
mov t3 t2
add
; t3 = 4

imme 31
sw

mov t3 t1
mov t3 t2
add
; t3 = 8

imme 32
sw

; load data

imme 31
; addr = 31
lw
; t3 = 4

mov t3 io
; should be 4
