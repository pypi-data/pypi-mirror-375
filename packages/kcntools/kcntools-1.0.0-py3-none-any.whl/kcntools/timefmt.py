import re
from datetime import datetime

_num = re.compile('^\d+$')
_zh_time_chr = set("∼至今到目前现在当一二三四五六七八九十零〇年月日号")


def _addS(args):
    for li in args:
        for c in "".join(li):
            _zh_time_chr.add(c)


_zh_e_pos = set(["离职", "毕业", '结束'])
_zh_years = set(["至今", "今", "目前", "现在", "当前", "当下"])
_addS([_zh_e_pos, _zh_years])

_ocr_chars = {'o', 'l', 's'}
_en_years = set(["now", "present", 'today', "current"])
_en_moth = {"january": 1, "jan": 1, "february": 2, "feb": 2, "march": 3, "mar": 3,
            "april": 4, "apr": 4, "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7, "jule": 7,
            "august": 8, "aug": 8, "september": 9, "sep": 9, "sept": 9, "october": 10, "oct": 10,
            "november": 11, "nov": 11, "december": 12, "dec": 12}
_time = re.compile("\d+|%s|(^|(?<=[^a-z]))(%s|%s|[%s]+)((?=[^a-z])|$)" % ("|".join(_zh_years), "|".join(_en_years), "|".join(_en_moth), "".join(_ocr_chars)))


def hasNow(dstr):
    """check the dstr has now str"""
    dstr = " %s " % dstr.lower()
    for s in _zh_years:
        if s in dstr:
            return True
    for s in _en_years:
        s = " %s " % s
        if s in dstr:
            return True
    return False


def _numPattern(numStr):
    assert _num.match(numStr) is not None
    _now = datetime.now()
    n = int(numStr)
    if n < 10:
        return 'S'
    if n < 13:
        return 'M'
    if n < 32:
        return 'D'
    if n < 100:
        return 'P'
    if n < _now.year//10:
        return 'U'
    if _now.year-100 < n < _now.year+10:
        return 'Y'
    return 'N'


def genPattern(line):
    _now = datetime.now()
    line = "".join(c if ord(c) < 255 or c in _zh_time_chr else ' ' for c in line.lower())
    line = line.strip()
    pattern = []
    if line in _zh_years:
        return [('→', -1)]

    _maxd = datetime.max

    def addPos(pos):
        if not pos:
            return
        pos = "".join(l for l in pos if l.strip())
        if any(l in pos for l in ['至', '到', 'to', '∼', '~', 'until']):
            pattern.append(('→', -1))
            return
        if any(l in pos for l in _zh_e_pos):
            pattern.append(('↲', -1))
            return
        if pos == 'year':
            pattern.append(('年', -1))
            return
        if pos == 'month' or pos == '.st' or pos == 'st':
            pattern.append(('月', -1))
            return
        if pos == 'nd' or pos == '.nd':
            pattern.append(('日', -1))
            return
        if not pos:
            pos = ' '
        pattern.append((pos, -1))

    p = 0
    for g in _time.finditer(line):
        s, e, numStr = g.start(), g.end(), g.group()
        addPos(line[p:s])
        p = e
        if (numStr in _zh_years) or (numStr in _en_years):
            pattern.append(('Y', _maxd.year))
            pattern.append(('M', _maxd.month))
            continue
        if numStr in _en_moth:
            pattern.append(('M', _en_moth[numStr]))
            continue
        if all(c in _ocr_chars for c in numStr):
            pattern.append((numStr, -2))
            continue

        zeros_idx = -1
        for i, c in enumerate(numStr):
            if c == '0':
                zeros_idx = i
                continue
            break
        if zeros_idx > -1:
            numStr = numStr[zeros_idx+1:]
            pattern.append(('O'*(zeros_idx+1), -1))
        if not numStr:
            continue
        F = _numPattern(numStr)
        if F == 'N':
            if len(numStr) == 3:
                ys, ms = numStr[:1], numStr[1:]
                yf, mf = _numPattern(ys), _numPattern(ms)
                yn, mn = int(ys), int(ms)
                if 0 < yn < 10 and 1 < mn < 33:
                    pattern.append((yf, yn))
                    pattern.append((mf, mn))
                    continue
            if len(numStr) == 4:
                ys, ms = numStr[:2], numStr[2:]
                yf, mf = _numPattern(ys), _numPattern(ms)
                yn, mn = int(ys), int(ms)
                if 0 < yn < 13 and 1 < mn < 33:
                    pattern.append((yf, yn))
                    pattern.append((mf, mn))
                    continue

            if len(numStr) == 5:
                ys, ms = numStr[:4], numStr[4:]
                yf, mf = _numPattern(ys), _numPattern(ms)
                yn, mn = int(ys), int(ms)
                if yn < 1900 and numStr[0] == '1' and _now.year > int(numStr[1:]):
                    pattern.append((yf, int(numStr[1:])))
                    continue
                if yf == 'Y' and 0 < mn:
                    pattern.append((yf, yn))
                    pattern.append((mf, mn))
                    continue
            if len(numStr) == 6:
                ys, ms = numStr[:4], numStr[4:]
                yf, mf = _numPattern(ys), _numPattern(ms)
                yn, mn = int(ys), int(ms)
                if yf == 'Y' and 0 < mn < 13:
                    pattern.append((yf, yn))
                    pattern.append((mf, mn))
                    continue
                if yf == 'Y' and mn > 12:
                    pattern.append((yf, yn))
                    pattern.append((_numPattern(numStr[4]), int(numStr[4])))
                    continue

            if len(numStr) == 6 or len(numStr) == 7:
                ys, ms, ds = numStr[:4], numStr[4], numStr[5:]
                yf, mf, df = _numPattern(ys), _numPattern(ms), _numPattern(ds)
                yn, mn, dn = int(ys), int(ms), int(ds)
                if yf == 'Y' and 0 < mn and 0 < dn < 32:
                    pattern.append((yf, yn))
                    pattern.append((mf, mn))
                    pattern.append((df, dn))
                    continue

            if len(numStr) == 8:
                ys, ms, ds = numStr[:4], numStr[4:6], numStr[6:]
                yf, mf, df = _numPattern(ys), _numPattern(ms), _numPattern(ds)
                yn, mn, dn = int(ys), int(ms), int(ds)
                if yf == 'Y' and 0 < mn < 13 and 0 < dn < 32:
                    pattern.append((yf, yn))
                    pattern.append((mf, mn))
                    pattern.append((df, dn))
                    continue

        pattern.append((F, int(numStr)))

    addPos(line[p:])
    pnum = {}
    for k, v in pattern:
        if v == -1 and k.strip() and all(ord(c) < 255 for c in k) and ("O" not in k):
            pnum[k] = pnum.get(k, 0)+1
    pnum = list(pnum.items())
    pnum.sort(key=lambda x: x[1])
    if len(pnum) > 0 and pnum[-1][1] > 1:
        key = {pnum[-1][0]: "/", "~": "-"}
        if len(pnum) == 2 and pnum[0][1] == 1:
            key[pnum[0][0]] = "-"
        newP = []
        for k, v in pattern:
            if v < 0 and k in key:
                newP.append((key[k], v))
            else:
                newP.append((k, v))
        pattern = newP

    return pattern


