# Mini Git

커밋 그래프(DAG)와 탐색·정렬·역색인을 직접 구현한 CLI 기반 미니 버전 관리 시스템.

## 실행

```bash
python main.py
```

Python 3.10 이상. 표준 라이브러리 외 의존성 없음.

## 시연

```bash
python demo.py
```

브랜치 분기와 병합이 있는 커밋 6개짜리 그래프를 만들고 모든 명령을 실행한다.
가짜 시계를 주입해 커밋 해시를 고정하므로 **실행할 때마다 같은 해시가 나온다** —
발표 자료의 그림과 화면 출력이 항상 일치한다.
(`main.py` 의 REPL 은 실제 시각을 쓰므로 매번 다른 해시가 나온다.)

```
97fc1d7  Initial commit      (Alice)
├── 8e798a0  Add login form      (Alice)   main
│   └── 8a825ba  Fix login bug   (Alice)   main
└── 1124123  Add payment API     (Bob)     feature
    └── eb3b7f6  Add payment tests (Bob)   feature

358996f  Merge branch 'feature' into main   부모 2개: 8a825ba, eb3b7f6
```

이 시나리오는 네 명령을 한 번에 보여주도록 설계했다.

- `LOG` — 브랜치가 갈라져 진입차수 0인 후보가 여러 개 생기므로 tie-break이 실제로 발동한다
- `PATH` — 루트에서 머지 커밋까지 길이 3짜리 최단 경로가 **두 개**라 사전순 규칙이 발동한다
- `SEARCH` — 작성자 2명, 공유 키워드(`add`, `login`, `payment`)가 겹치도록 메시지를 구성했다
- `MERGE` — 부모 2개인 커밋이 만들어진다

## 테스트

```bash
python run_tests.py             # 전체 186개
python run_tests.py -v          # 상세 출력
python -m unittest tests.test_graph -v   # 특정 모듈만
```

| 파일 | 대상 |
|---|---|
| `test_sorting.py` | merge_sort / insertion_sort / MinHeap / min_by, 안정성 |
| `test_graph.py` | 위상 정렬 / 조상 / BFS / 최단 경로 |
| `test_index.py` | 토큰화 / 인덱스 조회 / 순회 검색과의 동치성 |
| `test_repository.py` | INIT · BRANCH · SWITCH · COMMIT · LOG · PATH · ANCESTORS · SEARCH · MERGE |
| `test_cli.py` | 파싱 규칙 / 출력 문자열 / 표준 에러 메시지 |
| `test_diff.py` | LCS 줄 단위 비교 |
| `test_constraints.py` | 과제 제약(금지 API, 계층 분리, docstring) 정적 검사 |

### 검증 전략

**결정성 확보.** `Repository`는 시계를 주입받는다(`Repository(clock=...)`).
`datetime.now()`를 직접 호출하면 타임스탬프가 매번 달라져 커밋 해시도 달라지고,
결과값 일치를 검증할 수 없기 때문이다. 테스트는 `FakeClock`(1분씩 전진)과
`FixedClock`(항상 같은 시각)을 써서 같은 시나리오가 항상 같은 해시를 내게 한다.

**완전탐색 대조.** 정답이 자명하지 않은 두 알고리즘은 참조 구현과 맞춰본다.

- 위상 정렬: 무작위 DAG의 모든 유효한 위상 순서를 열거해, 결과가 그 안에
  있으면서 **사전순 최소**인지 확인
- 최단 경로: 모든 최단 경로를 만들어 사전순 최소를 고른 결과와 대조 (200건 이상)

**제약 사항 자동 검사.** `test_constraints.py`가 AST로 소스를 파싱해
`sorted()` / `list.sort()` 호출, `heapq`·`graphlib` 등 금지 모듈 import,
계층 위반(`graph.py`가 `Commit`을 참조하는지), docstring 누락을 잡는다.
정규식이 아니라 AST를 쓰는 이유는 "sorted()를 쓰지 않는다"고 적은 docstring
자체가 정규식에 걸리기 때문이다.

**돌연변이 검증.** 테스트가 실제로 결함을 잡는지 확인하기 위해, 구현을 일부러
14가지로 망가뜨려 테스트가 실패하는지 측정했다 — **14/14 탐지**. 예:

| 주입한 결함 | 실패한 테스트 |
|---|---|
| `merge_sort`의 `<=`를 `<`로 (안정성 파괴) | 2건 |
| 위상 정렬의 tie-break 제거 | 4건 |
| 최단 경로 탐욕 선택을 첫 후보로 | 2건 |
| 해시 입력에서 `sequence` 제외 | 1건 |
| `children` 역인덱스 갱신 누락 | 16건 |
| 검색 결과 정렬 제거 | 1건 |

