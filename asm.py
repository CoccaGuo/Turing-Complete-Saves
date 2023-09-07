'''
The Overture CPU assembler.

Author: CoccaGuo
Date: 2023/07/15

Registers:
t0~t3 temp regs,
s0~s1 saved regs,
sp stack ptr,
io gpio.

Basic Instructions:
 - OR
 - NAND
 - NOR
 - AND
 - ADD
 - SUB
 - EQ0
 - LT0
 - LTEQ0
 - JMP
 - NEQ0
 - GTEQ0
 - GT0
 - SW
 - LW

 - LABEL name
 - name

 - MOV R# R#
 - IMME number
 - raw_cmd


 Use `;` for comments.
'''
REGS = {
    'T0': 0,
    'T1': 1,
    'T2': 2,
    'T3': 3,
    'S0': 4,
    'S1': 5,
    'SP': 6,
    'IO': 7,
}

CMDS = {
    # CALC CMDS
    'OR':   0b01_000_000,
    'NAND': 0b01_000_001,
    'NOR':  0b01_000_010,
    'AND':  0b01_000_011,
    'ADD':  0b01_000_100,
    'SUB':  0b01_000_101,
    # COND CMDS
    'EQ0':  0b11_000_001,
    'LT0':  0b11_000_010,
    'LTEQ0':0b11_000_011,
    'JMP':  0b11_000_100,
    'NEQ0': 0b11_000_101,
    'GTEQ0':0b11_000_110,
    'GT0':  0b11_000_111,
    # MEM CMDS
    'SW':   0b01_000_110,
    'LW':   0b01_000_111,
}

labels = dict() # global label dict


def digit(op: str):
    try:
        i = int(op, base=0)
    except ValueError:
        return None
    return i


def register(reg: str):
    if reg in REGS.keys():
        return REGS.get(reg)

    if reg.startswith('R'):
        reg = reg.strip('R')
    if reg.startswith('REG'):
        reg = reg.strip('REG')
    if reg.startswith('$'):
        reg = reg.strip('$')

    try:
        i = int(reg.strip('R'))
        if i>=0 and i<8:
            return i
        else:
            return None
    except ValueError:
        return None


# def _macro(instr: str):
#     '''
#     convert defs into its defination.
#     not used in this stage.
#     '''

#     defs = dict()

#     ops = instr.upper().split('\n')

#     for ind, op in enumerate(ops):
#         op = op.strip()
#         if not op: continue
#         if op.startswith(';'): continue

#         if  op.startswith('DEF'):
#             _defs = op.split()
#             if len(_defs) < 3:
#                 raise SyntaxError(f'Line {ind+1}: `DEF` should follow with an identifier and a const.')
#             _name = _defs[1].strip()
#             _const = ' '.join(_defs[2:]).strip()
#             if not _name or not _const:
#                 raise SyntaxError(f'Line {ind+1}: `DEF` should follow with an identifier and a const.')
#             if _name in defs.keys():
#                 raise SyntaxError(f'Line {ind+1}: Multiple definition of DEF `{_name}`.')
#             defs[_name] = _const

#     replaced = list()
#     lines = instr.upper().split('\n')
#     for l in lines:
#         tokens = [defs.get(t, t) for t in l.split()]
#         replaced.append(' '.join(tokens).strip())
#     return '\n'.join(replaced).strip()


