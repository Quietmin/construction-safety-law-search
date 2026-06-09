# -*- coding: utf-8 -*-
"""국가법령정보센터 Open-API(DRF)로 건설안전 관련 법령/고시/별표를 모두 수집.
- 조문형 법령(target=law): 조문 + 별표
- 고시/행정규칙(target=admrul): 조문 + 별표
- 별표: 별표내용 텍스트 추출(표·이미지형은 제목+부분텍스트만 들어올 수 있음)
출력: fetched_laws.json  (build_data.py 가 lawdata.json 에 병합)
"""
import sys, json, re, time
import urllib.request, urllib.parse
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')
OC = sys.argv[1] if len(sys.argv) > 1 else 'unicpla'
UA = {'User-Agent': 'Mozilla/5.0'}

# 조문형 법령 (신규 추가분).  (검색명, key, 표시명, 필터라벨)
LAW_TARGETS = [
    ('중대재해 처벌 등에 관한 법률',            'sap',   '중대재해처벌법',           '중대재해법'),
    ('중대재해 처벌 등에 관한 법률 시행령',      'sap_e', '중대재해처벌법 시행령',     '중대재해법령'),
    ('건설기술 진흥법',                         'ctp',   '건설기술 진흥법',           '건설기술진흥법'),
    ('건설기술 진흥법 시행령',                   'ctp_e', '건설기술 진흥법 시행령',     '건진법령'),
    ('건설기술 진흥법 시행규칙',                 'ctp_r', '건설기술 진흥법 시행규칙',   '건진법규칙'),
    ('시설물의 안전 및 유지관리에 관한 특별법',   'fac',   '시설물안전법',             '시설물안전법'),
    ('시설물의 안전 및 유지관리에 관한 특별법 시행령', 'fac_e', '시설물안전법 시행령',   '시설물법령'),
    ('시설물의 안전 및 유지관리에 관한 특별법 시행규칙', 'fac_r', '시설물안전법 시행규칙', '시설물법규칙'),
    ('건설산업기본법',                          'cib',   '건설산업기본법',           '건설산업기본법'),
    ('유해·위험작업의 취업 제한에 관한 규칙',     'haz',   '유해위험작업 취업제한규칙',  '취업제한규칙'),
]

# 별표를 가져올 법령.  (검색명, key)  — 원본 4법은 기존 key 재사용해 같은 필터에 묶음
BYL_TARGETS = [
    ('산업안전보건법', 'law'),
    ('산업안전보건법 시행령', 'enf'),
    ('산업안전보건법 시행규칙', 'rule'),
    ('산업안전보건기준에 관한 규칙', 'std'),
    ('중대재해 처벌 등에 관한 법률 시행령', 'sap_e'),
    ('건설기술 진흥법 시행령', 'ctp_e'),
    ('건설기술 진흥법 시행규칙', 'ctp_r'),
    ('시설물의 안전 및 유지관리에 관한 특별법 시행령', 'fac_e'),
    ('유해·위험작업의 취업 제한에 관한 규칙', 'haz'),
]

# 고시/행정규칙.  (검색명, key, 표시명, 필터라벨)
ADM_TARGETS = [
    ('건설업 산업안전보건관리비 계상 및 사용기준', 'cost', '안전보건관리비 고시', '안전관리비고시'),
    ('사업장 위험성평가에 관한 지침',              'risk', '위험성평가 지침',     '위험성평가'),
    ('안전보건교육규정',                          'edu',  '안전보건교육규정',    '교육규정'),
]


def get(url):
    for i in range(6):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=35).read().decode('utf-8', 'replace')
        except Exception:
            time.sleep(1.3)
    raise RuntimeError('fail ' + url)


def fmt_date(s):
    return '%s. %s. %s.' % (s[0:4], int(s[4:6]), int(s[6:8])) if len(s) == 8 and s.isdigit() else s


def txt(el):
    return ''.join(el.itertext())