def _loadPattern():
    import os
    import json
    # file map
    py_dir = os.path.split(os.path.realpath(__file__))[0]
    with open(os.path.abspath(os.path.join(py_dir, 'time.pattern.json')), encoding='utf-8') as fd:
        return json.load(fd)


_PATTERNS = _loadPattern()

_mre = re.compile('\'\d+\'|[1-9a-z]')
_mPstr = re.compile('^(\'\d+\'|[1-9a-z])+$')


def _genPStr(pStr, nums):
    if not pStr:
        return ''
    assert _mPstr.match(pStr) is not None
    strs = []
    for g in _mre.finditer(pStr):
        x = g.group()
        if x[0] == "'":
            strs.append(x[1:-1])
            continue
        strs.append(str(nums[int(x, 24)-1]))
    return "".join(strs)


def _genDate(modeStr, nums):
    Y, M, D = modeStr.split('-')
    Y = _genPStr(Y, nums)
    if not Y:
        return ''
    _now = datetime.now()
    _nowY = _now.year
    _nowStr = str(_nowY)
    if len(_nowStr) < len(Y):
        return ''
    if len(_nowStr) > len(Y):
        xlen = len(_nowStr)-len(Y)
        Y1 = "%s%s" % (_nowStr[:xlen], Y)
        if int(Y1) > _nowY+5:
            if not int(_nowStr[:xlen]) > 1:
                return ''
            Y1 = "%s%s" % (str(int(_nowStr[:xlen])-1), Y)
        Y = Y1
    if int(Y) > _nowY+10:
        # wrong years
        return ''
    M = _genPStr(M, nums)
    if not (M and 0 < int(M) < 13):
        M = str(_now.month)
    D = _genPStr(D, nums)
    if not (D and 0 < int(D) < 32):
        D = str(min(28, _now.day))
    return '%d-%.2d-%.2d' % (int(Y), int(M), int(D))


_timeF = '%Y-%m-%d'


def recognize(time_str):
    pat = genPattern(time_str)
    patStr = "".join(p[0] for p in pat)
    if patStr not in _PATTERNS:
        #print("\"%s\":" % patStr)
        return (None, None)
    nums = [l[1] for l in pat if l[1] > 0]
    pat = _PATTERNS[patStr]
    #print(patStr, pat)
    fr, to = None, None
    if pat['from'] != '--':
        fr = _genDate(pat['from'], nums)
    if pat['to'] != '--':
        to = _genDate(pat['to'], nums)

    try:
        fr = datetime.strptime(fr, _timeF) if fr else None
    except:
        fr = None
    try:
        to = datetime.strptime(to, _timeF) if to else None
    except:
        to = None
    if fr and to:
        if fr.timestamp() > to.timestamp():
            return (to, fr)
    return (fr, to)
