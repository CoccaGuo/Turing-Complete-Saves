; memory.asm
; author: CoccaGuo
; Date: 2023-07-18
; Save data from 5 to 0 and print them.

; mem-addr: 1   2   3   ... n       ... 61
; data:     60  59  58  ... 61-n    ... 0

; value to save
imme 60
mov t0 s0

; memory pointer
imme 0
mov t0 sp

label _in_mem_loop
; now data in s0, ptr in sp

; sp++
imme 1
mov t0 t2
mov sp t1
add
mov t3 sp

; store word
mov sp t0
mov s0 t3
sw

; data--
mov s0 t1
imme 1
mov t0 t2
sub
mov t3 s0

; if data >= 0 loop
_in_mem_loop
gteq0

; demo print below

imme 40
lw
mov t3 io 
; should be 21=0x15
