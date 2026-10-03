import re

COMMIT_SOFT = 50
COMMIT_HARD = 72
PR_TITLE_MAX = 80
REQUIRED_SECTIONS = ['## Why', '## What', '## How to Test']


def validate_commit(text: str) -> str:
    """커밋 메시지 제목 길이 및 형식을 검증하고 필요시 후처리한다.

    Args:
        text (str): AI가 생성한 원본 커밋 메시지

    Returns:
        str: 길이 및 형식 검증이 완료된 커밋 메시지
    """
    lines = text.strip().splitlines()
    if not lines:
        return text

    title = lines[0].strip()
    if len(title) > COMMIT_HARD:
        print(f'[WARN] 커밋 제목 {len(title)}자 → {COMMIT_HARD}자로 자릅니다.')
        title = title[:COMMIT_HARD]
    elif len(title) > COMMIT_SOFT:
        print(f'[WARN] 커밋 제목이 {len(title)}자입니다. 50자 이내 권장.')

    return '\n'.join([title] + lines[1:])


def validate_pr(text: str) -> tuple[str, str]:
    """PR 제목 및 본문 형식을 검증하고 필수 섹션 및 불릿 구조를 보장한다.

    Args:
        text (str): AI가 생성한 원본 PR 초안 텍스트

    Returns:
        tuple[str, str]: (검증된 PR 제목, 검증된 PR 본문)
    """
    text = text.strip()

    # Extract TITLE: line
    m = re.search(r'^TITLE:\s*(.+)$', text, re.MULTILINE)
    if m:
        title = m.group(1).strip()
        body = text[m.end():].strip()
    else:
        # Fallback: first line as title
        parts = text.split('\n', 1)
        title = parts[0].strip()
        body = parts[1].strip() if len(parts) > 1 else ''

    if not title:
        title = 'feat: 변경 사항 반영'

    if len(title) > PR_TITLE_MAX:
        print(f'[WARN] PR 제목 {len(title)}자 → {PR_TITLE_MAX}자로 자릅니다.')
        title = title[:PR_TITLE_MAX]

    # 필수 섹션 존재 확인 및 누락 시 자동 보완 (후처리)
    missing = [s for s in REQUIRED_SECTIONS if s not in body]
    if missing:
        print(f'[WARN] PR 본문 필수 섹션 누락: {", ".join(missing)}')
        for s in missing:
            sec_name = s.replace('##', '').strip()
            body += f'\n\n{s}\n- {sec_name} 세부 사항 기술'

    # 각 섹션에 최소 1개 이상의 불릿(-) 포함 여부 검증 및 보정
    for s in REQUIRED_SECTIONS:
        # 섹션 헤더 위치 탐색
        idx = body.find(s)
        if idx != -1:
            # 다음 섹션 또는 텍스트 끝까지의 블록 추출
            next_idx = len(body)
            for other in REQUIRED_SECTIONS:
                if other != s:
                    o_idx = body.find(other, idx + len(s))
                    if o_idx != -1 and o_idx < next_idx:
                        next_idx = o_idx
            sec_block = body[idx + len(s):next_idx]
            if '-' not in sec_block and '*' not in sec_block:
                print(f'[WARN] {s} 섹션 내 불릿 누락 → 기본 불릿 항목 추가')
                body = (
                    body[:idx + len(s)]
                    + '\n- 세부 변경 내용 확인'
                    + body[idx + len(s):]
                )

    return title, body.strip()
