# -*- coding: utf-8 -*-
"""Parse extracted law text into structured article JSON, then inject into template -> index.html."""
import sys, re, json
sys.stdout.reconfigure(encoding='utf-8')

from extract_rtf import extract

SOURCES = [
    # (doc file, lawKey, display name, short filter label, effective date)
    ('산업안전보건법(법률)(제21374호)(20260601).doc', 'law', '산업안전보건법', '법', '2026. 6. 1.'),
    ('산업안전보건법 시행령(대통령령)(제36220호)(20260324).doc', 'enf', '산업안전보건법 시행령', '시행령', '2026. 3. 24.'),
    ('산업안전보건법 시행규칙(고용노동부령)(제00470호)(20260601).doc', 'rule', '산업안전보건법 시행규칙', '시행규칙', '2026. 6. 1.'),
    ('산업안전보건기준에 관한 규칙(고용노동부령)(제00450호)(20260302).doc', 'std', '산업안전보건기준에 관한 규칙', '안전보건규칙', '2026. 3. 2.'),
]

ART_RE = re.compile(r'^제(\d+)조(?:의(\d+))?\(([^)]*)\)\s*(.*)$')
ART_DEL_RE = re.compile(r'^제(\d+)조(?:의(\d+))?\s*삭제')
CHAP_RE = re.compile(r'^(제\d+장(?:의\d+)?)\s+(.*)$')


def parse_articles(text, lawKey, lawName):
    lines = text.split('\n')
    articles = []
    chapter = ''
    cur = None
    started = False
    for raw in lines:
        line = raw.strip()
        if not line:
            if cur is not None:
                cur['_buf'].append('')
            continue
        mc = CHAP_RE.match(line)
        if mc and not ART_RE.match(line):
            chapter = mc.group(1) + ' ' + mc.group(2).strip()
            continue
        md = ART_DEL_RE.match(line)
        ma = ART_RE.match(line)
        if ma:
            started = True
            if cur is not None:
                articles.append(cur)
            jo = int(ma.group(1))
            sub = int(ma.group(2)) if ma.group(2) else 0
            label = '제%d조' % jo + (('의%d' % sub) if sub else '')
            cur = {
                'lawKey': lawKey, 'law': lawName,
                'article': label, 'jo': jo, 'sub': sub,
                'chapter': chapter, 'title': ma.group(3).strip(),
                '_buf': [ma.group(4).strip()],
            }
            continue
        if md:
            # deleted article: close current, skip
            started = True
            if cur is not None:
                articles.append(cur)
                cur = None
            continue
        if started and cur is not None:
            cur['_buf'].append(line)
    if cur is not None:
        articles.append(cur)

    out = []
    for a in articles:
        body = '\n'.join(a.pop('_buf')).strip()
        body = re.sub(r'\n{3,}', '\n\n', body)
        if not body and not a['title']:
            continue
        a['body'] = body
        out.append(a)
    return out


def main():
    all_articles = []
    meta = []
    for fn, key, name, short, eff in SOURCES:
        txt = extract(fn)
        arts = parse_articles(txt, key, name)
        meta.append((name, short, key, len(arts), eff))
        all_articles.extend(arts)
        print('%-30s %4d articles' % (name, len(arts)))
    laws_meta = [{'key': k, 'name': n, 'short': s, 'count': c, 'eff': e} for (n, s, k, c, e) in meta]

    # Open-API(DRF)로 받아온 추가 법령/고시/별표 병합 (fetch_all.py 산출물)
    try:
        extra = json.load(open('fetched_laws.json', encoding='utf-8'))
        all_articles.extend(extra['articles'])
        have = set(l['key'] for l in laws_meta)
        for l in extra['laws']:
            if l['key'] not in have:
                laws_meta.append({'key': l['key'], 'name': l['name'], 'short': l['short'],
                                  'count': 0, 'eff': l.get('eff', '')})
                have.add(l['key'])
        print('+ fetched_laws.json: %d articles (%s)' %
              (len(extra['articles']), ', '.join(l['short'] for l in extra['laws'])))
    except FileNotFoundError:
        pass

    # 병합 후 법령별 조문 수 재계산 (별표 추가분 반영)
    counts = {}
    for a in all_articles:
        counts[a['lawKey']] = counts.get(a['lawKey'], 0) + 1
    for lm in laws_meta:
        lm['count'] = counts.get(lm['key'], 0)

    print('TOTAL', len(all_articles))

    data = {
        'laws': laws_meta,
        'articles': all_articles,
    }
    json.dump(data, open('lawdata.json', 'w', encoding='utf-8'), ensure_ascii=False)
    print('wrote lawdata.json')

    # inject into template
    try:
        tpl = open('template.html', encoding='utf-8').read()
    except FileNotFoundError:
        print('template.html not found; skipping inject')
        return
    payload = json.dumps(data, ensure_ascii=False)
    html = tpl.replace('/*__LAWDATA__*/null', payload)
    open('index.html', 'w', encoding='utf-8').write(html)
    print('wrote index.html (%d bytes)' % len(html))


if __name__ == '__main__':
    main()