def parse_article_text(text, lawKey, lawName, chapter):
    """'제N조(제목) 본문...' 한 덩어리 -> article dict (또는 장이면 (None, 새chapter))."""
    text = text.strip()
    if not text:
        return None, chapter
    mch = re.match(r'^(제\d+장(?:의\d+)?)\s+(.+)$', text)
    if mch and not re.match(r'^제\d+장.*?\(', text) and '조' not in text[:8]:
        return None, mch.group(1) + ' ' + mch.group(2).strip()
    ma = re.match(r'^제(\d+)조(?:의(\d+))?', text)
    if not ma:
        return None, chapter
    jo = int(ma.group(1)); sub = int(ma.group(2)) if ma.group(2) else 0
    label = '제%d조' % jo + (('의%d' % sub) if sub else '')
    mt = re.match(r'^제\d+조(?:의\d+)?\s*\(([^)]*)\)', text)
    title = mt.group(1).strip() if mt else ''
    body = re.sub(r'^제\d+조(?:의\d+)?\s*(\([^)]*\))?\s*', '', text, count=1).strip()
    body = re.sub(r'\n{3,}', '\n\n', body)
    return {'lawKey': lawKey, 'law': lawName, 'article': label, 'jo': jo, 'sub': sub,
            'chapter': chapter, 'title': title, 'body': body}, chapter


def parse_byeolpyo(root, lawKey, lawName):
    out = []
    for bu in root.iter('별표단위'):
        num = (bu.findtext('별표번호') or '').strip()
        gaji = (bu.findtext('별표가지번호') or '0').strip()
        gubun = (bu.findtext('별표구분') or '별표').strip()
        title = (bu.findtext('별표제목') or '').strip()
        content_el = bu.find('별표내용')
        body = txt(content_el).strip() if content_el is not None else ''
        body = re.sub(r'[ \t]+\n', '\n', body)
        body = re.sub(r'\n{3,}', '\n\n', body).strip()
        try:
            n = int(num)
        except ValueError:
            n = 0
        g = int(gaji) if gaji.isdigit() else 0
        label = '[%s %d%s]' % (gubun, n, ('의%d' % g if g else ''))
        if not body:
            body = '(표·서식형 ' + gubun + ' — 원문은 국가법령정보센터 첨부파일 참조) ' + title
        out.append({'lawKey': lawKey, 'law': lawName, 'article': label,
                    'jo': 90000 + n, 'sub': g, 'chapter': gubun,
                    'title': title or label, 'body': body})
    return out


def find_law_mst(name):
    q = urllib.parse.quote(name)
    root = ET.fromstring(get('https://www.law.go.kr/DRF/lawSearch.do?OC=%s&target=law&type=XML&display=20&query=%s' % (OC, q)))
    cands = []
    for law in root.findall('law'):
        cands.append(((law.findtext('법령명한글') or '').strip(),
                      (law.findtext('법령일련번호') or '').strip(),
                      (law.findtext('현행연혁코드') or '').strip()))
    cands = [c for c in cands if c[1]]
    exact = [c for c in cands if c[0] == name]
    pool = exact or cands
    cur = [c for c in pool if c[2] == '현행'] or pool
    return cur[0][1] if cur else None


def find_adm_id(name):
    q = urllib.parse.quote(name)
    root = ET.fromstring(get('https://www.law.go.kr/DRF/lawSearch.do?OC=%s&target=admrul&type=XML&display=20&query=%s' % (OC, q)))
    cands = []
    for a in root.findall('admrul'):
        cands.append(((a.findtext('행정규칙명') or '').strip(),
                      (a.findtext('행정규칙일련번호') or '').strip(),
                      (a.findtext('현행연혁구분') or '').strip()))
    cands = [c for c in cands if c[1]]
    exact = [c for c in cands if c[0] == name]
    pool = exact or cands
    cur = [c for c in pool if c[2] == '현행'] or pool
    return cur[0][1] if cur else None