## 프로젝트 구조

```
mini-git/
├── main.py              # 엔트리 포인트
├── README.md
├── demo.py              # 시연용 재현 가능 시나리오 (해시 고정)
├── run_tests.py         # 테스트 실행기
├── tests/               # 기능별 테스트 186개
│   ├── helpers.py       # 가짜 시계, 그래프 픽스처, 완전탐색 참조 구현
│   ├── test_sorting.py
│   ├── test_graph.py
│   ├── test_index.py
│   ├── test_repository.py
│   ├── test_cli.py
│   ├── test_diff.py
│   └── test_constraints.py
└── minigit/
    ├── models.py        # Commit (불변 노드)
    ├── errors.py        # 예외 계층 + 표준 에러 메시지
    ├── sorting.py       # merge_sort / insertion_sort / MinHeap / min_by
    ├── graph.py         # 위상 정렬, BFS, 조상 탐색, 최단 경로  ← Commit을 모름
    ├── index.py         # 역색인 (keyword / author)
    ├── diff.py          # 보너스: LCS 기반 줄 단위 diff
    ├── repository.py    # 저장소 상태 + 명령 (위 모듈들을 조합)
    ├── formatter.py     # 출력 포맷
    └── cli.py           # 파서 + REPL
```

### 계층 분리 원칙

`graph.py`는 `Commit`을 import하지 않는다. 노드는 문자열이고 간선은
`parents_of` / `children_of` 콜백으로만 주어진다.

- 알고리즘을 저장소 상태에서 독립시켜 단위 테스트가 가능해진다
- "Git이 그래프다"가 아니라 "그래프 위에 Git을 얹었다"는 관계가 코드로 드러난다

`sorting.py`도 마찬가지로 도메인을 모른다. 비교 기준은 전부 `key` 인자로 주입된다.

## 명령어

| 명령 | 설명 |
|---|---|
| `INIT <user_name>` | 저장소 초기화, `main` 브랜치 생성, HEAD/작성자 설정 |
| `USER <user_name>` | (확장) 현재 작성자 변경 |
| `BRANCH <branch_name>` | 현재 HEAD를 가리키는 브랜치 생성 |
| `SWITCH <branch_name>` | HEAD를 해당 브랜치로 이동 |
| `COMMIT <message>` | 현재 HEAD를 부모로 커밋 생성 + 역색인 갱신 |
| `MERGE <branch_name>` | (보너스) 부모 2개인 merge commit 생성 |
| `LOG` | **위상 정렬** — 부모가 항상 자식보다 먼저 |
| `LOG --sort-by=date\|author` | **전체 정렬** — 지정한 비교 기준으로 정렬 |
| `PATH <c1> <c2>` | 두 커밋 사이 최단 경로 (없으면 `No path`) |
| `ANCESTORS <hash>` | 도달 가능한 모든 조상 |
| `SEARCH <keyword>` | 메시지 키워드 검색 (역색인) |
| `SEARCH --author=<name>` | 작성자 검색 (역색인) |
| `DIFF <f1> <f2>` | (보너스) 두 텍스트 파일 줄 단위 비교 |
| `BENCH <n>` | (보너스) merge_sort vs insertion_sort 실행 시간 비교 |
| `HELP` / `EXIT` / `QUIT` | 도움말 / 종료 |

`USER`는 명세에 없는 확장이다. `INIT`이 작성자를 한 번만 정하면 세션 내
작성자가 하나뿐이라 `SEARCH --author`와 `LOG --sort-by=author`를 실제로
검증할 수 없어서 추가했다.

명령어는 대소문자를 구분하지 않는다. 공백이 포함된 인자는 따옴표로 감싼다.
커밋 해시는 접두사(짧은 해시)로도 지정할 수 있으며, 후보가 둘 이상이면
`Ambiguous commit: <ref>`로 거부한다.

### 표준 에러 메시지

`errors.py` 한 곳에서 관리한다.

```
Invalid args
Invalid args: <detail>
Repository is not initialized
Unknown branch: <name>
Unknown commit: <hash>
Ambiguous commit: <ref>
Branch already exists: <name>
Unknown command: <name>
Commit graph contains a cycle
```

## 실행 예시

