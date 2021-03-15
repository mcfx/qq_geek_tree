from base import get_chal, get_chal_vars, decode, execute, dump_res
from findtable import find_table

s = get_chal('F3B9B832')
tab, a, b = get_chal_vars(s)
code = decode(a, b)
res, (a2, b2, ops2, rc1) = execute(code, tab)
code2 = decode(a2, b2)
tab2 = find_table(ops2)
dump_res('stage1.txt', res)
print(tab2)
res2, (a3, b3, ops3, rc2) = execute(code2, tab2)
code3 = decode(a3, b3)
tab3 = find_table(ops3)
dump_res('stage2.txt', res2)
print(tab3)
res3, (a4, b4, ops4, rc3) = execute(code3, tab3)
print(a4, b4, ops4)
dump_res('stage3.txt', res3)
