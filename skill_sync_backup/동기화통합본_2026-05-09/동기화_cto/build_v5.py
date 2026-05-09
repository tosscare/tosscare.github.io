"""
build_v5.py — 통합업무파일 v5 빌드
v4 골조 + 자료 컨텐츠 통합 (iframe srcdoc + <template> 박제)

작업:
1. 5 페르소나 × 4 자료 = 20 매핑 (cto-terms 제외 = 19 컨텐츠)
2. HTML 자료 (terms, worklog): 통째로 iframe srcdoc 용 박제
3. MD 자료 (workscope, summary): 마크다운 변환 + 통일 디자인 wrapping
4. <template id="tpl-{persona}-{datatype}"> 박제
5. JS 라우터 수정 (renderData → iframe 로드)
6. CSS 추가 (iframe 풀스크린)
"""
import re
import os
import html as htmlmod
from md_to_html import md_to_html


PERSONAS = [
    ('cto',       '개발총괄', 'cto'),
    ('claude',    '클로드',  '클로드'),
    ('toss',      '토스',   '토스'),
    ('outsource', '외주개발', '외주'),
    ('content',   '콘텐츠',  '콘텐츠'),
]

PERSONA_FOLDER = {
    'cto': '동기화_cto',
    'claude': '동기화_클로드',
    'toss': '동기화_토스',
    'outsource': '동기화_외주',
    'content': '동기화_콘텐츠',
}

DATA_TYPES = ['terms', 'workscope', 'summary', 'worklog']

# (persona, datatype) → 파일명 (없으면 None)
def get_file_path(pid, dtype):
    folder = PERSONA_FOLDER[pid]
    fname = next(p[2] for p in PERSONAS if p[0] == pid)
    if dtype == 'terms':
        path = f'../{folder}/terms_{fname}.html'
        return path if os.path.exists(path) else None
    if dtype == 'workscope':
        path = f'../{folder}/sync_{fname}.md'
        return path if os.path.exists(path) else None
    if dtype == 'summary':
        path = f'../{folder}/02_summary_{fname}.md'
        return path if os.path.exists(path) else None
    if dtype == 'worklog':
        path = f'../{folder}/worklog_{fname}.html'
        return path if os.path.exists(path) else None
    return None


# --- 마크다운 자료용 wrapping HTML (통일 디자인) ---
def md_wrapper(title, body_html):
    """마크다운 변환 결과를 통일 디자인의 완전한 HTML 문서로 감싼다 (iframe srcdoc 용)."""
    return f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{htmlmod.escape(title)}</title>
