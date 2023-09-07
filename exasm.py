'''
The Overture CPU assembler with extended pseudo instructions.
These commands may overwrite the temp regs t0~t3.

! IMPORTANT:  READ the docs in the func before using! Some regs will be overwritten !!

Author: CoccaGuo
Date: 2023/07/17

Registers:
t0~t3 temp regs,
s0~s1 saved regs,
sp stack ptr,
io gpio.

Extended Instructions:

    - XOR 
    - NOT

    - SLL
   
    ! Choose one as global config below:
        Use 1 byte stack pointer (only 256 bytes stack) or 2 bytes stack pointer
    
    - PUSH (only in addr 0x0000~0x00ff)
    - POP  (only in addr 0x0000~0x00ff)

    - PUSH_L ( Will take s1 as sp0, sp as sp1)
    - POP_L  ( Will take s1 as sp0, sp as sp1)


    ! IMPORTANT Use imme, label will also override temp regs!!
        - IMME number (0~255)
        - LABEL name (0x0000~0xffff)

 Use `;` for comments.
'''

import uuid

BASIC_CMDS = [
    'OR',
    'NAND', 
    'NOR', 
    'AND',
    'ADD',
    'SUB',
    'EQ0',
    'LT0',
    'LTEQ0',
    'JMP',
    'NEQ0',
    'GTEQ0',
    'GT0',
    'SW',
    'LW',
    'IMME',
    'MOV',
]

label_dicts = dict()

def _xor():
    return [
        '; __begin_xor__',
        'nand',
        'mov t3 t0',
        'or',
        'mov t3 t1',
        'mov t0 t2',
        'and',
        '; __end_xor__',
        '\n',
    ]


def _not():
    return [
        '; __begin_not__',
        'imme 0',
        'mov t0 t2',
        'nor',
        '; __end_not__',
        '\n',
    ]


def _sll():
    '''
    Shift left logical the data in reg1 only ONCE.
    '''
    return [
        '; __begin_sll__',
        'mov t1 t2',
        'add',
        '; __end_sll__',
        '\n',
    ]

# push and pop only works in addr 0x0000~0x00ff

def _push():
    return [
        '; __begin_push__',
        'mov sp t1',
        'imme 1',
        'mov t0 t2',
        'mov t3 t0',
        'add',
        'mov t3 sp',
        'mov t0 t3',
        'mov sp t0',
        'sw',
        '; __end_push__',
        '\n',
    ]


def _pop():
    return [
        '; __begin_pop__',
        'mov sp t1',
        'imme 1',
        'mov t0 t2',
        'sub',
        'mov t3 sp',
        'mov t1 t0',
        'lw',
        '; __end_pop__',
        '\n',
    ]

'''
PUSH_L & POP_L usage:

 - When writing asm manually, you should not use these two commands.
   These two commands will overwrite s1, sp and all temp regs.

 - In C compiler, the starting point of the stack pointer is set to
   0x0100 by default, the first 0xff bytes data is reserved for compiler.
   The push_l/pop_l commands use the first 0xff area to save temp data.

'''

def _push_l():
    '''
    0x00-0xff: RAM USAGE
    0x00    data to store,
    0x01    ptr.l (sp) + 1
    
    '''

    __pass = '__exasm_push_l_pass__' + uuid.uuid4()

    return [
        '; __begin_push_l__',
        'imme 0x00',
        'sw', # save the data to push into 0x0 as a cache.
        'mov sp t1',
        'imme 1',
        'mov t0 t2',
        'add',
        'imme 0x01',
        'sw',  # save the sp++ into 0x1.
        __pass,
        'mov t0 sp',
        'imme 0x01',
        'lw',
        'mov sp t0',
        'neq0',
        'mov s1 t1',
        'imme 1',
        'mov t0 t2',
        'add',
        'mov t3 s1',
        'imme 0x01',
        'lw',
        'label ' + __pass,
        'mov t3 t1',
        'mov t3 sp',
        'mov s1 t2',
        'imme 0x00',
        'lw',
        'imme 0',
        'sw',
        '; __end_push_l__',
        '\n',
    ]
    


