"""
md_to_html.py — 마크다운 → HTML minimal 변환기
외부 라이브러리 ❌. 본 시스템의 sync_X.md, 02_summary_X.md 변환용.
지원: 헤더(#~####), 표(GFM), 리스트(-/숫자), 코드블록(```), 인용(>), 구분선(---), 인라인(**bold**, *em*, `code`, [link](url))
"""
import re
import html as htmlmod


def _inline(s):
    # HTML 이스케이프 먼저
    s = htmlmod.escape(s)
    # 인라인 코드 (다른 마크다운 무력화 위해 가장 먼저)
    placeholders = []
    def stash_code(m):
        placeholders.append(f'<code>{m.group(1)}</code>')
        return f'\x00{len(placeholders)-1}\x00'
    s = re.sub(r'`([^`\n]+)`', stash_code, s)
    # 굵게 **bold**
    s = re.sub(r'\*\*([^*\n]+?)\*\*', r'<strong>\1</strong>', s)
    # 기울임 *em* (단, 단어 경계)
    s = re.sub(r'(?<![\w*])\*([^*\n]+?)\*(?![\w*])', r'<em>\1</em>', s)
    # 링크 [text](url)
    s = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
    # placeholder 복원
    s = re.sub(r'\x00(\d+)\x00', lambda m: placeholders[int(m.group(1))], s)
    # 줄바꿈 (단락 안의 단일 줄바꿈은 공백으로)
    return s


def _is_table_separator(line):
    """| --- | :---: | ---: | 형식 검증"""
    s = line.strip().strip('|').strip()
    if not s: return False
    cells = [c.strip() for c in s.split('|')]
    return all(re.fullmatch(r':?-{3,}:?', c) for c in cells if c)


def md_to_html(md):
    """마크다운 → HTML 변환. 입력은 문자열, 출력은 HTML 문자열."""
    if not md or not md.strip():
        return ''
    lines = md.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    out = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # 빈 줄
        if not stripped:
            i += 1
            continue

        # 코드 블록 ```
        if stripped.startswith('```'):
            lang = stripped[3:].strip()
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith('```'):
                buf.append(lines[i])
                i += 1
            i += 1  # 닫는 ``` 건너뛰기
            cls = f' class="lang-{htmlmod.escape(lang)}"' if lang else ''
            out.append(f'<pre><code{cls}>{htmlmod.escape(chr(10).join(buf))}</code></pre>')
            continue

        # 헤더 #~######
        m = re.match(r'^(#{1,6})\s+(.+)$', stripped)
        if m:
            level = len(m.group(1))
            out.append(f'<h{level}>{_inline(m.group(2).strip())}</h{level}>')
            i += 1
            continue

        # 구분선 --- 또는 ===
        if re.fullmatch(r'-{3,}|={3,}|\*{3,}', stripped):
            out.append('<hr>')
            i += 1
            continue

        # 표 (| 시작 + 다음 줄이 separator)
        if stripped.startswith('|') and i + 1 < n and _is_table_separator(lines[i + 1]):
            header = [c.strip() for c in stripped.strip('|').split('|')]
            i += 2  # 헤더 + separator 건너뛰기
            body_rows = []
            while i < n and lines[i].strip().startswith('|'):
                row = lines[i].strip()
                cells = [c.strip() for c in row.strip('|').split('|')]
                # 셀 개수 정합 (헤더 기준 보정)
                if len(cells) < len(header):
                    cells += [''] * (len(header) - len(cells))
                elif len(cells) > len(header):
                    cells = cells[:len(header)]
                body_rows.append(cells)
                i += 1
            tbl = ['<table>']
            tbl.append('<thead><tr>')
            for c in header:
                tbl.append(f'<th>{_inline(c)}</th>')
            tbl.append('</tr></thead>')
            tbl.append('<tbody>')
            for row in body_rows:
                tbl.append('<tr>')
                for c in row:
                    tbl.append(f'<td>{_inline(c)}</td>')
                tbl.append('</tr>')
            tbl.append('</tbody></table>')
            out.append(''.join(tbl))
            continue

        # 인용 >
        if stripped.startswith('>'):
            buf = []
            while i < n and lines[i].strip().startswith('>'):
                content = re.sub(r'^\s*>\s?', '', lines[i])
                buf.append(content)
                i += 1
            inner = md_to_html('\n'.join(buf))
            out.append(f'<blockquote>{inner}</blockquote>')
            continue

        # 리스트 - * +  또는 1. 2. 3.
        if re.match(r'^\s*[-*+]\s+', line) or re.match(r'^\s*\d+\.\s+', line):
            ordered = bool(re.match(r'^\s*\d+\.\s+', line))
            items = []
            while i < n and lines[i].strip() and (
                re.match(r'^\s*[-*+]\s+', lines[i]) or re.match(r'^\s*\d+\.\s+', lines[i])
            ):
                content = re.sub(r'^\s*(?:[-*+]|\d+\.)\s+', '', lines[i])
                items.append(f'<li>{_inline(content)}</li>')
                i += 1
            tag = 'ol' if ordered else 'ul'
            out.append(f'<{tag}>{"".join(items)}</{tag}>')
            continue

        # 단락 (다음 빈 줄까지 또는 다른 블록 시작까지)
        para_buf = []
        while i < n:
            cur = lines[i]
            cur_strip = cur.strip()
            if not cur_strip:
                break
            if (cur_strip.startswith('#') or cur_strip.startswith('```')
                or cur_strip.startswith('|') or cur_strip.startswith('>')
                or re.match(r'^\s*[-*+]\s+', cur) or re.match(r'^\s*\d+\.\s+', cur)
                or re.fullmatch(r'-{3,}|={3,}|\*{3,}', cur_strip)):
                break
            para_buf.append(cur_strip)
            i += 1
        if para_buf:
            out.append(f'<p>{_inline(" ".join(para_buf))}</p>')

    return '\n'.join(out)


if __name__ == '__main__':
    import sys
    print(md_to_html(sys.stdin.read()))
