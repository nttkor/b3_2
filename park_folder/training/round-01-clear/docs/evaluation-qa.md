# B3-2 R01 — Evaluation Q&A Reference

## 1. Git commit graph가 왜 DAG인가?

commit은 과거 parent를 가리키고 새 commit은 기존 commit을 부모로 만들어집니다. 정상 생성 흐름에서는 미래 commit을 부모로 가리키지 않으므로 parent 방향을 따라가다 현재 commit으로 되돌아오는 cycle이 없어야 합니다. cycle이 생기면 ancestor 탐색과 parent-first LOG의 의미가 깨지고 무한 순환 위험도 생깁니다.

## 2. branch를 pointer로 이해하면 무엇이 달라지는가?

branch 생성은 commit 전체를 복사하는 작업이 아니라 현재 HEAD commit hash를 가리키는 새 이름을 만드는 작업입니다. SWITCH는 `head_branch`가 어떤 branch pointer를 사용할지 바꾸고, COMMIT은 새 node를 만든 뒤 현재 branch pointer를 새 hash로 이동시킵니다.

## 3. commit 저장소/branch/HEAD/user의 책임은?

- `commits`: hash → Commit 빠른 조회
- `branches`: branch name → commit hash pointer
- `head_branch`: 현재 작업 branch 이름
- `current_user`: 새 commit의 author

상태를 분리하면 branch 전환과 commit 생성 규칙을 명확히 설명할 수 있습니다.

## 4. commit hash를 증가 카운터로 만든 이유와 중복 방지는?

미션은 세션 내 unique hash를 요구하며 실제 Git SHA를 요구하지 않습니다. `c000001`처럼 증가하는 counter는 같은 세션에서 재사용하지 않으므로 uniqueness를 단순하게 보장하고 테스트 결과도 재현하기 쉽습니다.

## 5. Inverted Index는 언제 갱신되는가?

COMMIT이 성공해 hash/Commit이 생성될 때 message token과 author를 index에 추가합니다. keyword는 공식 최소 기준대로 whitespace `split()` 후 `lower()` 처리하고, 한 message에 같은 token이 반복되어도 같은 commit hash를 중복 추가하지 않습니다.

## 6. 기본 LOG에서 부모가 자식보다 먼저 나와야 하는 이유와 구현은?

공식 학습용 LOG는 최신순이 아니라 parent-first입니다. Reference는 commit을 output에 넣기 전에 parent를 재귀적으로 먼저 방문합니다. `visited`로 중복을 막고, `visiting` 중 동일 hash를 다시 만나면 cycle로 판단합니다.

## 7. 직접 구현 정렬 알고리즘은 무엇인가?

Reference는 stable merge sort를 사용합니다.

- 평균 시간복잡도: O(n log n)
- 최악 시간복잡도: O(n log n)
- 안정 정렬: Yes
- 추가 메모리: O(n)

`sorted()`와 `list.sort()`를 사용하지 않습니다.

## 8. 안정 정렬이란?

정렬 key가 같은 원소의 기존 상대 순서를 유지하는 정렬입니다. merge 과정에서 key가 같을 때 왼쪽 원소를 먼저 선택하여 안정성을 유지합니다.

## 9. PATH는 왜 BFS를 사용하는가?

공식 PATH는 parent-child 연결을 무방향 간선으로 보았을 때 간선 수가 가장 적은 경로를 요구합니다. 모든 edge weight가 동일하므로 BFS가 최단 간선 수를 찾기에 적합합니다.

## 10. PATH에서 왜 parent-child를 무방향으로 보는가?

공식 정의가 그렇게 규정되어 있기 때문입니다. 실제 commit의 parent 방향만 사용하면 서로 다른 branch의 두 child 사이에서 공통 parent를 거쳐 반대 branch로 올라갈 수 없지만, 무방향으로 보면 branch 간 관계를 shortest path 문제로 탐색할 수 있습니다.

## 11. 최단경로가 여러 개면 사전순 최소 경로를 어떻게 보장하는가?

Reference는 target에서 각 node까지 BFS distance를 계산합니다. source에서 이동할 때 distance가 정확히 1 감소하는 neighbor만 shortest-path 후보가 됩니다. 그중 hash가 사전순으로 가장 작은 neighbor를 매 단계 선택하면 전체 hash sequence도 사전순 최소가 됩니다.

## 12. ANCESTORS와 PATH 탐색 방향은 어떻게 다른가?

- ANCESTORS: child → parents 방향만 탐색
- PATH: parent-child를 무방향 edge로 해석