```
mini-git> init "Alice"
Initialized repository.
Current branch: main
Current user: Alice

mini-git> commit "Initial commit"
[main dd26577] Initial commit

mini-git> branch feature
Created branch: feature

mini-git> switch feature
Switched to branch: feature

mini-git> commit "Add login feature"
[feature 5791258] Add login feature

mini-git> switch main
Switched to branch: main

mini-git> commit "Add payment feature"
[main b7741d2] Add payment feature

mini-git> log
commit dd26577 (Alice, 2026-08-20 09:22:57)
    Initial commit
commit 5791258 (Alice, 2026-08-20 09:22:57) [feature]
    Add login feature
commit b7741d2 (Alice, 2026-08-20 09:22:57) [main]
    Add payment feature

mini-git> path 5791258 b7741d2
Path: 5791258 -> dd26577 -> b7741d2

mini-git> search "login"
Found 1 commit:

- 5791258: Add login feature

mini-git> merge feature
[main 2ee6a6f] Merge branch 'feature' into main
```

---

# 과제 목표에 대한 답변

## 1. 커밋 그래프는 왜 DAG인가

**방향성(Directed):** 커밋은 자기 부모의 해시를 필드로 가진다. 반대로 부모는
자식을 모른다. 자식이 만들어지는 시점에 부모는 이미 존재하고 불변이기 때문이다.
따라서 간선에는 자식 → 부모라는 방향이 내재해 있다.

**비순환(Acyclic):** 커밋 해시는 부모 해시를 포함한 내용으로부터 계산된다.
어떤 커밋이 자기 자손을 부모로 가지려면 아직 존재하지 않는 해시를 미리
알아야 하므로 사이클을 만들 수 없다. 이 프로젝트에서는 부모가 항상 "현재 HEAD",
즉 이미 저장소에 존재하는 커밋이므로 **구조적으로** 사이클이 생기지 않는다.

**트리가 아닌 이유:** merge 커밋은 부모를 2개 가진다. 즉 서로 다른 두 경로가
한 노드로 다시 합쳐진다. 트리는 노드마다 부모가 최대 1개이므로 이 구조를
표현할 수 없다. 반대로 브랜치는 한 부모에서 자식이 여러 개 갈라지는 것이다.
분기와 병합이 모두 가능한 구조가 DAG다.

구현상 이 성질은 `Commit`을 `frozen=True` + `parents: tuple`로 불변화해
런타임에 간선이 추가되는 사고를 타입 수준에서 차단하는 것으로 보강했다.
`topological_order`의 사이클 검사(`CycleError`)는 그 불변식에 대한 안전망이다.

## 2. "부모가 먼저 출력되는 로그"에 필요한 접근

시간순 정렬로는 안 된다. 정렬은 전순서(total order)를 만들지만, 커밋 그래프가
요구하는 건 **부분순서(partial order)** 이기 때문이다. 서로 다른 브랜치의 두
커밋 사이에는 "먼저"라는 관계 자체가 정의되지 않는다.

필요한 것은 **위상 정렬**이다. Kahn 알고리즘을 사용했다.

1. 각 커밋의 진입차수 = 부모 수
2. 진입차수 0인 커밋(부모 없는 최초 커밋)을 후보에 넣는다
3. 후보에서 하나 꺼내 출력하고, 그 자식들의 진입차수를 1 감소
4. 0이 된 자식을 후보에 추가, 후보가 빌 때까지 반복

**동률(tie-break) 문제:** 브랜치가 갈라진 뒤로는 진입차수 0인 후보가 동시에
여러 개가 된다. 즉 위상 정렬의 답이 하나가 아니다. 아무거나 고르면 실행할
때마다 출력이 달라진다. 그래서 후보들 중 **해시 사전순으로 최소인 것**을
고정 선택한다.

`--sort-by` 쪽에서도 동률이 생기면 `sequence`(생성 순번)로 확정한다.
`sequence`는 세션 내 단조 증가하므로 언제나 유일한 순서를 만든다.

**이것이 이 프로젝트에서 정렬이 하는 또 하나의 역할이다** — 표시 순서를
바꾸는 것뿐 아니라, 답이 여러 개인 지점에서 항상 같은 답을 고르게 만드는
결정성 확보.

### `LOG`와 `LOG --sort-by`는 다른 명령이다

명세는 위상 제약을 `LOG` 항목에만 걸었고, `--sort-by`는 별도 항목에서
"timestamp 기준으로 정렬 / 작성자 이름 기준으로 정렬"이라고만 규정한다.
따라서 `--sort-by`는 위상 순서 안의 tie-break이 아니라 **위상 순서를 대체하는
전체 정렬**로 구현했다.

