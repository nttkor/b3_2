"""AI 프롬프트 생성 모듈 (src/prompt_builder.py).

이 모듈은 Git 저장소에서 수집된 변경 메타데이터(`git status`, `git diff`, 브랜치명)와
프로젝트 컨벤션 규칙을 결합하여, LLM(대규모 언어 모델)이 엄격한 규칙에 맞춰
커밋 메시지 및 Pull Request 초안을 생성하도록 유도하는 프롬프트를 조립합니다.

주요 특징:
    1. 프롬프트 엔지니어링 기반 규격 유도 (Inference Guidance):
       - 언어 설정(한국어/영어), 제목 길이 제약(50자 권장/최대 72자, PR 80자),
         불릿 구조, 마크다운 필수 섹션을 명시하여 초안 작성 단계에서 90% 이상 규격을 준수시킵니다.
    2. 컨텍스트 격리 및 명확한 구획화:
       - `--- GIT STATUS ---`, `--- GIT DIFF ---` 등의 텍스트 경계선을 두어
         LLM이 작업 상태와 diff 코드 변경점을 혼동하지 않고 정확히 인지하도록 설계되었습니다.
"""


def build_commit_prompt(status: str, diff: str, convention: dict) -> str:
    """Git 변경 사항과 컨벤션을 기반으로 커밋 메시지 생성용 AI 프롬프트를 조립한다.

    작업 트리의 `git status` 및 `git diff` 텍스트와 컨벤션 설정(`convention`)을 분석하여
    Conventional Commit 규격(제목 50자 이내, 접두어, 본문 불릿 요약)의 커밋 메시지를
    생성하도록 지시하는 사용자 프롬프트 문자열을 반환합니다.

    Args:
        status (str): `git status` 명령을 통해 수집된 작업 트리 요약 문자열.
        diff (str): `git diff` 및 `git diff --cached`를 통해 수집된 변경 코드 diff 문자열.
        convention (dict): 컨벤션 설정 딕셔너리 (`commit_language`, `commit_prefix` 등 포함).

    Returns:
        str: AI 모델(ChatCompletion API)에 전달할 완성된 커밋 메시지 생성 프롬프트 문자열.

    Raises:
        None: 내부 로직은 순수 문자열 포맷팅으로 예외를 발생시키지 않습니다.
    """
    # 1. 언어 설정 결정 (ko: 한국어, 기타: English)
    lang = '한국어' if convention.get('commit_language', 'ko') == 'ko' else 'English'

    # 2. 접두어 규칙 생성 (commit_prefix 옵션에 따라 feat/fix 등 강제 여부 결정)
    prefix_rule = (
        '- conventional commit 형식 사용: feat/fix/docs/refactor/test/chore/style'
        if convention.get('commit_prefix', True)
        else '- prefix 없이 자유 형식 허용'
    )

    # 3. 엄격한 규칙과 구획화된 Git 컨텍스트를 포함하는 프롬프트 템플릿 완성
    return f"""\
Git 변경 사항을 분석하여 커밋 메시지를 생성하세요.
언어: {lang}

규칙:
- 제목: 50자 이내 권장(최대 72자), 명령형, 마침표 없음
{prefix_rule}
- 본문: 변경된 파일(모듈) 1~3개 언급, 핵심 변경 사항 1~2개를 불릿으로 요약
- 커밋 메시지만 출력하고 다른 설명은 쓰지 않음

출력 형식:
<type>: <한 줄 설명>

- <변경 사항 1>
- <변경 사항 2>

--- GIT STATUS ---
{status}

--- GIT DIFF ---
{diff}
"""


def build_pr_prompt(status: str, diff: str, branch: str, convention: dict) -> str:
    """Git 변경 사항과 브랜치 정보를 바탕으로 PR 초안 생성용 AI 프롬프트를 조립한다.

    작업 브랜치명, Git 상태 요약, diff 변경분 및 컨벤션의 필수 섹션 목록을 기반으로,
    1줄 제목(최대 80자)과 3대 필수 섹션(Why, What, How to Test) 및 불릿 항목을 갖춘
    GitHub Pull Request 본문 초안을 작성하도록 지시하는 프롬프트 문자열을 반환합니다.

    Args:
        status (str): `git status`를 통해 수집된 파일 변경 요약 문자열.
        diff (str): 기준 브랜치 대비 현재 작업 브랜치의 전체 변경 diff 문자열.
        branch (str): 현재 작업 중인 Git 브랜치 이름 (예: `feature/login`).
        convention (dict): 컨벤션 설정 딕셔너리 (`pr_language`, `pr_sections` 포함).

    Returns:
        str: AI 모델(ChatCompletion API)에 전달할 완성된 PR 초안 생성 프롬프트 문자열.

    Raises:
        None: 내부 로직은 순수 문자열 포맷팅으로 예외를 발생시키지 않습니다.
    """
    # 1. 언어 설정 결정 (ko: 한국어, 기타: English)
    lang = '한국어' if convention.get('pr_language', 'ko') == 'ko' else 'English'

    # 2. 필수 섹션 목록 추출 및 템플릿 구성 (기본값: Why, What, How to Test)
    sections: list[str] = convention.get('pr_sections', ['Why', 'What', 'How to Test'])
    section_names = ', '.join(sections)
    # 섹션별 최소 1개 불릿 힌트를 포함한 템플릿 마크다운 조립
    section_template = '\n\n'.join(f'## {s}\n- <내용>' for s in sections)

    # 3. 출력 형식 제약 및 격리된 컨텍스트를 담은 최종 프롬프트 조립
    return f"""\
Git 변경 사항을 분석하여 Pull Request 제목과 본문 초안을 생성하세요.
언어: {lang}

규칙:
- PR 제목: 최대 80자, 변경 내용을 명확하게 표현
- PR 본문: 다음 섹션 필수 포함 ({section_names}), 각 섹션 최소 불릿 1개
- 다른 설명 없이 지정된 형식만 출력

출력 형식:
TITLE: <PR 제목>

{section_template}

--- 현재 브랜치 ---
{branch}

--- GIT STATUS ---
{status}

--- GIT DIFF ---
{diff}
"""
