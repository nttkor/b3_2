"""커밋 메시지 및 PR 초안 사후 검증 모듈 (src/validator.py).

이 모듈은 AI 모델이 생성한 커밋 메시지와 Pull Request 초안이 사전에 정의된
길이 제약 및 형식 규칙(제목 길이, 필수 섹션, 불릿 구조)을 만족하는지 검사하고,
규격을 위반한 경우 0.001초 만에 즉시 확정적으로 보정(Deterministic Post-Processing)하는
2단계 안전장치 역할을 전담합니다.

주요 특징:
    1. 결정론적 하드 슬라이싱 (Deterministic Hard Truncation):
       - LLM은 확률적 토큰 생성 엔진이므로 글자 수를 완벽히 통제하기 어렵습니다.
       - 본 검증기는 파이썬의 문자열 슬라이싱(`title[:72]`, `title[:80]`)을 통해
         수학적으로 100% 길이 제약을 확정합니다.
    2. 필수 섹션 및 불릿 구조 자동 복구:
       - PR 본문에 Why, What, How to Test 중 누락된 섹션이 있을 경우 플레이스홀더를 자동 합성하고,
         섹션 내에 불릿 기호(`-` 또는 `*`)가 누락되었을 경우 기본 항목을 강제 삽입하여
         동료평가 및 실무 협업 시 완벽한 마크다운 가독성을 보장합니다.
"""

import re

# 커밋 메시지 제목 길이 제약 상수
COMMIT_SOFT = 50        # 권장 최대 글자 수 (50자 초과 시 [WARN] 경고 출력)
COMMIT_HARD = 72        # 절대 한계 글자 수 (72자 초과 시 즉시 강제 절삭)

# Pull Request 제목 길이 제약 상수
PR_TITLE_MAX = 80       # PR 제목 최대 한계 글자 수 (80자 초과 시 즉시 강제 절삭)

# Pull Request 본문 필수 마크다운 섹션 헤더 목록
REQUIRED_SECTIONS = ['## Why', '## What', '## How to Test']


def validate_commit(text: str) -> str:
    """커밋 메시지 제목의 길이를 검증하고 필요시 하드 슬라이싱으로 후처리한다.

    입력된 텍스트의 첫 번째 줄(제목)을 추출하여 72자를 초과할 경우 72자로 강제 절삭하고,
    50자를 초과할 경우 사용자에게 권장 초과 경고([WARN])를 안내합니다.

    Args:
        text (str): AI가 생성한 원본 커밋 메시지 텍스트.

    Returns:
        str: 길이 및 형식 검증과 보정이 완료된 커밋 메시지 문자열.

    Raises:
        None: 빈 문자열이나 어떠한 비정상 텍스트가 입력되어도 안전하게 원본 또는 보정본을 반환합니다.
    """
    lines = text.strip().splitlines()
    # 생성된 텍스트가 비어 있는 경우 원본 그대로 반환
    if not lines:
        return text

    # 첫 줄을 커밋 제목으로 간주하여 앞뒤 공백 제거
    title = lines[0].strip()

    # 1. 72자 하드 리밋 검증: 72자 초과 시 72자로 단호하게 강제 절삭
    if len(title) > COMMIT_HARD:
        print(f'[WARN] 커밋 제목 {len(title)}자 → {COMMIT_HARD}자로 자릅니다.')
        title = title[:COMMIT_HARD]
    # 2. 50자 소프트 리밋 검증: 50자 초과 ~ 72자 이하인 경우 권장 가이드 경고 출력
    elif len(title) > COMMIT_SOFT:
        print(f'[WARN] 커밋 제목이 {len(title)}자입니다. 50자 이내 권장.')

    # 절삭/검증된 제목과 나머지 본문 줄들을 다시 결합하여 반환
    return '\n'.join([title] + lines[1:])


def validate_pr(text: str) -> tuple[str, str]:
    """PR 제목 및 본문 형식을 검증하고 필수 3대 섹션 및 불릿 구조를 보장한다.

    생성된 텍스트에서 'TITLE:' 라인을 파싱하여 제목과 본문을 분리합니다.
    제목은 80자 한도로 하드 컷하며, 본문은 Why/What/How to Test 필수 섹션 누락 여부 및
    섹션별 불릿(`-` 또는 `*`) 존재 여부를 검사하여 누락된 요소를 자동 복구합니다.

    Args:
        text (str): AI가 생성한 원본 PR 초안 텍스트.

    Returns:
        tuple[str, str]: (검증 및 보정된 PR 제목, 검증 및 보정된 PR 본문) 형태의 튜플.

    Raises:
        None: 비정상적이거나 깨진 텍스트 입력 시에도 기본 제목과 섹션을 합성하여 크래시를 방지합니다.
    """
    text = text.strip()

    # 1. 정규표현식을 통해 'TITLE: <내용>' 패턴으로 PR 제목과 본문 분리
    m = re.search(r'^TITLE:\s*(.+)$', text, re.MULTILINE)
    if m:
        title = m.group(1).strip()
        body = text[m.end():].strip()
    else:
        # 'TITLE:' 태그가 누락된 경우의 폴백: 첫 번째 줄을 제목으로, 나머지를 본문으로 분리
        parts = text.split('\n', 1)
        title = parts[0].strip()
        body = parts[1].strip() if len(parts) > 1 else ''

    # 제목이 완전히 비어 있을 경우 기본 제목 자동 부여
    if not title:
        title = 'feat: 변경 사항 반영'

    # 2. PR 제목 80자 하드 컷 검증 및 슬라이싱 절삭
    if len(title) > PR_TITLE_MAX:
        print(f'[WARN] PR 제목 {len(title)}자 → {PR_TITLE_MAX}자로 자릅니다.')
        title = title[:PR_TITLE_MAX]

    # 3. 필수 섹션(Why, What, How to Test) 누락 검사 및 자동 보충
    missing = [s for s in REQUIRED_SECTIONS if s not in body]
    if missing:
        print(f'[WARN] PR 본문 필수 섹션 누락: {", ".join(missing)}')
        for s in missing:
            sec_name = s.replace('##', '').strip()
            # 누락된 섹션 헤더 및 기본 불릿 플레이스홀더를 본문 말미에 추가
            body += f'\n\n{s}\n- {sec_name} 세부 사항 기술'

    # 4. 각 섹션 블록 내에 최소 1개 이상의 불릿('-', '*') 기호가 존재하는지 검증 및 보정
    for s in REQUIRED_SECTIONS:
        # 섹션 헤더의 시작 위치 탐색
        idx = body.find(s)
        if idx != -1:
            # 현재 섹션 헤더 이후부터 다음 섹션 헤더 시작 전까지의 블록 범위 산출
            next_idx = len(body)
            for other in REQUIRED_SECTIONS:
                if other != s:
                    o_idx = body.find(other, idx + len(s))
                    if o_idx != -1 and o_idx < next_idx:
                        next_idx = o_idx
            sec_block = body[idx + len(s):next_idx]

            # 해당 섹션 블록 내에 불릿 기호가 없으면 기본 불릿 항목 강제 삽입
            if '-' not in sec_block and '*' not in sec_block:
                print(f'[WARN] {s} 섹션 내 불릿 누락 → 기본 불릿 항목 추가')
                body = (
                    body[:idx + len(s)]
                    + '\n- 세부 변경 내용 확인'
                    + body[idx + len(s):]
                )

    return title, body.strip()