이 구분 자체가 학습 포인트다. 두 옵션의 결과가 대칭이 아니기 때문이다.
무작위 시나리오 200개(브랜치 최대 20개, 작성자 4명)에서 측정한 결과:

| 명령 | "부모가 자식보다 먼저" 위반 |
|---|---|
| `LOG` | **0 / 200** |
| `LOG --sort-by=date` | **0 / 200** |
| `LOG --sort-by=author` | **200 / 200** |

- **`date`가 우연히 통과하는 이유:** 부모는 언제나 자식보다 먼저 생성되므로
  timestamp가 커밋 그래프의 방향과 단조 일치한다. 이 시스템에서 날짜순은
  가능한 위상 순서 중 하나다. 즉 **정렬 기준이 그래프 구조와 상관있을 때만**
  우연히 성립한다.
- **`author`가 항상 깨지는 이유:** 작성자 이름은 그래프 구조와 아무 관계가
  없다. 정렬은 전순서(total order)를 만들지만 커밋 그래프가 요구하는 건
  부분순서(partial order)라서, 무관한 기준으로 전순서를 강제하면 부모-자식
  관계가 무너진다.

**이것이 "왜 LOG는 정렬이 아니라 위상 정렬이어야 하는가"에 대한 실증이다.**
날짜순만 보면 정렬로 충분해 보이지만, 그건 우연이지 보장이 아니다.

구현상 `Repository.is_parent_first()`로 이를 검사하고, `--sort-by` 결과가
제약을 깨뜨렸을 때 CLI가 안내 문구를 덧붙인다.

```
mini-git> log --sort-by=author
commit 18544d3 (Alice, ...) [feature]
    Add login feature
commit 0733c8a (Bob, ...) [main]
    Add payment feature
commit 49c51f0 (Zoe, ...)
    Initial commit

(note: this order is sorted by author, so a parent may appear after its
child. use plain LOG for parent-first order.)
```

루트 커밋(Zoe)이 자기 자손들보다 뒤에 출력된 것을 확인할 수 있다.

**자료구조 선택:** 후보 집합을 리스트로 두고 매 반복 재정렬하면
O(V² log V)이고 `pop(0)`도 O(V)다. **최소 힙**(직접 구현, `sorting.MinHeap`)을
쓰면 O((V + E) log V)로 떨어진다.

## 3. 최단 경로와 조상 탐색

### PATH — 사전순 최소 최단 경로

부모-자식 간선을 **무방향**으로 보므로, 가중치가 모두 1인 그래프의 최단 경로
문제다. 따라서 BFS로 충분하다(다익스트라는 과잉).

최단 경로가 여러 개일 때 사전순 최소를 고르기 위해 2단계로 나눴다.

1. **target에서** BFS를 돌려 거리 테이블 `dist`를 만든다.
   무방향이므로 `dist(target, x) == dist(x, target)`이다.
2. start에서 출발해, 이웃 중 `dist`가 정확히 1 작은 것들만 후보로 남긴다.
   (이들은 반드시 어떤 최단 경로 위에 있다) 그중 해시가 최소인 것을 고른다.
   target에 닿을 때까지 반복.

**탐욕 선택의 정당성:** 모든 해시 길이가 같으므로(sha1 40자) 경로 문자열의
사전순 비교는 각 자리 해시를 앞에서부터 비교하는 것과 동치다. 따라서 앞에서부터
매 단계 최소를 고르면 전체가 최소가 된다. **해시 길이가 가변이면 이 논증은
성립하지 않는다.**

시간복잡도 O(V + E), 공간복잡도 O(V).

무작위 그래프 1,600건에 대해 완전탐색 결과와 대조해 전건 일치를 확인했다.

### ANCESTORS

부모 방향으로만 도달 가능한 노드를 전부 모으는 도달 가능성 문제다.
BFS로 구현했다.

**재귀 대신 반복을 쓴 이유:** 커밋 히스토리는 본질적으로 긴 사슬이라 깊이가
수천이 되기 쉽다. 재귀 DFS는 파이썬 기본 재귀 한계(약 1000)에서
`RecursionError`가 난다. 깊이 3000짜리 히스토리로 검증했다.
BFS는 부수적으로 "가까운 조상부터"라는 세대순 결과를 준다.

시간복잡도 O(V + E) — `visited` 집합 덕분에 각 노드/간선을 최대 한 번만 본다.

## 4. 정렬 알고리즘