def _compile(instr: str, stage=2):
    '''
    Compile asm into binarys.
    Stage: 1 for parsing labels, 2 for constructing binary.
    '''
    bin = list() # binary code
    

    bin.append(0x00) # reserve the first byte for simulation issues.
    pc = 1 # prog counter
    errs = list()

    ops = instr.upper().split('\n') 

    for ind, op in enumerate(ops):
        op = op.strip()
        if not op: continue
        if op.startswith(';'): continue

        if op.startswith('#'): 
            errs.append(SyntaxError(f'Line {ind+1}: {op}\t Macros are not allowed in this stage.'))
            continue

        # parsing command
        if op in CMDS.keys():
             bin.append(CMDS.get(op))
             pc += 1
             continue

        # parsing label
        if op.startswith('LABEL') and stage == 1:
            if len(op.split('LABEL')) < 2:
                errs.append(SyntaxError(f'Line {ind+1}: {op}\t `LABEL` should follow an identifier.'))
                continue
            _label = op.split('LABEL')[1].strip()
            if not _label:
                errs.append(SyntaxError(f'Line {ind+1}: {op}\t `LABEL` should follow with an identifier.'))
            elif labels.get(_label):
                errs.append(SyntaxError(f'Line {ind+1}: {op}\t Multiple definition of LABEL `{_label}`.'))
            else:
                labels[_label] = pc
                continue

        if op.startswith('LABEL') and stage == 2:
            continue

        if op in labels.keys():
            _pc_ind = labels.get(op)
            if _pc_ind > 63:
                errs.append(IndexError(f'Line {ind+1}: {op}\t LABEL index out of range (0~63).'))
            elif _pc_ind == 0x00:
                errs.append(IndexError(f'Line {ind+1}: {op}\t LABEL index should not be zero.'))
            bin.append(labels.get(op))
            pc += 1
            continue


        # parse mov
        if op.startswith('MOV'):
            _regs = op.split()
            if len(_regs) != 3:
                errs.append(SyntaxError(f'Line {ind+1}: {op}\t `MOV` should follow with two regs.'))
                continue
            _reg_src = register(_regs[1].strip())
            _reg_dst = register(_regs[2].strip())
            if _reg_src is not None and _reg_dst is not None:
                _cmd = 0x80 | _reg_src << 3 | _reg_dst
                bin.append(_cmd)
                pc += 1
                continue
            else:
                errs.append(SyntaxError(f'Line {ind+1}: {op}\t `MOV` should follow with two regs.'))
                continue

        # parse imme
        if op.startswith('IMME'):
            _imme = op.replace('IMME', '').strip()
            _imme = digit(_imme)
            if _imme is None:
                errs.append(SyntaxError(f'Line {ind+1}: {op}\t `IMME` should follow with an integer.'))
                continue
            if _imme >= 0 and _imme < 64:
                bin.append(_imme)
                pc += 1
                continue
            else:
                errs.append(SyntaxError(f'Line {ind+1}: {op}\t Immediate number out of range (0~63).'))
                continue


        # parse raw
        _raw = digit(op)
        if _raw is None and stage == 2:
            errs.append(SyntaxError(f'Line {ind+1}: {op}\t Unidentified instruction `{op}`.'))
        elif _raw is None and stage == 1:
            pc+=1 # take this as an unparsed label.
        elif _raw > 255 or _raw < 0:
            errs.append(IndexError(f'Line {ind+1}: {op}\t Command out of range 0~255.'))
        else:
            bin.append(_raw)
            pc += 1
            continue

    if stage == 1:
        return 0
    elif stage == 2:
        if not errs:
            return 0, bin
        else:
            return len(errs), errs


if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        print('asm [option] [file]')
        print('-o: output file name.')
        exit(0)
    if len(sys.argv) == 2:
        in_file = sys.argv[1]
        out_file = in_file + '.bin'
    elif len(sys.argv) == 3:
        in_file = sys.argv[2]
        out_file = sys.argv[1]
    elif len(sys.argv) == 4:
        if sys.argv[1] != '-o':
            print('asm [option] [file]')
            print('-o: output file name.')
            exit(0)
        in_file = sys.argv[3]
        out_file = sys.argv[2]
    else:
        print('asm [option] [file]')
        print('-o: output file name.')
        exit(0)
    
    with open(in_file, 'r') as f:
        instr = f.read()
    
    _compile(instr, stage=1)
    err, bin = _compile(instr, stage=2)
    if err != 0:
        for e in bin:
            print(e)
        print(f'Assembly terminated with {err} error(s).')
        exit(0)
    else:
        with open(out_file, 'wb') as f:
            f.write(bytes(bin))
        print(f'Assembly finished.')
        print(f'Output file: {out_file}')
        exit(0)
    




