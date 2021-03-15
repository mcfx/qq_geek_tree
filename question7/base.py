import os, base64, requests
if not os.path.isdir('cache'):
    os.mkdir('cache')


def get_chal(s):
    if os.path.isfile('cache/' + s + '.js'):
        return open('cache/' + s + '.js').read()
    r = requests.get('http://159.75.70.9:8080/' + s + '.js').text
    open('cache/' + s + '.js', 'w').write(r)
    return r


def get_chal_vars(s):
    s1 = '__TENCENT_CHAOS_VM.v=5;var g=I(["'
    s2 = '",['
    s = s[s.find(s1) + len(s1):]
    a = s[:s.find('"')]
    s = s[s.find(s2) + len(s2):]
    b = s[:s.find(']')].split(',')
    c = []
    for x in b:
        if x.isnumeric():
            c.append(int(x))
        elif 'e' in x:
            u, v = x.split('e')
            c.append(int(u) * 10**int(v))
        else:
            assert False
    return orig_opcodes, a, c


def decode(a, c):
    a = base64.b64decode(a)
    res = []
    for x in a:
        res.append(x)
        while len(c) and len(res) == c[0]:
            res.append(c[1])
            c = c[2:]
    return res


def encode(s):
    a = []
    b = []
    for i in range(len(s)):
        if s[i] < 256:
            a.append(s[i])
        else:
            b.append(i)
            b.append(s[i])
    return base64.b64encode(bytes(a)).decode(), b


orig_opcodes = {
    0: 'PUSHSUBS',
    1: 'SUBST1',
    2: 'SHL',
    3: 'PUSHTYPE',
    4: 'PUSHNULL',
    5: 'CMPEQ',
    6: 'SUBST2',
    7: 'PACKTOP2',
    8: 'MOVI',
    9: 'OUT',
    10: 'POPN',
    11: 'CHKIN',
    12: 'PACK2',
    14: 'SWAPN',
    15: 'PUSHTOP',
    16: 'PUSHARRTOP',
    18: 'CALL1',
    21: 'FLIP',
    22: 'AND',
    23: 'JMP',
    24: 'POP',
    25: 'CALL2',
    26: 'PUSHWINDOW',
    27: 'ADD',
    28: 'DEL',
    29: 'SUB',
    30: 'SUBST3',
    31: 'PUSHI',
    32: 'XOR',
    33: 'OR',
    34: 'DIV',
    35: 'CMPGE',
    36: 'CALL3',
    37: 'NOT',
    39: 'SHRU',
    40: 'PUSHUNDEF',
    41: 'PUSHTRUE',
    42: 'PUSHFALSE',
    43: 'SHR',
    44: 'DEFINE',
    45: 'PUSHSTR',
    46: 'MUL',
    47: 'UNKGNULL',
    49: 'OUTPOP',
    50: 'SUBST4',
    51: 'SUBST5',
    52: 'JNZ',
    53: 'THROW',
    54: 'RETURN1',
    55: 'MOD',
    56: 'SETLEN',
    58: 'CMPEQ3',
    60: 'SUBST6',
    61: 'CMPG',
    62: 'ORARRAY',
    63: 'SUBST7',
    64: 'CALL4',
    66: 'CONCAT',
    67: 'RETURNG'
}
orig_rev = {}
for i in orig_opcodes:
    orig_rev[orig_opcodes[i]] = i