`sorted()`, `list.sort()`를 일절 사용하지 않았다.

| 알고리즘 | 최선 | 평균 | 최악 | 공간 | 안정성 |
|---|---|---|---|---|---|
| `merge_sort` | O(n log n) | O(n log n) | O(n log n) | O(n) | **안정** |
| `insertion_sort` | O(n) | O(n²) | O(n²) | O(1) | **안정** |
| `MinHeap` push/pop | — | O(log n) | O(log n) | O(n) | — |

**merge_sort가 항상 O(n log n)인 이유:** 입력 분포와 무관하게 매번 정확히
절반으로 쪼개기 때문에 퀵소트 같은 최악 케이스가 없다. 대신 병합용 임시 배열이
필요해 공간이 O(n)이다.

**안정성의 근거:** `_merge()`에서 동률일 때 `<=` 비교로 **왼쪽을 먼저** 취한다.
`<`로 바꾸면 오른쪽이 먼저 나가면서 원래 순서가 뒤집혀 불안정 정렬이 된다.
`LOG --sort-by=author`에서 같은 작성자의 커밋들이 원래 순서를 유지하는 것이
이 성질 덕분이다.

**비교 기준 교체:** 모든 정렬 함수가 `key: Callable` 인자를 받는다. 정렬
로직은 그대로 두고 기준만 주입한다.

**`min_by`:** 최단 경로의 다음 후보를 고를 때는 정렬 결과 전체가 아니라 첫
원소만 필요하다. 전체 정렬 O(k log k) 대신 O(k) 선형 스캔으로 처리했다.

`BENCH <n>` 명령으로 두 알고리즘의 실측 시간을 비교할 수 있다.

## 5. 역색인은 왜 순회 검색보다 빠른가

커밋 N개, 메시지 평균 토큰 M개, 결과 K개라고 하자.

| 방식 | 검색 1회 | 커밋 1회 | 공간 |
|---|---|---|---|
| 전체 순회 | **O(N × M)** | O(1) | O(N) |
| 역색인 | **O(1) + O(K)** | O(M) | O(N × M) |

핵심은 **검색 시점의 비용을 커밋 시점으로 옮긴 것**이다. 커밋할 때 메시지를
토큰으로 쪼개 `keyword -> {commit_hash}` 해시맵에 미리 넣어둔다. 검색은
해시맵 조회 한 번이므로 커밋이 100만 개로 늘어도 조회 비용은 그대로다.
결과를 담는 데 필요한 O(K)만 남는다.

즉 전형적인 **space-time trade-off**다. 저장 공간을 O(N × M)으로 늘리는 대신
검색을 상수 시간으로 만든다. 실제 Git의 `git grep --cached`나 검색 엔진의
색인이 같은 원리다.

**두 종류의 인덱스:**
- `keyword_to_hashes`: 메시지 토큰 → 커밋 해시 집합
- `author_to_hashes`: 작성자(소문자) → 커밋 해시 집합

**토큰화:** 최소 기준(공백 `split` + `lower`)에 더해 양끝 구두점을 제거한다.
`"Add login feature."`로 커밋했을 때 `search feature`가 실패하는 문제를 막기
위해서다.

**결정성 주의:** 인덱스 값이 `set`이라 순회 순서가 보장되지 않는다. 그대로
출력하면 같은 명령의 결과 순서가 실행마다 달라질 수 있으므로, 반환 직전에
`merge_sort`로 `sequence` 기준 정렬해 고정했다.

---

## 커밋 해시 유일성

해시 입력에 `sequence`(생성 순번)를 포함시킨다.

```
message:<message>
author:<author>
timestamp:<isoformat>
parents:<h1,h2>
sequence:<n>
```

`timestamp`만으로는 같은 사용자가 같은 메시지로 같은 순간에 커밋할 때 충돌
가능성이 남는다. `sequence`는 세션 내에서 단조 증가하므로 다른 필드가 전부
같아도 해시가 갈린다. 깊이 3000 히스토리에서 충돌 없음을 확인했다.

## 제약 사항 준수

- 그래프 전용 라이브러리 미사용 (`collections.deque`만 큐 용도로 사용)
- `sorted()` / `list.sort()` / `heapq` 미사용 — 정렬과 힙 모두 직접 구현
- 알고리즘 로직을 `graph.py` / `sorting.py` / `index.py`로 분리
- 모든 주요 함수·클래스에 docstring 작성
- 파일 내용 추적 / 네트워크 / 영속성 미구현 (메모리 상 동작)