def fetch_law(name, key, disp):
    mst = find_law_mst(name)
    if not mst:
        print('  !! law 검색 실패:', name); return [], ''
    root = ET.fromstring(get('https://www.law.go.kr/DRF/lawService.do?OC=%s&target=law&MST=%s&type=XML' % (OC, mst)))
    eff = fmt_date((root.findtext('.//시행일자') or '').strip())
    arts = []; chapter = ''
    for ju in root.iter('조문단위'):
        parts = [el.text.strip() for el in ju.iter() if el.tag.endswith('내용') and el.text and el.text.strip()]
        a, chapter = parse_article_text('\n'.join(parts), key, disp, chapter)
        if a:
            arts.append(a)
    return arts, eff


def fetch_adm(name, key, disp):
    aid = find_adm_id(name)
    if not aid:
        print('  !! admrul 검색 실패:', name); return [], '', []
    root = ET.fromstring(get('https://www.law.go.kr/DRF/lawService.do?OC=%s&target=admrul&ID=%s&type=XML' % (OC, aid)))
    eff = fmt_date((root.findtext('.//시행일자') or '').strip())
    arts = []; chapter = ''
    yn = (root.findtext('.//조문형식여부') or 'Y').strip()
    contents = [c for c in root.iter('조문내용')]
    if yn == 'Y':
        for c in contents:
            a, chapter = parse_article_text(txt(c), key, disp, chapter)
            if a:
                arts.append(a)
    if not arts:  # 비조문형 또는 파싱 실패 -> 전체를 단일 항목으로
        whole = '\n'.join(txt(c).strip() for c in contents).strip()
        if whole:
            arts.append({'lawKey': key, 'law': disp, 'article': '전문', 'jo': 1, 'sub': 0,
                         'chapter': '', 'title': disp, 'body': re.sub(r'\n{3,}', '\n\n', whole)})
    byl = parse_byeolpyo(root, key, disp)
    return arts, eff, byl


def fetch_byeolpyo_only(name, key, disp):
    mst = find_law_mst(name)
    if not mst:
        print('  !! 별표 대상 검색 실패:', name); return []
    root = ET.fromstring(get('https://www.law.go.kr/DRF/lawService.do?OC=%s&target=law&MST=%s&type=XML' % (OC, mst)))
    return parse_byeolpyo(root, key, disp)


def main():
    laws = []
    articles = []
    DISP = {}

    for name, key, disp, short in LAW_TARGETS:
        try:
            arts, eff = fetch_law(name, key, disp)
            articles.extend(arts)
            laws.append({'key': key, 'name': disp, 'short': short, 'eff': eff})
            DISP[key] = disp
            print('[법] %-22s %4d 조문 (시행 %s)' % (disp, len(arts), eff))
            time.sleep(0.4)
        except Exception as e:
            print('  !! 오류(법)', name, repr(e))

    for name, key, disp, short in ADM_TARGETS:
        try:
            arts, eff, byl = fetch_adm(name, key, disp)
            articles.extend(arts); articles.extend(byl)
            laws.append({'key': key, 'name': disp, 'short': short, 'eff': eff})
            DISP[key] = disp
            print('[고시] %-20s %4d 조문 + %d 별표 (시행 %s)' % (disp, len(arts), len(byl), eff))
            time.sleep(0.4)
        except Exception as e:
            print('  !! 오류(고시)', name, repr(e))

    # 별표 (원본 4법 포함). 표시명은 원본 매핑이 build_data 에서 처리되므로 임시 disp 사용
    BYL_DISP = {'law': '산업안전보건법', 'enf': '산업안전보건법 시행령',
                'rule': '산업안전보건법 시행규칙', 'std': '산업안전보건기준에 관한 규칙'}
    for name, key in BYL_TARGETS:
        try:
            disp = DISP.get(key) or BYL_DISP.get(key, name)
            byl = fetch_byeolpyo_only(name, key, disp)
            articles.extend(byl)
            print('[별표] %-26s %3d 건 (%s)' % (name, len(byl), key))
            time.sleep(0.4)
        except Exception as e:
            print('  !! 오류(별표)', name, repr(e))

    json.dump({'laws': laws, 'articles': articles},
              open('fetched_laws.json', 'w', encoding='utf-8'), ensure_ascii=False)
    print('TOTAL fetched articles:', len(articles), '-> fetched_laws.json')


if __name__ == '__main__':
    main()