같은 graph라도 문제 정의에 따라 edge 방향을 다르게 사용합니다.

## 13. Inverted Index는 왜 전체 순회 검색보다 빠른가?

전체 순회 검색은 매 SEARCH마다 모든 commit message를 검사합니다. Inverted Index는 commit 생성 시 token/author → hash 목록을 미리 만들어 검색할 때 해당 bucket에서 후보를 바로 가져옵니다. index 갱신 비용과 메모리를 더 쓰는 대신 반복 검색 비용을 줄입니다.

## 14. keyword token 기준은 무엇인가?

공식 최소 기준대로 message를 공백 기준 `split()`하고 `lower()`로 정규화합니다. 따라서 Reference keyword search는 임의 substring 검색이 아니라 정규화된 token의 정확한 일치입니다.

## 15. Commit lookup에 Python dict를 사용하는 것은 왜 허용되는가?

B3-2의 제약은 graph 전용 library와 표준 정렬 API를 금지합니다. 기본 `list`, `dict`, `set`은 사용할 수 있다고 공식 문서에 명시되어 있으며, commit hash로 빠르게 찾는 저장소도 요구합니다.

## 16. 기본 LOG와 `LOG --sort-by`의 목적 차이는?

기본 LOG는 parent-before-child라는 graph 선후관계를 보장합니다. `--sort-by=date|author`는 별도의 비교 기준으로 전체 commit을 정렬하는 기능입니다. 현재 공식 요구에서는 sort 옵션에 parent-before-child를 동시에 요구하지 않습니다.

## 17. commit 수가 10배 늘어나면 어디가 병목인가?

현재 `_neighbors()`는 child를 찾기 위해 전체 `commits`를 훑습니다. PATH의 BFS에서 이를 여러 번 호출하면 큰 graph에서 비용이 커집니다. 확장 시 `parent -> children` adjacency index를 commit 생성 시 함께 유지하면 neighbor 조회를 훨씬 줄일 수 있습니다. 검색 index도 데이터 규모가 커지면 persistent index/DB를 고려할 수 있습니다.

## 18. PATH 요구가 parent 방향만 허용하도록 바뀌면?

현재는 parent와 child 모두 neighbor로 사용합니다. parent-only로 바뀌면 `_neighbors()` 대신 현재 commit의 `parents`만 다음 후보로 사용합니다. 그러면 child에서 ancestor로는 갈 수 있지만 ancestor에서 descendant로 내려가거나 다른 branch sibling으로 이동할 수 없습니다. 결과적으로 기존에 존재하던 많은 PATH가 `No path`가 됩니다.

## 19. `LOG --sort-by=author`에서도 parent-before-child를 유지하라고 요구가 강화되면?

단순히 author key로 merge sort하면 graph 선후관계를 깨뜨릴 수 있습니다. 이 경우 parent-before-child를 hard constraint로 두고, 현재 indegree가 0인 출력 가능 commit들 중 author가 가장 작은 것을 선택하는 방식의 **priority-aware topological ordering**을 사용할 수 있습니다. 즉 author는 tie-breaker이고 DAG dependency가 우선입니다.

## 20. counter hash와 random hash를 바꾸면 테스트/재현성에 어떤 차이가 있는가?

Counter 방식은 같은 명령 sequence에서 같은 hash 순서를 얻기 쉬워 unit test와 debugging이 단순합니다. Random 방식은 충돌 방지 검사가 추가로 필요하고 test에서 실제 hash를 동적으로 캡처해야 하며 실패 재현도 어려워질 수 있습니다. 대신 ID가 생성 순서를 직접 노출하지 않는 특성이 있습니다. B3-2에서는 학습과 재현성을 우선해 counter를 선택했습니다.

## 21. 주요 함수와 클래스의 주석/docstring 기준은?

Commit model, custom sorting algorithm, repository 책임처럼 **왜 존재하고 어떤 불변조건을 지키는지**가 중요한 단위에 설명을 둡니다. 코드 한 줄을 기계적으로 번역하는 주석보다 DAG, stable sort, token normalization, tie-break 같은 설계 의도를 설명하는 쪽을 우선합니다.

## 22. 10만 commit 수준으로 커지면 추가로 무엇을 바꿀 수 있는가?

현재는 모든 데이터가 memory에 있고 child adjacency도 즉석에서 찾습니다. 대규모에서는 parent→children adjacency, persistent storage, index partitioning, pagination, incremental log/search, cache 등을 검토합니다. 단, R01에서는 공식 범위를 넘어 시스템을 과도하게 확장하지 않습니다.