def execute(code, opcodes, verbose=False, recomp_dict=None):
    res = []
    recompile_code = [0] * len(code)

    def uprint(*args):
        t = str(oldpc).ljust(7, ' ') + ' '.join(map(str, args))
        ot = ' '.join(map(str, args))
        tmp = []
        ok = False
        for i in range(-1, -4, -1):
            si = stack[i]
            ti = '-' if si is None else 'string(%d)' % len(si) if type(si) is str and len(si) > 100 else repr(si)
            tmp.append(ti)
            if si is not None:
                ok = True
        if ok:
            t = t.ljust(39, ' ') + ' ; {%d} ' % len(stack) + ' '.join(tmp)
        if verbose:
            print(t)
        # pos, opstr, stack, text, text_ori
        res.append((oldpc, opstr, stack[-2:], t, ot))

    pc_candidates = [(0, 0)]
    vis = set()

    stack = [None] * 100

    def pop(cnt):
        if not cnt:
            return
        for _ in range(cnt):
            stack.pop(-1)

    def push(x):
        stack.append(x)

    def sset(pos, func):
        if s1 is not None and s2 is not None:
            if pos == 0:
                push(func(s1, s2))
            else:
                stack[-pos] = func(s1, s2)
        else:
            if pos == 0:
                push(None)
            else:
                stack[-pos] = None

    def ssetn(pos):
        if pos == 0:
            push(None)
        else:
            stack[-pos] = None

    the_long_base64_str = ''
    the_long_int_arr = []
    the_long_code_arr = []

    while len(pc_candidates):
        pc, ptype = pc_candidates.pop(0)
        if pc in vis:
            continue
        vis.add(pc)
        if ptype == 4:
            res.append((pc, 'FUNCSTART', [None, None], ''))
        if ptype != 0:
            stack = [None] * 100
        oldpc = pc
        opstr = opcodes[code[pc]]
        opcode = orig_rev[opstr]
        if recomp_dict is not None:
            recompile_code[pc] = recomp_dict[opstr]
        else:
            recompile_code[pc] = opcode
        pc += 1
        altpc = None
        defpc = True
        s1 = stack[-1]
        s2 = stack[-2]
        if opcode == 0:
            pop(1)
            if s1 == 'array_tmp_1':
                push('array_tmp_2')
            else:
                ssetn(0)
            uprint('pop 1: push s1[0][s1[1]]')
        elif opcode == 1:
            uprint('mov stack[s2[0]][0], s1')
        elif opcode == 2:
            pop(1)
            if type(s2) is list:
                ssetn(1)
            else:
                sset(1, lambda s1, s2: s2 << s1)
            uprint('pop 1: shl s2, s1')
        elif opcode == 3:
            ssetn(0)
            uprint('push typeof(s1)')
        elif opcode == 4:
            # ssetn(0)
            push('__NULL')
            uprint('push null')
        elif opcode == 5:
            pop(1)
            sset(1, lambda s1, s2: s2 == s1)
            uprint('pop 1: cmpe s2, s1')
        elif opcode == 6:
            pop(1)
            uprint('pop 1: mov stack[s2[0]][0], s1[0][s1[1]]')
        elif opcode == 7:
            pop(2)
            stack.append([s2, s1])
            uprint('push [s2, s1]')
        elif opcode == 8:
            stack[-1] = code[pc]
            uprint('mov s1, %d' % code[pc])
            recompile_code[pc] = code[pc]
            pc += 1
        elif opcode == 9:
            uprint('out [%d, len(stack), %d]' % (code[pc], code[pc + 1]))
            recompile_code[pc] = code[pc]
            recompile_code[pc + 1] = code[pc + 1]
            pc += 2
        elif opcode == 10:
            pop(code[pc])
            uprint('pop %d' % code[pc])
            recompile_code[pc] = code[pc]
            pc += 1
        elif opcode == 11:
            pop(1)
            ssetn(1)
            uprint('pop 1: check s2 in s1')
        elif opcode == 12:
            pop(2)
            if type(s2) is list and len(s2) > 0 and type(s2[0]) is int:
                push(['__STACK' + str(s2[0]), s1])
            else:
                ssetn(0)
            uprint('pop 2: push [stack[s2][0], s1]')
        elif opcode == 14:
            t = code[pc] + 2
            stack[-1], stack[-t] = stack[-t], stack[-1]
            uprint('swap stack[-%d], s1' % (code[pc] + 2))
            recompile_code[pc] = code[pc]
            pc += 1
        elif opcode == 15:
            push(s1)
            uprint('push s1')
        elif opcode == 16:
            pop(1)
            if s1 is not None:
                push([s1])
            else:
                ssetn(0)
            uprint('pop 1: push [s1]')
        elif opcode == 18:
            pop(1)
            if s1 == 'array_tmp_2':
                push([])
            else:
                ssetn(0)
            uprint('pop 1: push s1([null] + stack[-%d:])' % code[pc])
            recompile_code[pc] = code[pc]
            pc += 1
        elif opcode == 21:
            if s1 is None:
                ssetn(0)
            else:
                push(~s1)
            uprint('flip s1')
        elif opcode == 22:
            pop(1)
            sset(1, lambda s1, s2: s2 & s1)
            uprint('pop 1: and s2, s1')
        elif opcode == 23:
            uprint('jmp %d' % code[pc])
            altpc = [(code[pc], 0)]
            defpc = False
            recompile_code[pc] = code[pc]
            pc += 1
        elif opcode == 24:
            pop(1)
            uprint('pop 1')
        elif opcode == 25:
            pop(code[pc])
            ssetn(0)
            uprint('pop %d: push s1(stack[-%d:])' % (code[pc], code[pc]))
            recompile_code[pc] = code[pc]
            pc += 1
        elif opcode == 26:
            pop(1)
            if s1 == 'Array':
                push('array_tmp_1')
            else:
                ssetn(0)
            uprint('pop 1: push [window, s1]')
        elif opcode == 27:
            pop(1)
            if type(s2) is list or type(s2) is str:
                ssetn(1)
            else:
                sset(1, lambda s1, s2: s2 + s1)
            uprint('pop 1: add s2, s1')
        elif opcode == 28:
            pop(1)
            ssetn(0)
            uprint('pop 1: push del(s1[0][s1[1]])')
        elif opcode == 29:
            pop(1)
            if type(s2) is str or type(s2) is list:
                ssetn(1)
            else:
                sset(1, lambda s1, s2: s2 - s1)
            uprint('pop 1: sub s2, s1')
        elif opcode == 30:
            if type(s2) is list and len(s2) >= 2 and type(s2[0]) is list and s2[1] is not None:
                while len(s2[0]) <= s2[1]:
                    s2[0].append(None)
                if type(s1) is str and len(s1) >= 500:
                    s2[0][s2[1]] = 'the_long_base64_str'
                    the_long_base64_str = s1
                else:
                    s2[0][s2[1]] = s1
                    if len(s2[0]) >= 50:
                        if type(s2[0][0]) is int:
                            the_long_int_arr = s2[0]
                        elif sum(map(lambda x: type(x) is str and x.startswith('CODE_'), s2[0])) >= 20:
                            the_long_code_arr = s2[0]
            uprint('mov s2[0][s2[1]], s1')
        elif opcode == 31:
            push(code[pc])
            uprint('push %d' % code[pc])
            recompile_code[pc] = code[pc]
            pc += 1
        elif opcode == 32:
            pop(1)
            if type(s2) is str or type(s2) is list:
                ssetn(1)
            else:
                sset(1, lambda s1, s2: s2 ^ s1)
            uprint('pop 1: xor s2, s1')
        elif opcode == 33:
            pop(1)
            if type(s2) is list:
                ssetn(1)
            else:
                sset(1, lambda s1, s2: s2 | s1)
            uprint('pop 1: or s2, s1')
        elif opcode == 34:
            pop(1)
            sset(1, lambda s1, s2: s2 // s1)
            uprint('pop 1: div s2, s1')
        elif opcode == 35:
            pop(1)
            sset(1, lambda s1, s2: s2 >= s1)
            uprint('pop 1: cmpge s2, s1')
        elif opcode == 36:
            pop(code[pc])
            s1 = stack[-1]
            pop(1)
            ssetn(0)
            uprint('pop %d: pop 1: push s1[0][s1[1]]([null] + stack[-%d:])' % (code[pc], code[pc]))
            recompile_code[pc] = code[pc]
            pc += 1
        elif opcode == 37:
            if s1 is None:
                ssetn(0)
            else:
                push(not s1)
            uprint('not s1')
        elif opcode == 39:
            pop(1)
            if type(s2) is str or type(s2) is list:
                ssetn(1)
            else:
                sset(1, lambda s1, s2: s2 >> s1)
            uprint('pop 1: ushr s2, s1')
        elif opcode == 40:
            ssetn(0)
            uprint('push undefined')
        elif opcode == 41:
            push(True)
            uprint('push true')
        elif opcode == 42:
            push(False)
            uprint('push false')
        elif opcode == 43:
            pop(1)
            if type(s2) is str or type(s2) is list:
                ssetn(1)
            else:
                sset(1, lambda s1, s2: s2 >> s1)
            uprint('pop 1: shr s2, s1')
        elif opcode == 44:
            a, b, c = code[pc + 0], code[pc + 1], code[pc + 2]
            push('CODE_' + str(a))
            uprint('define_code %d, %d, %d    [%s]' % (a, b, c, ' '.join(map(str, code[pc + 3:pc + 3 + b * 2 + c]))))
            for i in range(3 + b * 2 + c):
                recompile_code[pc + i] = code[pc + i]
            pc += 3
            pc += b * 2 + c
            pc_candidates.append((a, 4))
        elif opcode == 45:
            push('')
            uprint('push ""')
        elif opcode == 46:
            pop(1)
            sset(1, lambda s1, s2: s2 * s1)
            uprint('pop 1: mul s2, s1')
        elif opcode == 47:
            uprint('unk g = null')
        elif opcode == 49:
            uprint('popout')
        elif opcode == 50:
            pop(1)
            ssetn(0)
            uprint('pop 1: push stack[s1[0]][0]')
        elif opcode == 51:
            pop(1)
            uprint('pop 1: mov s2[0][s2[1]], stack[s1[0]][0]')
        elif opcode == 52:
            uprint('jnz %d' % code[pc])
            altpc = [(code[pc], 3)]
            recompile_code[pc] = code[pc]
            pc += 1
        elif opcode == 53:
            uprint('throw s1')
        elif opcode == 54:
            uprint('return true')
            defpc = False
        elif opcode == 55:
            pop(1)
            sset(1, lambda s1, s2: s2 % s1)
            uprint('pop 1: mod s2, s1')
        elif opcode == 56:
            stack = [None] * code[pc]
            uprint('resize stack %d' % code[pc])
            recompile_code[pc] = code[pc]
            pc += 1
        elif opcode == 58:
            pop(1)
            sset(1, lambda s1, s2: s2 == s1)
            uprint('pop 1: cmpeq3 s2, s1')
        elif opcode == 60:
            pop(1)
            uprint('pop 1: mov s2[0][s2[1]], s1[0][s1[1]]')
        elif opcode == 61:
            pop(1)
            sset(1, lambda s1, s2: s2 > s1)
            uprint('pop 1: cmpg s2, s1')
        elif opcode == 62:
            uprint('or stack[s1[0]], []')
        elif opcode == 63:
            pop(2)
            ssetn(0)
            uprint('pop 2: push [s2[0][s2[1]], s1]')
        elif opcode == 64:
            pop(code[pc])
            s1 = stack[-1]
            pop(1)
            ssetn(0)
            uprint('pop %d: pop 1: push s1[0][s1[1]](stack[-%d:])' % (code[pc], code[pc]))
            recompile_code[pc] = code[pc]
            pc += 1
        elif opcode == 66:
            sset(2, lambda s1, s2: s2 + chr(s1 + code[pc]))
            # print(stack[-2:])
            uprint('concat s2, chr(s1 + %d)' % code[pc])
            recompile_code[pc] = code[pc]
            pc += 1
        elif opcode == 67:
            uprint('return !!g')
            defpc = False
        else:
            print(pc, opcode)
            assert False
        if altpc:
            pc_candidates = altpc + pc_candidates
        if defpc:
            pc_candidates.insert(0, (pc, 0))

    pc_pos = {}
    for i in range(len(res)):
        pc_pos[res[i][0]] = i

    ops = []

    assert len(the_long_code_arr) == 68 or len(the_long_code_arr) == 0

    for i in range(len(the_long_code_arr)):
        t = the_long_code_arr[i]
        if t is None:
            continue
        pc = int(t[5:])
        j = pc_pos[pc]
        while res[j][1] != 'FUNCSTART':
            j += 1
        func = res[pc_pos[pc]:j]
        ops.append([i, pc, func])

    return res, (the_long_base64_str, the_long_int_arr, ops, recompile_code)


def dump_res(fn, res):
    open(fn, 'w').write('\n'.join(map(lambda x: x[3], res)))
