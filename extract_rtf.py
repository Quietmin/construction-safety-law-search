# -*- coding: utf-8 -*-
"""RTF(.doc) -> plain text extractor for 국가법령정보센터 exports (iText RTF)."""
import sys

SKIP_DEST = {
    'fonttbl','colortbl','stylesheet','info','generator','filetbl',
    'listtable','listoverridetable','revtbl','rsidtbl','pgdsctbl',
    'header','footer','headerl','headerr','headerf','footerl','footerr','footerf',
    'pict','object','themedata','datastore','latentstyles','xmlnstbl',
}

def rtf_to_text(s):
    out = []
    stack = [{'skip': False, 'uc': 1}]
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c == '{':
            stack.append({'skip': stack[-1]['skip'], 'uc': stack[-1]['uc']})
            i += 1
        elif c == '}':
            if len(stack) > 1:
                stack.pop()
            i += 1
        elif c == '\\':
            if i + 1 >= n:
                break
            nxt = s[i+1]
            if nxt == '*':
                stack[-1]['skip'] = True
                i += 2
                continue
            if nxt == "'":
                hx = s[i+2:i+4]
                i += 4
                if not stack[-1]['skip']:
                    try:
                        out.append(bytes([int(hx, 16)]).decode('cp1252', 'ignore'))
                    except Exception:
                        pass
                continue
            if nxt == 'u' and i + 2 < n and (s[i+2] == '-' or s[i+2].isdigit()):
                j = i + 2
                if s[j] == '-':
                    j += 1
                while j < n and s[j].isdigit():
                    j += 1
                num = int(s[i+2:j])
                if num < 0:
                    num += 65536
                if not stack[-1]['skip']:
                    out.append(chr(num))
                i = j
                # skip uc fallback chars
                uc = stack[-1]['uc']
                skipped = 0
                while skipped < uc and i < n:
                    if s[i] == '\\':
                        if i + 1 < n and s[i+1] == "'":
                            i += 4
                        else:
                            i += 2
                        skipped += 1
                    elif s[i] in '{}':
                        break
                    else:
                        i += 1
                        skipped += 1
                continue
            if nxt.isalpha():
                j = i + 1
                while j < n and s[j].isalpha():
                    j += 1
                word = s[i+1:j]
                param = None
                k = j
                if k < n and (s[k] == '-' or s[k].isdigit()):
                    k2 = k + 1 if s[k] == '-' else k
                    while k2 < n and s[k2].isdigit():
                        k2 += 1
                    param = int(s[k:k2])
                    k = k2
                if k < n and s[k] == ' ':
                    k += 1
                i = k
                if word == 'bin' and param and param > 0:
                    i += param
                    continue
                if word == 'uc':
                    stack[-1]['uc'] = param if param is not None else 1
                    continue
                if word in SKIP_DEST:
                    stack[-1]['skip'] = True
                    continue
                if not stack[-1]['skip']:
                    if word in ('par', 'line', 'sect'):
                        out.append('\n')
                    elif word in ('row',):
                        out.append('\n')
                    elif word in ('cell', 'tab'):
                        out.append('\t')
                continue
            else:
                sym = nxt
                i += 2
                if not stack[-1]['skip']:
                    if sym in ('\\', '{', '}'):
                        out.append(sym)
                    elif sym == '~':
                        out.append(' ')
                    elif sym in ('-', '_'):
                        pass
                continue
        else:
            if not stack[-1]['skip'] and c not in '\r\n':
                out.append(c)
            i += 1
    return ''.join(out)


def extract(path):
    raw = open(path, 'rb').read().decode('latin-1')
    return rtf_to_text(raw)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    txt = extract(sys.argv[1])
    out_path = sys.argv[2] if len(sys.argv) > 2 else None
    if out_path:
        open(out_path, 'w', encoding='utf-8').write(txt)
        print('wrote', len(txt), 'chars to', out_path)
    else:
        print(txt[:3000])