def _pop_l():
    '''
    0x00-0xff: RAM USAGE
    0x02    data to pop
    
    '''
    __pass = '__exasm_pop_l_pass__' + uuid.uuid4()

    return [
        '; __begin_pop_l__',
        'mov sp t1',
        'mov s1 t2',
        'imme 0',
        'lw',
        'imme 0x02',
        'sw',
        __pass,
        'mov sp t3',
        'neq0',
        'imme 1',
        'mov t0 t2',
        'mov s1 t1',
        'sub',
        'mov t3 s1',
        'label ' + __pass,
        'imme 1',
        'mov t0 t2',
        'mov sp t1',
        'sub',
        'mov t3 sp',
        'imme 0x02',
        'lw',
        '; __end_pop_l__',
        '\n',
    ]




def _imme(number):
    '''
    This function writes immediate number from 0~255 into reg0.
    However, this function will overwrite the reg1 and reg2.
    Note that this function is design to preserve reg3.
    '''
    if number < 0 or number > 255:
        return None
    if number < 64: # 1 line
        return [f'imme {number}']
    elif number < 127: # design to preserve t3 reg.
        return [       # 9 lines
            f'; __begin_imme_{number}__',
            'imme 63',
            'mov t0 t1',
            f'imme {number-63}',
            'mov t0 t2',
            'mov t3 t0',
            'add',
            'mov t0 t1',
            'mov t3 t0',
            'mov t1 t3',
            '; __end_imme__',
            '\n',
        ]
    elif number < 190: # 14 lines
        return [
            f'; __begin_imme_{number}__',
            'imme 63',
            'mov t0 t1',
            'mov t0 t2',
            'mov t3 t0', #
            'add',
            'mov t3 t1',
            'mov t0 t3', #
            f'imme {number-126}',
            'mov t0 t2',
            'mov t3 t0', #
            'add',
            'mov t0 t1', #
            'mov t3 t0',
            'mov t1 t3', #
            '; __end_imme__',
            '\n',
        ]
    elif number < 253: # 20 lines
        return [
            f'; __begin_imme_{number}__',
            'imme 63',
            'mov t0 t1',
            'mov t0 t2',
            'mov t3 t0', #
            'add',
            'mov t3 t1',
            'mov t0 t3', #
            'imme 63',
            'mov t0 t2',
            'mov t3 t0', #
            'add',
            'mov t3 t1',
            'mov t0 t3', #
            f'imme {number-189}',
            'mov t0 t2',
            'mov t3 t0', #
            'add',
            'mov t0 t1', #
            'mov t3 t0',
            'mov t1 t3', #
            '; __end_imme__',
            '\n',
        ]
    else:   # 17 lines
        return [
            f'; __begin_imme_{number}__',
            'imme 63',
            'mov t0 t1',
            'mov t0 t2',
            'mov t3 t0', #
            'add',
            'mov t3 t1',
            'mov t3 t2',
            'add',
            'mov t3 t1',
            'mov t0 t3', #
            f'imme {number-252}',
            'mov t0 t2',
            'mov t3 t0', #
            'add',
            'mov t0 t1', #
            'mov t3 t0',
            'mov t1 t3', #
            '; __end_imme__',
            '\n',
        ]



def _labels(pc: int):
    if pc < 1 or pc > 65535:
        raise SyntaxError('Code length exceeded the flash memory.')
    else:
        _cmds = list()
        _cmds.append('; __begin_label__')
        _low_8 = pc & 0xff
        _high_8 = (pc >> 8) & 0xff
        _cmds.extend(_imme(_low_8))
        _cmds.append('mov t0 t3') # _low_8 will be preserved in reg3.
        _cmds.extend(_imme(_high_8))
        _cmds.append('mov t0 t2')
        _cmds.append('mov t3 t1')
        _cmds.append('imme 0')
        _cmds.append('; __end_label__')
        _cmds.append('\n')
        return _cmds
    
