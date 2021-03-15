## 批量种树 & 前两题

首先 F12 一下，看看请求，可以发现先 pull 了一个 js，然后把 js 运行的结果返回上去，就成功种下一棵树。那么可以写个脚本快速种树：

```python
import requests


def pull():
    return requests.get('http://159.75.70.9:8081/pull?u=xxx').json()


def push(t, a):
    return requests.get('http://159.75.70.9:8081/push', params={'t': t, 'a': a}).json()


def tree():
    q = pull()
    print(q)
    c = q['c']
    t = q['t']
    if c == 'A274075A':
        a = q['a'][0]
    elif c == 'A3C2EA99':
        a = q['a'][0]
        a = a * a + a
    else:
        assert False
    r = push(t, a)
    print(r)


while True:
    tree()
```

看到服务器的 ip 在广州，于是把脚本放在那边的 vps 上跑，就种的比较快。

前两题非常简单，就不多说了。

## 第三题（100000）

题目中有用的部分如下：

```js
window[g('0x0')] = function (h) {
    var i = 0x30d3f;
    for (var j = 0x30d3f; j > 0x0; j--) {
        var k = 0x0;
        for (var l = 0x0; l < j; l++) {
            k += h['a'][0x0];
        }
        k % h['a'][0x2] == h['a'][0x1] && j < i && (i = j);
    }
    return i;
};
```

只需要优化内层循环就可以有足够的速度了。（下面的代码需要加在前面的脚本的后面）

```python
    elif c == 'A5473788':
        a = q['a']
        i = 0x30d3f
        for j in range(0x30d3f, -1, -1):
            k = a[0] * j
            if k % a[2] == a[1] and j < i:
                i = j
        a = i
```

## 第四题（250000）

一个基本只包含 `+()![]` 的 js。虽然之前看到过类似的混淆，但是没搜到直接能用的反混淆工具。

观察发现这里面大量代码只是为了生成常量，比如

```js
(!![] + [][(![] + [])[+[]] + ([![]] + [][[]])[+!+[] + [+[]]] + (![] + [])[!+[] + !+[]] + (!![] + [])[+[]] + (!![] + [])[!+[] + !+[] + !+[]] + (!![] + [])[+!+[]]])[+!+[] + [+[]]]
```

只是为了生成 `o`。手动发现并替换掉这些常量后，代码就可读了不少：

```js
window.A593C8B8=async(_)=>(($,_,__,___,____)=>{let _____=function*(){while([])yield[(_,__)=>_+__,(_,__)=>_-__,(_,__)=>_*__][++__%(3)]['bind'](0,___,____)}();let ______=function(_____,______,_______){____=_____;___=______['next']()['value']();__==_['a']['length']&&_______(-___)};return new Promise(__=>_['a']['for'+([]['filter']['constructor']('return/0/')()['constructor']+[])['12']+'a'+([]['filter']+[])[3]+'h'](___=>$['setTimeout'](____=>______(___,_____,__),___)))})(window,_,+[],+[],+[])
```

格式化并替换掉变量名：

```js
window.A593C8B8 = async (a) => {
    var b = 0,
        c = 0,
        d = 0;
    let e = function* () {
        while ([]) yield [(a, b) => a + b, (a, b) => a - b, (a, b) => a * b][++b % (3)]['bind'](0, c, d)
    }();
    let f = function (e, f, g) {
        d = e;
        c = f['next']()['value']();
        console.log(d + ' ' + c);
        b == a['a']['length'] && g(-c)
    };
    return new Promise(b => a['a']['forEach'](c => setTimeout(d => f(c, e, b), c)))
}
```

可以发现是按照 a 数组的值 setTimeout 对应时间，再做加减乘的运算。setTimeout 的部分可以用排序代替。

```python
def q4(s):
    s.sort()
    c = 0
    d = 0
    v = [lambda x, y:x + y, lambda x, y:x - y, lambda x, y:x * y]
    for i in range(len(s)):
        d = s[i]
        c = v[(i + 1) % 3](c, d)
    return -c
```

## 第五题（500000）

js 加载了一段 wasm，并把 Math 传了进去。使用 wasm2c 可以反编译得到 C 代码：