<style>
:root {{
  --c-bg: #f8fafc;
  --c-surface: #ffffff;
  --c-text: #1a202c;
  --c-text-2: #4a5568;
  --c-text-3: #718096;
  --c-border: #e2e8f0;
  --c-border-2: #cbd5e0;
  --c-primary: #1a365d;
  --c-primary-2: #2b6cb0;
  --c-accent: #ebf8ff;
  --c-code-bg: #edf2f7;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Pretendard', 'Noto Sans KR', 'Segoe UI', sans-serif;
  background: var(--c-bg);
  color: var(--c-text);
  line-height: 1.7;
  -webkit-font-smoothing: antialiased;
  font-size: 14px;
}}
body {{
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px 28px 80px;
}}
h1 {{
  font-size: 24px; font-weight: 800; color: var(--c-primary);
  border-bottom: 3px solid var(--c-primary); padding-bottom: 10px; margin-bottom: 18px;
  letter-spacing: -0.01em;
}}
h2 {{
  font-size: 18px; font-weight: 700; color: var(--c-primary-2);
  margin-top: 28px; margin-bottom: 12px;
}}
h3 {{
  font-size: 16px; font-weight: 700; color: var(--c-text);
  margin-top: 22px; margin-bottom: 10px;
}}
h4, h5, h6 {{
  font-size: 14px; font-weight: 700; color: var(--c-text-2);
  margin-top: 18px; margin-bottom: 8px;
}}
p {{ margin-bottom: 12px; color: var(--c-text); }}
a {{ color: var(--c-primary-2); text-decoration: underline; text-underline-offset: 2px; }}
a:hover {{ color: var(--c-primary); }}
strong {{ color: var(--c-text); font-weight: 700; }}
em {{ font-style: italic; color: var(--c-text-2); }}
code {{
  background: var(--c-code-bg); padding: 2px 6px; border-radius: 4px;
  font-family: 'SF Mono', Menlo, Consolas, monospace; font-size: 0.9em; color: #c53030;
}}
pre {{
  background: #1a202c; color: #e2e8f0; padding: 14px 16px; border-radius: 8px;
  overflow-x: auto; margin: 12px 0; font-size: 13px; line-height: 1.55;
}}
pre code {{ background: none; padding: 0; color: inherit; font-size: inherit; }}
blockquote {{
  background: var(--c-accent); border-left: 4px solid var(--c-primary-2);
  padding: 10px 14px; margin: 12px 0; border-radius: 0 6px 6px 0; color: var(--c-text-2);
}}
blockquote p:last-child {{ margin-bottom: 0; }}
ul, ol {{ margin: 10px 0 14px 24px; }}
li {{ margin-bottom: 4px; }}
hr {{ border: none; border-top: 1px solid var(--c-border-2); margin: 22px 0; }}
table {{
  border-collapse: collapse; width: 100%; margin: 12px 0;
  font-size: 13px; background: var(--c-surface);
  border-radius: 6px; overflow: hidden;
  box-shadow: 0 1px 2px rgba(0,0,0,0.03);
}}
th, td {{
  border: 1px solid var(--c-border); padding: 8px 12px;
  text-align: left; vertical-align: top;
}}
thead th {{ background: var(--c-accent); color: var(--c-primary); font-weight: 700; }}
tbody tr:nth-child(even) td {{ background: #fafbfc; }}
@media (max-width: 600px) {{
  body {{ padding: 16px 18px 60px; font-size: 13px; }}
  h1 {{ font-size: 20px; }}
  h2 {{ font-size: 16px; }}
  table {{ font-size: 12px; }}
  th, td {{ padding: 6px 8px; }}
}}
</style>
</head>
<body>
{body_html}
</body>
</html>'''


# --- HTML 파일 로드 (terms, worklog용 — 통째로 iframe srcdoc) ---
def load_html_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


# --- MD 파일 로드 + 변환 ---
def load_md_file(path, title):
    with open(path, 'r', encoding='utf-8') as f:
        md = f.read()
    body = md_to_html(md)
    return md_wrapper(title, body)


# --- "자료 없음" placeholder (cto-terms 등) ---
def empty_placeholder(persona_name, datatype_name, msg):
    body = f'''
<h1>{htmlmod.escape(persona_name)} · {htmlmod.escape(datatype_name)}</h1>
<blockquote>{htmlmod.escape(msg)}</blockquote>
'''
    return md_wrapper(f'{persona_name} {datatype_name}', body)


# --- 자료별 컨텐츠 생성 ---
def build_content(pid, dtype):
    persona_name = next(p[1] for p in PERSONAS if p[0] == pid)
    dtype_name = {
        'terms': '용어정의', 'workscope': '업무범위',
        'summary': '합의누적', 'worklog': '작업박제'
    }[dtype]
    title = f'{persona_name} · {dtype_name}'

    # cto의 terms는 자체 사전 ❌ (02_summary_cto.md 박제 사실)
    if pid == 'cto' and dtype == 'terms':
        return empty_placeholder(persona_name, dtype_name,
            '본 페르소나는 통합 메타 운용 전용으로, 자체 용어 사전이 없습니다. '
            '메타 룰 ⓐ~ⓤ는 instruction_cto.md §17을 참조하세요.')

    path = get_file_path(pid, dtype)
    if not path:
        return empty_placeholder(persona_name, dtype_name, '자료 파일이 없습니다.')

    if dtype in ('terms', 'worklog'):
        return load_html_file(path)
    else:  # workscope, summary
        return load_md_file(path, title)


# --- v4 골조 + template 박제 + JS 수정 ---
def build_v5():
    with open('통합업무파일_v4.html', 'r', encoding='utf-8') as f:
        v4 = f.read()

    # 모든 자료 컨텐츠 생성
    templates = []
    for pid, _, _ in PERSONAS:
        for dtype in DATA_TYPES:
            content = build_content(pid, dtype)
            tpl_id = f'tpl-{pid}-{dtype}'
            # <template> 안에 통째로 박제 (iframe srcdoc 용)
            # textContent로 박제 (innerHTML이 아닌 텍스트로 — </template> 충돌 방지)
            templates.append((tpl_id, content))

    # 1. <template> 들을 body 끝(</body> 직전)에 박제
    template_blocks = []
    for tpl_id, content in templates:
        # </template>은 안 나옴 (확인) — textContent 안전
        # 만약 있으면 escape 필요. 검증:
        if '</template>' in content.lower():
            raise ValueError(f'{tpl_id}: 자료에 </template> 포함 — escape 필요')
        # template 태그는 innerHTML 안에 그대로 두고, JS가 .innerHTML로 추출
        # 단, srcdoc 인자로 넘길 때 따옴표 escape 필요 → JS에서 처리
        # template 태그 내용은 그대로 보존
        template_blocks.append(
            f'<template id="{tpl_id}">{content}</template>'
        )
    template_html = '\n'.join(template_blocks)

    # 2. CSS 추가 (iframe 풀스크린)
    css_addon = '''
/* === 자료 iframe (3단 풀스크린) === */
#view-data .app-body { padding: 0; max-width: none; }
.app-data-iframe {
  display: block; width: 100%; height: calc(100vh - 56px);
  border: none; background: var(--c-bg);
}
.app-data-loading {
  display: flex; align-items: center; justify-content: center;
  height: calc(100vh - 56px); color: var(--c-text-3); font-size: 14px;
}
'''
    v5 = v4.replace('</style>', css_addon + '</style>', 1)

    # 3. JS 수정: renderData 함수가 iframe 로드하도록 수정
    old_render_data = '''  // ----- 렌더: 자료(3단) -----
  function renderData(personaId, dataTypeId) {
    const p = personasById[personaId];
    const dt = dataTypesById[dataTypeId];
    if (!p || !dt) return false;
    document.getElementById('data-title').textContent = `${p.name} · ${dt.name}`;
    document.getElementById('data-sub').textContent = dt.icon;
    // 자료 컨텐츠는 placeholder (다음 빌드에서 통합)
    return true;
  }'''
    new_render_data = '''  // ----- 렌더: 자료(3단) -----
  function renderData(personaId, dataTypeId) {
    const p = personasById[personaId];
    const dt = dataTypesById[dataTypeId];
    if (!p || !dt) return false;
    document.getElementById('data-title').textContent = `${p.name} · ${dt.name}`;
    document.getElementById('data-sub').textContent = dt.icon;
    // 자료 컨텐츠 — iframe srcdoc 로드 (자체 JS·CSS 100% 보존, 격리 100%)
    const container = document.getElementById('data-content');
    container.innerHTML = '<div class="app-data-loading">자료 로드 중...</div>';
    const tpl = document.getElementById(`tpl-${personaId}-${dataTypeId}`);
    if (!tpl) {
      container.innerHTML = '<div class="app-placeholder"><div class="app-placeholder__icon">⚠️</div><div class="app-placeholder__title">자료 없음</div><div class="app-placeholder__desc">해당 자료가 박제되지 않았습니다.</div></div>';
      return true;
    }
    // template.innerHTML = 박제된 완전한 HTML 문서 → iframe srcdoc 로 주입
    const iframe = document.createElement('iframe');
    iframe.className = 'app-data-iframe';
    iframe.setAttribute('title', `${p.name} ${dt.name}`);
    iframe.srcdoc = tpl.innerHTML;
    container.innerHTML = '';
    container.appendChild(iframe);
    return true;
  }'''
    if old_render_data not in v5:
        raise ValueError('renderData 원본 미발견 — 빌드 중단')
    v5 = v5.replace(old_render_data, new_render_data)

    # 4. <template> 들을 </body> 직전에 박제
    if '</body>' not in v5:
        raise ValueError('</body> 미발견 — 빌드 중단')
    v5 = v5.replace('</body>', f'\n{template_html}\n</body>')

    # 5. 출력
    with open('통합업무파일_v5.html', 'w', encoding='utf-8') as f:
        f.write(v5)

    return len(templates), len(v5)


if __name__ == '__main__':
    n_tpl, size = build_v5()
    print(f'✅ v5 빌드 완료')
    print(f'   - 박제된 자료: {n_tpl}종')
    print(f'   - 파일 크기: {size:,} bytes ({size/1024:.1f} KB)')