def _self_counted_label(pc: int):
    _max_cond_cmd_len = 44
    cmds = _labels(pc)
    _pure_cmds = [c for c in cmds if not c.strip().startswith(';')]
    while len(_pure_cmds) != _max_cond_cmd_len:
        cmds.append('MOV S0 S0')
        _pure_cmds.append('MOV S0 S0')
    return cmds


def _setup():
    # initialize all registers:
    return [
        '; __SETUP_CODE__',
        'IMME 0',
        'MOV T0 T1',
        'MOV T0 T2',
        'MOV T0 T3',
        'MOV T0 S0',
        'MOV T0 S1',
        'MOV T0 SP',
        'MOV T0 IO',
        '; __END_SETUP__',
        '\n',
    ]


    '''
    Begin of the Compiler.
    '''

def exasm_compile(instr: str):
    code = list() 
    code.extend(_setup())

    ops = instr.upper().split('\n') 

    for op in ops:
        op = op.strip()
        if not op: 
            code.append('\n')
            continue

        if op.startswith('XOR'):
            code.extend(_xor())
            continue

        if op.startswith('NOT'):
            code.extend(_not())
            continue

        if op.startswith('SLL'):
            code.extend(_sll())
            continue

        if op.startswith('PUSH'):
            code.extend(_push())
            continue

        if op.startswith('POP'):
            code.extend(_pop())
            continue
        
        if op.startswith('PUSH_L'):
            code.extend(_push_l())
            continue
        
        if op.startswith('POP_L'):
            code.extend(_pop_l())
            continue

        if op.startswith('IMME'):
            __i = op.replace('IMME', '').strip()
            __i = int(__i, base=0)
            code.extend(_imme(__i))
            continue

        code.append(op)

    return code

def exasm_label_expr(in_codes: list, stage: int):
    out_code = list()
    pc = 1

    for in_code in in_codes:
        __c = in_code.upper().strip()

        if __c.startswith(';'): out_code.append(__c); continue
        if __c.startswith('#'): out_code.append(__c); continue
        if not __c: out_code.append('\n'); continue

        if __c.split()[0] in BASIC_CMDS:
            out_code.append(__c)
            pc += 1
            continue

        if __c.startswith('LABEL') and stage == 1:
            _label = __c.split('LABEL')[1].strip()
            if not _label:
                raise SyntaxError('Label name not specified.')
            elif label_dicts.get(_label):
                raise ValueError(f'Multiple defination of label name {_label}.')
            else:
                label_dicts[_label] = pc
                continue

        if __c.startswith('LABEL') and stage == 2:
            out_code.append('; ' + __c)
            continue

        # consider left items are labels:
        if stage == 1:
            pc += 44
            continue
        if stage == 2:
            if __c in label_dicts.keys():
                cmds = _self_counted_label(label_dicts.get(__c))
                out_code.extend(cmds)
                pc += 44
            else:
                raise SyntaxError('Label not exist.')
            
    if stage == 2:
        return out_code


if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        print('exasm [option] [file]')
        print('-o: output file name.')
        exit(0)
    if len(sys.argv) == 2:
        in_file = sys.argv[1]
        out_file = in_file + '.asm'
    elif len(sys.argv) == 3:
        in_file = sys.argv[2]
        out_file = sys.argv[1]
    elif len(sys.argv) == 4:
        if sys.argv[1] != '-o':
            print('exasm [option] [file]')
            print('-o: output file name.')
            exit(0)
        in_file = sys.argv[3]
        out_file = sys.argv[2]
    else:
        print('exasm [option] [file]')
        print('-o: output file name.')
        exit(0)
    
    with open(in_file, 'r') as f:
        instr = f.read()

    try:
        __code = exasm_compile(instr)
        exasm_label_expr(__code, stage=1)
        __code = exasm_label_expr(__code, stage=2)
    except Exception as e:
        print(e)
        exit(0)

    with open(out_file, 'w+') as __out_file:
        __out_file.write('\n'.join(__code).upper())

    


    
    






        

        
        






        