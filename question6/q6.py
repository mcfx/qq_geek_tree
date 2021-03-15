code = eval(open('q6t.js').read())


res = []


def uprint(*args):
    res.append(str(oldpc).ljust(5, ' ') + ' '.join(map(str, args)))


push_string = None

pc = 0
while pc < len(code):
    oldpc = pc
    opcode = code[pc]
    pc += 1
    if opcode != 68:
        push_string = None
    if opcode == 0:
        uprint('or s1, s2')
    elif opcode == 3:
        uprint('exit define_code')
    elif opcode == 5:
        uprint('push undefine')
    elif opcode == 7:
        uprint('return true')
    elif opcode == 8:
        uprint('mov s2[0][s2[1]], s1')
    elif opcode == 9:
        uprint('not s1')
    elif opcode == 12:
        uprint('push', '[%d]' % code[pc])
        pc += 1
    elif opcode == 13:
        uprint('mov s1, %d' % code[pc])
        pc += 1
    elif opcode == 15:
        uprint('mod s2, s1')
    elif opcode == 16:
        uprint('push ""')
        push_string = ''
    elif opcode == 17:
        uprint('jmp', code[pc])
        pc += 1
    elif opcode == 24:
        uprint('pop 1; push [stack[s2][0], s1]')
    elif opcode == 25:
        uprint('or stack[%d], []' % code[pc])
        pc += 1
    elif opcode == 31:
        uprint('swap stack[-%d], s1' % (code[pc] + 2))
        pc += 1
    elif opcode == 32:
        uprint('jnz %d' % code[pc])
        pc += 1
    elif opcode == 33:
        uprint('resize stack %d' % code[pc])
        pc += 1
    elif opcode == 34:
        uprint('cmp s2, s1')
    elif opcode == 37:
        uprint('pop 1')
    elif opcode == 41:
        uprint('mov stack[s2[0]][0], s1')
    elif opcode == 44:
        uprint('pop 1; mul s2, s1')
    elif opcode == 45:
        uprint('pop 1; push [window, s1]')
    elif opcode == 48:
        uprint('push stack[s1[0]][0]')
    elif opcode == 52:
        uprint('pop 1; push s1[0][s1[1]](s1[0], stack[-%d:])' % code[pc])
        pc += 1
    elif opcode == 53:
        # print(code[pc])
        uprint('push stack[%d][0]' % code[pc])
        pc += 1
    elif opcode == 55:
        uprint('push %d' % code[pc])
        pc += 1
    elif opcode == 57:
        uprint('pop 1; push s1[0][s1[1]]')
    elif opcode == 58:
        uprint('pop 1; push s1')
    elif opcode == 63:
        uprint('pop %d' % code[pc])
        pc += 1
    elif opcode == 65:
        uprint('add s2, s1')
    elif opcode == 68:
        if push_string is not None:
            push_string += chr(code[pc])
            res.pop()
            uprint('push "%s"' % push_string)
        else:
            uprint('concat s1, char(%d) # %c' % (code[pc], chr(code[pc])))
        pc += 1

open('q6.txt', 'w').write('\n'.join(res))
