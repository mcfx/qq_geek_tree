from base import orig_rev, orig_opcodes


def find_table(ops):
    for op in ops:
        func = op[2]
        opcnt = {t: 0 for t in orig_rev}
        for x in func:
            t = x[1]
            opcnt[t] += 1
        op.append(opcnt)

    def check_ORARRAY(op):
        func = op[2]
        c1 = 0
        c2 = 0
        for x in func:
            t = x[2][1]
            if type(t) is str:
                if t == 'undefined':
                    c1 += 1
                elif t == 'length':
                    c2 += 1
        if c1 >= 1 and c2 >= 3:
            return 'ORARRAY'
        return None

    def check_CALL(op):
        func = op[2]
        opcnt = op[3]
        c1 = 0
        c2 = 0
        c3 = 0
        u = []
        for x in func:
            t = x[2][1]
            if type(t) is str:
                if t == 'apply':
                    c1 += 1
                    u.append(t)
                elif t == 'Function':
                    c2 += 1
                    u.append(t)
                elif t == 'prototype':
                    c3 += 1
                    u.append(t)
        if c1 and c2 and c3:
            if len(func) >= 475:
                return 'CALL3'
            return 'CALL1'
        if c1:
            if len(func) >= 320:
                return 'CALL4'
            return 'CALL2'
        return None

    def check_ALU(op):
        func = op[2]
        opcnt = op[3]
        c1 = 0
        c2 = 0
        for x in func:
            t = x[2][1]
            if type(t) is str:
                if t == 'length':
                    c1 += 1
                elif t == 'pop':
                    c2 += 1
        if c1 == 2 and c2 == 1:
            if opcnt['CMPEQ3'] == 1:
                return 'CMPEQ3'
            if opcnt['DIV'] == 1:
                return 'DIV'
            if opcnt['MOD'] == 1:
                return 'MOD'
            # if opcnt['MUL'] == 1:
            #    return 'MUL'
            if opcnt['CMPEQ'] == 1:
                return 'CMPEQ'
            if opcnt['CMPG'] == 1:
                return 'CMPG'
            if opcnt['CMPGE'] == 1:
                return 'CMPGE'
        return None

    def check_RETURN(op):
        func = op[2]
        for x in func:
            if x[1].startswith('RETURN') and x[2][1] is not None:
                print(x)
                if x[2][1] == True:
                    return 'RETURN1'
        return None

    def check_PUSHUNDEF(op):
        func = op[2]
        c1 = 0
        for x in func:
            t = x[2][1]
            if type(t) is str:
                if t == 'undefined':
                    c1 += 1
        if c1:
            return 'PUSHUNDEF'
        return None

    def check_CONCAT(op):
        func = op[2]
        c1 = 0
        for x in func:
            t = x[2][1]
            if type(t) is str:
                if t == 'fromCharCode':
                    c1 += 1
        if c1:
            return 'CONCAT'
        return None

    def check_OPTX(op):
        opcnt = op[3]
        if opcnt['PUSHTYPE'] >= 1:
            return 'PUSHTYPE'
        if opcnt['THROW'] >= 1:
            return 'THROW'
        # if opcnt['PUSHWINDOW'] >= 1:
        #    return 'PUSHWINDOW'
        return None

    def check_SETLEN(op):
        func = op[2]
        opcnt = op[3]
        c1 = 0
        c2 = 0
        c3 = 0
        c4 = 0
        lst = None
        for x in func:
            t = x[2][1]
            if type(t) is str:
                if t == 'length':
                    c1 += 1
            if lst is not None and lst[4] == 'push 1' and x[1] == 'ADD' and t is None:
                c2 += 1
            if lst is not None and lst[4] == 'push 1' and x[1] == 'SUB' and t is None:
                c4 += 1
            if x[1] == 'SUB' and t is None:
                c3 += 1
            lst = x
        if c1 == 1 and c2 == 1:
            if c3:
                if c4:
                    if opcnt['JNZ']:
                        return 'JNZ'
                    return 'MOVI'
                return 'POPN'
            return 'SETLEN'
        return None

    def check_PUSHI(op):
        func = op[2]
        opcnt = op[3]
        c1 = 0
        c2 = 0
        c3 = 0
        c4 = 0
        lst = None
        for x in func:
            t = x[2][1]
            if type(t) is str:
                if t == 'push':
                    c1 += 1
                elif t == 'length':
                    c3 += 1
                elif t == 'pop':
                    c4 += 1
            if lst is not None and lst[4] == 'push 1' and x[1] == 'ADD' and t is None:
                c2 += 1
            lst = x
        if c1 == 1 and c2 == 1:
            if c3 == 2 and c4 == 1:
                return 'SWAPN'
            return 'PUSHI'
        return None

    def check_PUSHARRTOP(op):
        func = op[2]
        opcnt = op[3]
        c1 = 0
        c2 = 0
        c3 = 0
        c4 = 0
        for x in func:
            t = x[2][1]
            if type(t) is str:
                if t == 'push':
                    c1 += 1
                elif t == 'pop':
                    c2 += 1
                elif t == 'Array':
                    c3 += 1
            if x[1] == 'SUBST3' and type(x[2][0]) is list and type(x[2][0][0]) is list and len(x[2][0][0]) == 2:
                c4 += 1
        if c1 == 1 and c2 == 1 and c3 == 1:
            if c4:
                return 'PUSHWINDOW'
            return 'PUSHARRTOP'
        return None

    def check_JMP(op):
        func = op[2]
        opcnt = op[3]
        c1 = 0
        lst = None
        for x in func:
            t = x[2][1]
            if lst is not None and lst[4] == 'push 1' and x[1] == 'ADD' and t is None:
                c1 += 1
            lst = x
        if c1 == 1:
            return 'JMP'
        return None

    def check_PUSHNULL(op):
        func = op[2]
        opcnt = op[3]
        c1 = 0
        c2 = 0
        c3 = 0
        c4 = 0
        c5 = 0
        c6 = 0
        lst = None
        for x in func:
            t = x[2][1]
            if type(t) is str:
                if t == 'push':
                    c1 += 1
                elif t == 'pop':
                    c2 += 1
            if lst is not None and x[1] == 'CALL4':
                if lst[2][1] == True:
                    c3 += 1
                elif lst[2][1] == '__NULL':
                    c4 += 1
                elif lst[2][1] == '':
                    c5 += 1
                elif lst[2][1] == False:
                    c6 += 1
            lst = x
        if c1 == 1 and c2 == 0:
            if c3:
                return 'PUSHTRUE'
            if c4:
                return 'PUSHNULL'
            if c5:
                return 'PUSHSTR'
            if c6:
                return 'PUSHFALSE'
        return None

    def check_DEFINE(op):
        func = op[2]
        opcnt = op[3]
        if opcnt['DEFINE']:
            return 'DEFINE'

    def check_POP(op):
        func = op[2]
        opcnt = op[3]
        c1 = 0
        c2 = 0
        c3 = 0
        for x in func:
            t = x[2][1]
            if type(t) is str:
                if t == 'push':
                    c1 += 1
                elif t == 'pop':
                    c2 += 1
                elif t == 'length':
                    c3 += 1
        if c1 == 0 and c2 == 1 and c3 == 0:
            return 'POP'

    def check_SUBST1(op):
        func = op[2]
        opcnt = op[3]
        c1 = 0
        c2 = 0
        c3 = 0
        lst = None
        for x in func:
            t = x[2][1]
            if type(t) is str:
                if t == 'length':
                    c1 += 1
                elif t == 'pop':
                    c2 += 1
            lst = x
        if c1 == 2 and c2 == 0:
            if func[0][4] == 'resize stack 10':  # emmmm
                return 'SUBST3'
            return 'SUBST1'

    def check_PUSHTOP(op):
        func = op[2]
        opcnt = op[3]
        c1 = 0
        c2 = 0
        c3 = 0
        lst = None
        for x in func:
            t = x[2][1]
            if type(t) is str:
                if t == 'length':
                    c1 += 1
                elif t == 'push':
                    c2 += 1
            if lst is not None and lst[4] == 'push 1' and x[1] == 'SUB' and t is None:
                c3 += 1
            lst = x
        if c1 == 1 and c2 == 1 and c3 == 1:
            return 'PUSHTOP'
        return None

    def check_ALU_pass2(op):
        func = op[2]
        opcnt = op[3]
        c1 = 0
        c2 = 0
        c3 = 0
        c4 = 0
        c5 = 0
        c6 = 0
        c7 = 0
        c8 = 0
        c9 = 0
        c10 = 0
        c11 = 0
        c12 = 0
        lst = None
        for x in func:
            t = x[2][1]
            if type(t) is str:
                if t == 'length':
                    c1 += 1
                elif t == 'pop':
                    c2 += 1
            if lst is not None and lst[2] == [None, None] and x[1] == 'ADD':
                c3 += 1
            if lst is not None and lst[2] == [None, None] and x[1] == 'SUB':
                c4 += 1
            if lst is not None and lst[2] == [None, None] and x[1] == 'MUL':
                c5 += 1
            if lst is not None and lst[2] == [None, None] and x[1] == 'SHL':
                c6 += 1
            if lst is not None and lst[2] == [None, None] and x[1] == 'SHR':
                c7 += 1
            if lst is not None and lst[2] == [None, None] and x[1] == 'SHRU':
                c8 += 1
            if lst is not None and lst[2] == [None, None] and x[1] == 'AND':
                c9 += 1
            if lst is not None and lst[2] == [None, None] and x[1] == 'OR':
                c10 += 1
            if lst is not None and lst[2] == [None, None] and x[1] == 'XOR':
                c11 += 1
            if lst is not None and lst[2] == [None, None] and x[1] == 'CHKIN':
                c12 += 1
            lst = x
        if c1 == 2 and c2 == 1:
            if c3:
                return 'ADD'
            if c4:
                return 'SUB'
            if c5:
                return 'MUL'
            if c6:
                return 'SHL'
            if c7:
                return 'SHR'
            if c8:
                return 'SHRU'
            if c9:
                return 'AND'
            if c10:
                return 'OR'
            if c11:
                return 'XOR'
            if c12:
                return 'CHKIN'
        return None

    def check_PACK2(op):
        func = op[2]
        opcnt = op[3]
        c1 = 0
        c2 = 0
        c3 = 0
        c4 = 0
        u = []
        for x in func:
            t = x[2][1]
            if type(t) is str:
                if t == 'push':
                    c1 += 1
                    u.append(t)
                elif t == 'pop':
                    c2 += 1
                    u.append(t)
                elif t == 'Array':
                    c3 += 1
                    u.append(t)
                elif t == 'reverse':
                    c4 += 1
                    u.append(t)
        if c1 == 1 and c2 == 2 and c3 == 1:
            if c4 == 1:
                return 'PACKTOP2'
            if u == ['pop', 'pop', 'push', 'Array']:  # emmmm
                return 'SUBST7'
            if u == ['pop', 'push', 'Array', 'pop']:
                return 'PACK2'
        return None

    def check_SUBST4(op):
        func = op[2]
        opcnt = op[3]
        c1 = 0
        c2 = 0
        u = []
        for x in func:
            t = x[2][1]
            if type(t) is str:
                if t == 'push':
                    c1 += 1
                    u.append(t)
                elif t == 'pop':
                    c2 += 1
                    u.append(t)
        if c1 == 1 and c2 == 1:
            if opcnt['FLIP']:
                return 'FLIP'
            if opcnt['NOT']:
                return 'NOT'
            if u == ['push', 'pop']:
                return 'SUBST4'
            if opcnt['DEL']:
                return 'DEL'
            return 'PUSHSUBS'
        return None

    def check_OUT(op):
        func = op[2]
        opcnt = op[3]
        c1 = 0
        u = []
        lst = None
        for x in func:
            t = x[2][1]
            if type(t) is str:
                if t == 'push':
                    u.append(t)
                elif t == 'Array':
                    u.append(t)
                elif t == 'length':
                    u.append(t)
            if lst is not None and lst[4] == 'push 1' and x[1] == 'ADD' and t is None:
                c1 += 1
            lst = x
        if c1 == 2 and u == ['push', 'Array', 'length']:
            return 'OUT'
        return None

    def check_RETURNG(op):
        func = op[2]
        lst = None
        for x in func:
            t = x[2][1]
            if lst is not None and lst[4] == 'pop 1' and x[1].startswith('RETURN') and t is None:
                return 'RETURNG'
            lst = x

    def check_SUBST2(op):
        func = op[2]
        opcnt = op[3]
        c1 = 0
        c2 = 0
        c3 = 0
        lst = None
        for x in func:
            t = x[2][1]
            if type(t) is str:
                if t == 'length':
                    c1 += 1
                elif t == 'pop':
                    c2 += 1
            if lst is not None and lst[4] == 'push 1' and x[1] == 'SUB' and t is None:
                c3 += 1
            lst = x
        if c1 == 1 and c2 == 1 and c3 == 1:
            return 'SUBST2'
        return None

    def special(op):
        # return None
        if op[0] == 52:
            return 'SUBST2'
        if op[0] == 63:
            return 'SUBST6'  # not sure
        if op[0] == 11:
            return 'SUBST5'  # not sure too

    checks = [
        check_ORARRAY,
        check_CALL,
        check_ALU,
        check_RETURN,
        check_PUSHUNDEF,
        check_CONCAT,
        check_OPTX,
        check_SETLEN,
        check_PUSHI,
        check_PUSHARRTOP,
        check_JMP,
        check_PUSHNULL,
        check_DEFINE,
        check_POP,
        check_SUBST1,
        check_PUSHTOP,
        check_ALU_pass2,
        check_PACK2,
        check_SUBST4,
        check_OUT,
        check_RETURNG,
        check_SUBST2,
        # special,
    ]

    known = {}
    res = {}
    unknown = set(orig_rev)

    for checker in checks:
        tmp = {}
        tfunc = []
        opsn = []
        for op in ops:
            t = checker(op)
            if t is not None:
                assert t in unknown
                tmp[t] = op
                res[op[0]] = t
                print(t, *op[:2], len(op[2]))
                tfunc.append(op[:2])
            else:
                opsn.append(op)
        print(checker, {x: tmp[x][:2] for x in tmp.keys()}, tfunc)
        assert len(tmp) == len(tfunc) or list(tmp) == ['POP'] or list(tmp) == ['SUBST2']
        for x in tmp:
            unknown.remove(x)
        known.update(tmp)
        ops = opsn
    for op in ops:
        print(op[0], op[1], len(op[2]))
    return res