```c
extern int ffimport$0(int local0, int local1); /* import */
extern int ffimport$1(int local0, int local1); /* import */
int f0(int local0, int local1) {
	// Parsed WASM function locals:
	int local2; 
	int local3; 
	int local4; 
	int local5; 
	int local6; 
	int local7; 
	local2 = local0;
	if (local4 = local1 - 1) {
	while (1) { // Loop name: 'label$2'
	local3 = local2;
	local6 = 0;
	local7 = 10;
	while (1) { // Loop name: 'label$3'
	local5 = local3 % 10;
	local3 = local3 / 10;
	local6 = 	ffimport$1(local5, local6);
;
	local7 = 	ffimport$0(local5, local7);
;
	if (local3 > 0) break;
	} // End of loop 'label$3'
	local2 = local2 + local6 * local7;
	if (	local4 = local4 - 1;
) break;
	} // End of loop 'label$2'

	} // <No else block>
local2}
```

可以看出，程序把 local2 的每一位用两个外部函数（ffimport）运算，然后乘积加回到 local2 上，重复 local0 这么多次。

而直接查看 wasm 就可以得知这两个外部函数分别是 min 和 max：

![image-20210315201323559](https://cdn.mcfx.work/typora-tmp/image-20210315201323559.png)

这样就可以用 python 实现了：

```python
def f(x, y):
    for i in range(y - 1):
        s = list(map(int, str(x)))
        x += max(s) * min(s)
    return x
```

但是这个实现不够快。其实要加快也很简单，可以发现 min(s) 为 0 时就可以不继续算了，加上这个判断就可以很快得出结果。

## 第六题（1000000）

不难看出是一个栈式虚拟机，照着代码抄一遍可以写一个反汇编器出来。（代码可以在 https://github.com/mcfx0/qq_geek_tree 找到，这里就不放了）

```
0    resize stack 3
2    or stack[2], []
4    push ""
5    concat s1, char(119) # w
7    concat s1, char(105) # i
9    concat s1, char(110) # n
11   concat s1, char(100) # d
13   concat s1, char(111) # o
15   concat s1, char(119) # w
17   pop 1; push [window, s1]
18   push ""
19   concat s1, char(67) # C
21   concat s1, char(65) # A
23   concat s1, char(49) # 1
25   concat s1, char(56) # 8
27   concat s1, char(48) # 0
29   concat s1, char(55) # 7
31   concat s1, char(69) # E
33   concat s1, char(66) # B
```

反汇编之后，发现有大量的代码其实是在构造字符串，于是把这部分也处理成一条 push 字符串的指令。

```
125  pop 1; push s1
126  push stack[s1[0]][0]
138  push "BigInt"
140  pop 1; push [window, s1]
154  push "1661594"
156  pop 1; push s1[0][s1[1]](s1[0], stack[-1:])
158  pop 1; mul s2, s1
159  mov stack[s2[0]][0], s1
160  swap stack[-2], s1
162  push [6]
164  pop 1; push s1
165  push stack[s1[0]][0]
177  push "BigInt"
179  pop 1; push [window, s1]
211  push "1125899906842597"
213  pop 1; push s1[0][s1[1]](s1[0], stack[-1:])
215  mod s2, s1
216  mov stack[s2[0]][0], s1
217  swap stack[-2], s1
```

往后翻，看到了 BigInt 和 mod 操作，于是猜想可能是对输入做若干操作然后模这个大数。在浏览器中运行一遍函数，传 12 个 0 进去，可以得到结果为 6，这像是 6 个 1 相加，而操作应该是乘方。改成 1 和 11 个 0，结果为 1661599，这就比较像是 6 个乘积之和了。

继续实验可以发现，这个代码内置了 12 个数 $b_0,\dots, b_{11}$，而答案是 $\sum_{i=0}^5 b_{2i}^{a^{2i}}b_{2i+1}^{a_{2i+1}}\bmod 1125899906842597$。

于是用快速幂（比如 python 的 pow）来完成这个操作即可。

### 小插曲（1010000）

脚本跑到 1010000 时，发现下发的 js 变了。下载下来查看，发现还是虚拟机，但是指令编码变了，内置的常数也变了。那么我们应该需要一个办法来快速找到这些常数。

这个虚拟机构造字符串的方法是 $[op,char_1,op,char_2,\dots,op,char_n]$，其中 op 是指令编号，$char_i$ 是字符串的第 i 个字符。由于这些 BigInt 也是如此构造的，可以发现这些 $char_i$ 全是数字，而利用这个特点可以高效地找到所需的常数。具体可以看下面的代码。

```python
def find_q6_nums(s):
    def isnum(x):
        return x >= 48 and x <= 57
    i = 1
    res = {}
    while i < len(s):
        if not isnum(s[i]):
            i += 1
            continue
        j = i
        a = set()
        b = []
        while j < len(s) and isnum(s[j]):
            if len(a | set([s[j - 1]])) > 1:
                break
            a.add(s[j - 1])
            b.append(s[j])
            j += 2
        if len(b) < 5:
            i += 1
            continue
        x = list(a)[0]
        y = int(''.join(map(chr, b)))
        if x not in res:
            res[x] = []
        res[x].append(y)
        i = j
    for x in res:
        if len(res[x]) >= 10:
            t = res[x]
            r2 = []
            for i in range(len(t)):
                if t[i] > 10**10:
                    mod = t[i]
                    if t[i - 1] <= 10**7:
                        r2.append(t[i - 1])
            return r2, mod
    return None
```

## 第七题（2000000）

拿到题目，发现又是个栈式虚拟机。但是这次的指令多了不少。反汇编器的代码也放在 https://github.com/mcfx0/qq_geek_tree 。

这次的字符串拼接等指令要更恶心一点，所以反汇编器里面还需要对栈上的状态做少量模拟，这样更方便人查看。

```
21980  push ""                          ; {25} '' [[], 0] []
21981  push 8                           ; {26} 8 '' [[], 0]
21983  concat s2, chr(s1 + 59)          ; {26} 8 'C' [[], 0]
21985  mov s1, 62                       ; {26} 62 'C' [[], 0]
21987  push 26                          ; {27} 26 62 'C'
21989  pop 1: sub s2, s1                ; {26} 36 'C' [[], 0]
21990  concat s2, chr(s1 + 67)          ; {26} 36 'Cg' [[], 0]
21992  mov s1, 53                       ; {26} 53 'Cg' [[], 0]
21994  push 2                           ; {27} 2 53 'Cg'
21996  pop 1: sub s2, s1                ; {26} 51 'Cg' [[], 0]
21997  concat s2, chr(s1 + 60)          ; {26} 51 'Cgo' [[], 0]
21999  mov s1, 38                       ; {26} 38 'Cgo' [[], 0]
22001  push 30                          ; {27} 30 38 'Cgo'
22003  pop 1: add s2, s1                ; {26} 68 'Cgo' [[], 0]
22004  concat s2, chr(s1 + 40)          ; {26} 68 'Cgol' [[], 0]
22006  mov s1, 37                       ; {26} 37 'Cgol' [[], 0]
22008  push 17                          ; {27} 17 37 'Cgol'
22010  pop 1: add s2, s1                ; {26} 54 'Cgol' [[], 0]
22011  concat s2, chr(s1 + 11)          ; {26} 54 'CgolA' [[], 0]
22013  mov s1, 57                       ; {26} 57 'CgolA' [[], 0]
22015  push 31                          ; {27} 31 57 'CgolA'
22017  pop 1: sub s2, s1                ; {26} 26 'CgolA' [[], 0]
22018  concat s2, chr(s1 + 80)          ; {26} 26 'CgolAj' [[], 0]
22020  mov s1, 19                       ; {26} 19 'CgolAj' [[], 0]
22022  push 47                          ; {27} 47 19 'CgolAj'
22024  pop 1: add s2, s1                ; {26} 66 'CgolAj' [[], 0]
22025  concat s2, chr(s1 + 45)          ; {26} 66 'CgolAjo' [[], 0]
22027  mov s1, 46                       ; {26} 46 'CgolAjo' [[], 0]
22029  push 17                          ; {27} 17 46 'CgolAjo'
```

反汇编出来之后，看到他一开始又在拼接 base64 字符串，盲猜又是个虚拟机套娃。

对反汇编器做了若干改进（上面 github 放的已经是最终版本了），可以把 base64 字符串和那个巨大的数组给提出来。由于这里和之前 js 比较相似，盲猜是同一个虚拟机，只是指令编码有所区别，那么我们需要快速找到每个指令的编码是多少。

受到上一题的影响，我怕到 2010000 或者 2020000 时又来一套换编码的虚拟机，我决定用程序来自动分析每个指令是在哪个函数中实现的。由于这个虚拟机基本只是把 js 翻译了一遍，每个函数还是有很强的特征，比如每个算术指令的函数中，一定出现了两个 `length`，一个 `pop`，和一个对应操作的指令。不过程序中还有很多花指令，这些也需要想办法剔除掉。这部分代码也可以在 github 中查看。

把这个套娃的虚拟机解出来之后，好家伙，他也是个套娃。不过由于之前写了通用的处理方法，只需要再调用一遍就能再次解开。

最内层的虚拟机有一个挺长的主函数，应该就是题目需要的函数了。一开始，为了图方便，我把这个函数的字节码转成可以在最外层虚拟机运行的，但是丢进去发现跑不起来。又试了把第二层虚拟机转成最外层等各种方法，最终也还是没能跑起来。

仔细研究发现，这个函数有 7 个参数，其中第一个是题目，而后面 6 个是外面两层传进去的一些参数（其实是 6 个函数），这就导致需要找到这些参数才能解出题目。通过把内层虚拟机拿到外层跑，以及在合适的位置输出整个栈，可以拿到这些函数。不过试图搞三个虚拟机来分别跑这三份代码的尝试失败了。总之只能先读代码了。手动反编译得到如下结果：

```
arg3, func4 ~ func9

a_tmp_15=a_arr.slice(0)
cnt_16=func5()
var_17=0
if(a.length<16)goto label_360
label_394:
if(cnt_16!=0)goto label_415
if(cnt_16<0)goto label_719
push String.fromCharCode(102) // 'f'
'f'+'l'
'fl' + func7(a_tmp_15, var_17)
'fl'+func7(a_tmp_15, var_17)+'{'
'fl'+func7(a_tmp_15, var_17)+'{'+func8(input['t'], cnt_16)
'fl'+func7(a_tmp_15, var_17)+'{'+func8(input['t'], cnt_16)+func9(a_tmp_15, var_17)
return

label_719: infinite loop

label_415:
if(func4(cnt_16)!=cnt_16)goto label_451
i_18=0
label_496:
if(i_18<a.length)goto label_589
cnt_16=func5()
goto label_394

label_589:
var_17=func6(cnt_16^a_tmp_15[i_18],var_17)
i_18++
goto label_496

label_451: infinite loop

label_360: infinite loop
```

由于可以拿到这些函数的 js 对象，经过实验可以发现，其中 func4(x) 大概是输出 x-1，func5 每次调用会 -1，func6 是模 $2^{32}$ 意义下的加法，func7 对于题目的 a 只会输出 `ag`，func8(x,y) 是 x.repeat(y+1)，func9 对于题目的 a 只会输出 `}`。

于是最后的答案便是 flag{题目的 t}。

另外多说一句，label_415 处的 `if(func4(cnt_16)!=cnt_16)goto label_451` 似乎一定会返回 true，然后就跳到 label_451 去死循环了，这也许就是硬跑跑不出来的原因？。。

## 第八题（2000001）

代码很简单：

```js
window.C37CD28B=function({a}){let max=1n;let sum=0n;for(let i=0;i<a[0];i++)max*=10n;loop:for(let i=2n;i<max;i++){for(let j=2n;j<i;j++){if(i%j==0n)continue loop;}sum^=i;}return sum+"";}
```

是求所有 $\le 10^{13}$ 的质数的异或和。

使用 fast prime sieve 之类的关键词可以搜索到 [primesieve](https://github.com/kimwalisch/primesieve) 这个项目，而他的示例中给出了一个多线程求和的代码（https://github.com/kimwalisch/primesieve#libprimesieve-multi-threading）。改成异或就可以了。