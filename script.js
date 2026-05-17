const stages = [
  {
    id: "K0",
    group: "foundation",
    title: "입문 구현 기반",
    body: "입출력, 변수, 조건, 반복, 배열을 안정적으로 다루는 단계입니다."
  },
  {
    id: "K1",
    group: "foundation",
    title: "초기 독해와 구현",
    body: "문제 조건을 코드 구조로 옮기고 작은 예제를 직접 검산합니다."
  },
  {
    id: "K2",
    group: "foundation",
    title: "초등 초반 안정권",
    body: "완전탐색, 시뮬레이션, 정렬, 누적합의 기본 패턴을 익힙니다."
  },
  {
    id: "K3",
    group: "bridge",
    title: "초중등 브리지",
    body: "초등 중반과 중등 입문이 만나는 구간으로, 관찰과 간단한 그래프를 연결합니다."
  },
  {
    id: "K4",
    group: "bridge",
    title: "BFS / DP 입문",
    body: "큐 기반 탐색, 상태 정의, 점화식의 첫 설계를 시각화로 다룹니다."
  },
  {
    id: "K5",
    group: "bridge",
    title: "중등-고등 진입",
    body: "트리, 유니온 파인드, 구간 사고처럼 구현 부담이 올라가는 단계입니다."
  },
  {
    id: "K6",
    group: "advanced",
    title: "자료구조 활용",
    body: "세그먼트 트리, 집합 관리, 삭제와 탐색을 결합한 문제를 다룹니다."
  },
  {
    id: "K7",
    group: "advanced",
    title: "고등 중반",
    body: "증명 부담이 있는 그래프, DP, 최적화 문제를 수업의 중심으로 둡니다."
  },
  {
    id: "K8",
    group: "advanced",
    title: "고등 후반",
    body: "분할정복 최적화, 컨벡스 헐 트릭, 트리 DP 같은 상위 주제를 연결합니다."
  },
  {
    id: "K9",
    group: "advanced",
    title: "포스트 KOI 브리지",
    body: "IOI/Codeforces 고난도 성장으로 넘어가기 위한 설계와 업솔빙 단계입니다."
  }
];

const curriculumTree = [
  {
    title: "기초",
    stage: "K0-K2",
    action: "문제를 코드로 옮기는 힘 만들기",
    description: "입출력, 조건, 반복, 배열, 문자열을 안정적으로 다룹니다.",
    resources: [
      link("BIKO", "KOI 2025 1차 초등부", "https://www.biko.kr/challenge?collections=koi2025r1e1"),
      link("BIKO", "KOI 2025 2차 장애물", "https://www.biko.kr/problem/5422")
    ],
    questions: ["입력 크기를 보고 반복문 횟수를 예상했나요?", "예제 말고 직접 만든 작은 입력으로 확인했나요?"],
    children: [
      {
        title: "프로그래밍 기본",
        stage: "K0-K1",
        action: "문법보다 입력과 상태 변화에 집중",
        description: "변수, 조건문, 반복문, 함수, 표준 입출력을 문제 풀이에 맞게 씁니다.",
        resources: [
          link("BIKO", "KOI 2025 2차 장애물", "https://www.biko.kr/problem/5422"),
          link("KOI PDF", "장애물 문제", "https://assets.koi.or.kr/koi/2025/2/problems/obstacle.pdf")
        ],
        questions: ["변수 이름이 의미를 설명하나요?", "반복문 시작과 끝 조건을 말로 설명할 수 있나요?"]
      },
      {
        title: "배열과 문자열",
        stage: "K1-K2",
        action: "인덱스와 범위 실수 줄이기",
        description: "배열 순회, 카운팅, 문자열 처리, 간단한 누적 정보를 다룹니다.",
        resources: [
          link("LeetCode", "Two Sum", "https://leetcode.com/problems/two-sum/"),
          link("LeetCode", "Valid Anagram", "https://leetcode.com/problems/valid-anagram/")
        ],
        questions: ["0번 인덱스와 마지막 인덱스를 따로 확인했나요?", "카운팅 배열을 쓸 수 있는 값 범위인가요?"]
      },
      {
        title: "복잡도 감각",
        stage: "K2",
        action: "가능한 풀이와 불가능한 풀이 구분",
        description: "N의 크기와 시간 제한을 보고 O(N), O(N log N), O(N^2)을 구분합니다.",
        resources: [
          link("BOJ", "시간 복잡도 문제 모음", "https://www.acmicpc.net/step/53")
        ],
        questions: ["최악의 경우 반복 횟수는 몇 번인가요?", "N이 10배 커지면 실행 시간은 얼마나 커지나요?"]
      }
    ]
  },
  {
    title: "자료구조",
    stage: "K2-K7",
    action: "데이터를 어떤 모양으로 들고 있을지 결정",
    description: "선형 구조, 트리, 그래프, 구간 자료구조를 문제 상황에 맞게 고릅니다.",
    resources: [
      link("LeetCode", "Data Structure Study Plan", "https://leetcode.com/studyplan/data-structure/"),
      link("KOI Index", "공식 링크 인덱스", "curriculum/problems/koi/official-link-index.md")
    ],
    questions: ["삽입, 삭제, 탐색 중 무엇이 자주 일어나나요?", "순서가 중요한가요, 연결 관계가 중요한가요?"],
    children: [
      {
        title: "선형",
        stage: "K2-K4",
        action: "배열 위에서 빠르게 움직이기",
        description: "배열, 스택, 큐, 덱, 해시, 누적합을 사용합니다.",
        resources: [
          link("LeetCode", "Range Sum Query - Immutable", "https://leetcode.com/problems/range-sum-query-immutable/"),
          link("BOJ", "구간 합 구하기 4", "https://www.acmicpc.net/problem/11659")
        ],
        questions: ["처리 순서가 앞에서 뒤로 한 번만 가도 되나요?", "구간 정보를 매번 다시 계산하고 있나요?"],
        children: [
          {
            title: "스택 / 큐 / 덱",
            stage: "K3-K4",
            action: "최근 것, 먼저 온 것, 양끝 처리를 구분",
            description: "괄호, BFS 큐, 슬라이딩 윈도우 후보 관리에 사용합니다.",
            resources: [
              link("LeetCode", "Valid Parentheses", "https://leetcode.com/problems/valid-parentheses/"),
              link("LeetCode", "Implement Queue using Stacks", "https://leetcode.com/problems/implement-queue-using-stacks/")
            ],
            questions: ["마지막에 들어온 것을 먼저 써야 하나요?", "큐에 같은 상태가 여러 번 들어가지 않게 했나요?"]
          },
          {
            title: "누적합 / 차분",
            stage: "K2-K4",
            action: "반복 구간 계산 줄이기",
            description: "구간 합, 변화량 기록, 여러 질의를 빠르게 처리합니다.",
            resources: [
              link("BIKO", "KOI 2025 2차 통행료", "https://www.biko.kr/problem/5425"),
              link("LeetCode", "Range Sum Query - Immutable", "https://leetcode.com/problems/range-sum-query-immutable/"),
              link("BOJ", "구간 합 구하기 4", "https://www.acmicpc.net/problem/11659")
            ],
            questions: ["구간 합을 몇 번 물어보나요?", "l=0 또는 첫 칸을 어떻게 처리하나요?"]
          }
        ]
      },
      {
        title: "트리",
        stage: "K5-K8",
        action: "부모-자식 관계와 부분트리 보기",
        description: "DFS, LCA, 트리 DP, 루트 바꾸기 관점을 다룹니다.",
        resources: [
          link("LeetCode", "Binary Tree Level Order Traversal", "https://leetcode.com/problems/binary-tree-level-order-traversal/"),
          link("BIKO", "KOI 2025 2차 축제", "https://www.biko.kr/problem/5431")
        ],
        questions: ["루트를 어디로 잡아도 되나요?", "부분트리 정보가 부모로 올라가나요?"]
      },
      {
        title: "그래프",
        stage: "K4-K8",
        action: "정점과 간선으로 상태 연결하기",
        description: "BFS/DFS, 최단거리, 위상정렬, 연결성 문제를 다룹니다.",
        resources: [
          link("BIKO", "KOI 2024 2차 가로등", "https://www.biko.kr/problem/4671"),
          link("LeetCode", "Number of Islands", "https://leetcode.com/problems/number-of-islands/")
        ],
        questions: ["정점은 무엇이고 간선은 무엇인가요?", "방문 처리는 큐에 넣을 때 하나요, 꺼낼 때 하나요?"]
      },
      {
        title: "구간 자료구조",
        stage: "K6-K8",
        action: "변하는 배열에서 빠른 질의 처리",
        description: "Fenwick tree, segment tree, lazy propagation의 필요성을 봅니다.",
        resources: [
          link("BIKO", "KOI 2025 2차 상자 보관", "https://www.biko.kr/problem/5429"),
          link("BIKO", "KOI 2025 2차 수열과 쿼리", "https://www.biko.kr/problem/5430"),
          link("BOJ", "구간 합 구하기", "https://www.acmicpc.net/problem/2042")
        ],
        questions: ["배열 값이 중간에 바뀌나요?", "질의와 업데이트가 각각 몇 번인가요?"]
      }
    ]
  },
  {
    title: "알고리즘",
    stage: "K2-K9",
    action: "풀이 전략 선택",
    description: "완전탐색에서 최적화까지 문제를 푸는 대표 전략을 정리합니다.",
    resources: [
      link("LeetCode", "Algorithm Study Plan", "https://leetcode.com/studyplan/algorithm/"),
      link("KOI Index", "공식 링크 인덱스", "curriculum/problems/koi/official-link-index.md")
    ],
    questions: ["이 문제의 병목은 경우의 수인가요, 자료 검색인가요?", "더 빠른 풀이가 필요한 근거가 있나요?"],
    children: [
      {
        title: "완전탐색 / 시뮬레이션",
        stage: "K2-K4",
        action: "가능한 경우를 빠짐없이 만들기",
        description: "작은 제한에서 모든 후보를 만들고 조건을 검사합니다.",
        resources: [
          link("BIKO", "KOI 2025 2차 거울", "https://www.biko.kr/problem/5423"),
          link("LeetCode", "Permutations", "https://leetcode.com/problems/permutations/")
        ],
        questions: ["모든 후보를 만들면 몇 개인가요?", "시뮬레이션 상태를 한 줄로 설명할 수 있나요?"]
      },
      {
        title: "정렬 / 이분탐색",
        stage: "K3-K5",
        action: "순서를 이용해 후보 줄이기",
        description: "정렬 후 스캔, 매개변수 탐색, lower/upper bound를 다룹니다.",
        resources: [
          link("LeetCode", "Binary Search", "https://leetcode.com/problems/binary-search/"),
          link("BOJ", "수 찾기", "https://www.acmicpc.net/problem/1920")
        ],
        questions: ["정렬하면 무엇을 빨리 판단할 수 있나요?", "이분탐색 조건은 참/거짓이 한 번만 바뀌나요?"]
      },
      {
        title: "그리디",
        stage: "K4-K6",
        action: "지금 선택이 유지되는 이유 설명",
        description: "정렬 기준, 교환 논증, 반례 확인을 함께 훈련합니다.",
        resources: [
          link("LeetCode", "Assign Cookies", "https://leetcode.com/problems/assign-cookies/"),
          link("BOJ", "회의실 배정", "https://www.acmicpc.net/problem/1931")
        ],
        questions: ["지금 선택을 나중에 바꿔야 하는 반례가 있나요?", "정렬 기준을 바꾸면 답이 달라지나요?"]
      },
      {
        title: "동적 계획법",
        stage: "K4-K8",
        action: "상태와 전이를 먼저 쓰기",
        description: "1차원/2차원 DP, 배낭, 구간 DP, 트리 DP로 확장합니다.",
        resources: [
          link("LeetCode", "Climbing Stairs", "https://leetcode.com/problems/climbing-stairs/"),
          link("LeetCode", "House Robber", "https://leetcode.com/problems/house-robber/"),
          link("BIKO", "KOI 2025 2차 가방", "https://www.biko.kr/problem/5426")
        ],
        questions: ["dp[i]가 정확히 무엇을 뜻하나요?", "현재 상태는 어떤 이전 상태에서 오나요?"]
      },
      {
        title: "그래프 알고리즘",
        stage: "K4-K9",
        action: "탐색, 거리, 연결성, 순서를 구분",
        description: "BFS/DFS, Dijkstra, MST, SCC, flow로 확장합니다.",
        resources: [
          link("LeetCode", "Course Schedule", "https://leetcode.com/problems/course-schedule/"),
          link("LeetCode", "Network Delay Time", "https://leetcode.com/problems/network-delay-time/"),
          link("BIKO", "KOI 2025 2차 새로운 인연", "https://www.biko.kr/problem/5427")
        ],
        questions: ["가중치가 있나요?", "방향이 있나요?", "최단거리인가요, 연결성인가요?"]
      },
      {
        title: "문자열 / 수학",
        stage: "K5-K9",
        action: "패턴과 수식으로 압축",
        description: "문자열 매칭, 해싱, 조합론, 정수론을 필요한 시점에 다룹니다.",
        resources: [
          link("LeetCode", "Implement strStr", "https://leetcode.com/problems/find-the-index-of-the-first-occurrence-in-a-string/"),
          link("BOJ", "문자열 집합", "https://www.acmicpc.net/problem/14425")
        ],
        questions: ["문자열을 매번 비교하면 총 몇 글자를 보나요?", "수식으로 바꾸면 상태 수가 줄어드나요?"]
      }
    ]
  },
  {
    title: "문제풀이 훈련",
    stage: "K1-K9",
    action: "풀이 과정을 재사용 가능한 절차로 만들기",
    description: "문제 읽기, 전략 선택, 구현, 디버깅, 업솔빙을 분리해서 훈련합니다.",
    resources: [
      link("KOI Index", "공식 링크 인덱스", "curriculum/problems/koi/official-link-index.md"),
      link("BIKO", "BIKO", "https://www.biko.kr/")
    ],
    questions: ["풀이 전 생각과 풀이 후 배운 점이 분리되어 있나요?", "틀린 제출의 원인이 기록되어 있나요?"],
    children: [
      {
        title: "문제 읽기",
        stage: "K1-K9",
        action: "조건과 목표를 표로 정리",
        description: "입력 크기, 출력 목표, 예외 조건, 숨은 상태를 먼저 찾습니다.",
        questions: ["구해야 하는 값이 정확히 무엇인가요?", "제한 조건에서 풀이 힌트를 찾았나요?"]
      },
      {
        title: "구현 계획",
        stage: "K2-K9",
        action: "코드 쓰기 전 자료구조와 함수 나누기",
        description: "변수 의미, 반복 순서, 검산 예제를 먼저 정합니다.",
        questions: ["핵심 배열/그래프의 의미를 주석 없이 설명할 수 있나요?", "작은 테스트를 손으로 계산했나요?"]
      },
      {
        title: "디버깅 / 업솔빙",
        stage: "K2-K9",
        action: "틀린 이유를 유형화",
        description: "반례, 경계값, 시간초과 원인, 더 나은 풀이를 기록합니다.",
        resources: [
          link("Test Data", "KOI 테스트 데이터 인덱스", "curriculum/problems/koi/test-data-index.md")
        ],
        questions: ["오답이 구현 실수인가요, 접근 실수인가요?", "다시 풀면 먼저 무엇을 확인할 건가요?"]
      }
    ]
  },
  {
    title: "KOI 단계",
    stage: "K0-K9",
    action: "기출 문제를 현재 위치에 연결",
    description: "학년 구분보다 필요한 개념과 구현 부담으로 문제를 배치합니다.",
    resources: [
      link("KOI", "공식 과거 대회", "https://koi.or.kr/archives/"),
      link("BIKO", "BIKO", "https://www.biko.kr/")
    ],
    questions: ["학년 표기보다 실제 필요한 개념은 무엇인가요?", "이 문제는 어느 단계의 대표 문제인가요, 도전 문제인가요?"],
    children: [
      {
        title: "K0-K2 기초",
        stage: "K0-K2",
        action: "구현 안정화",
        description: "초기 구현, 독해, 완전탐색, 정렬, 누적합을 익힙니다.",
        resources: [
          link("BIKO", "KOI 2025 2차 장애물", "https://www.biko.kr/problem/5422"),
          link("BIKO", "KOI 2025 1차 먼 카드", "https://www.biko.kr/problem/5354")
        ],
        questions: ["문제 조건을 빠짐없이 코드로 옮겼나요?", "시간초과보다 구현 안정성이 먼저인가요?"]
      },
      {
        title: "K3-K5 브리지",
        stage: "K3-K5",
        action: "초중고 공유 문제 연결",
        description: "관찰, BFS, DP 입문, 트리/유니온 파인드 진입 문제를 다룹니다.",
        resources: [
          link("BIKO", "KOI 2025 2차 거울", "https://www.biko.kr/problem/5423"),
          link("BIKO", "KOI 2025 2차 통행료", "https://www.biko.kr/problem/5425"),
          link("BIKO", "KOI 2025 2차 가방", "https://www.biko.kr/problem/5426")
        ],
        questions: ["관찰로 줄일 수 있는 상태가 있나요?", "BFS/DP 중 어느 쪽 상태 정의가 자연스럽나요?"]
      },
      {
        title: "K6-K9 심화",
        stage: "K6-K9",
        action: "상위 자료구조와 최적화",
        description: "세그먼트 트리, 고급 그래프, 최적화 DP, 고난도 업솔빙으로 확장합니다.",
        resources: [
          link("BIKO", "KOI 2025 2차 로봇", "https://www.biko.kr/problem/5428"),
          link("BIKO", "KOI 2025 2차 수열과 쿼리", "https://www.biko.kr/problem/5430"),
          link("BIKO", "KOI 2025 2차 축제", "https://www.biko.kr/problem/5431")
        ],
        questions: ["단순 풀이의 병목은 어디인가요?", "어떤 자료구조나 최적화가 병목을 없애나요?"]
      }
    ]
  }
];

function link(source, title, href) {
  return { source, title, href };
}

const visuals = {
  prefix: {
    title: "Prefix Sum",
    captions: [
      "원본 배열에서 구간 합을 여러 번 묻는 상황입니다.",
      "왼쪽부터 누적합을 만들어 sum[i] = sum[i - 1] + a[i]를 계산합니다.",
      "구간 [2, 5]의 합은 prefix[5] - prefix[1]처럼 두 값의 차이로 구합니다."
    ],
    render(step) {
      const values = [3, 1, 4, 1, 5, 9];
      const prefix = values.reduce((acc, value, index) => {
        acc.push((acc[index - 1] || 0) + value);
        return acc;
      }, []);
      const active = step === 0 ? [0, 1, 2, 3, 4, 5] : step === 1 ? [0, 1, 2, 3] : [1, 5];
      return `
        <div class="array-row">${values.map((value, index) => cell(value, active.includes(index), false)).join("")}</div>
        <div class="array-row">${prefix.map((value, index) => cell(value, step > 0 && active.includes(index), step === 2 && [1, 5].includes(index))).join("")}</div>
      `;
    }
  },
  bfs: {
    title: "BFS Queue",
    captions: [
      "시작 정점을 큐에 넣고 방문 표시를 합니다.",
      "큐의 앞에서 하나를 꺼내 인접한 미방문 정점을 뒤에 넣습니다.",
      "큐가 빌 때까지 같은 일을 반복하면 거리 순서대로 탐색됩니다."
    ],
    render(step) {
      const grid = [
        ["S", ".", ".", "#"],
        ["#", ".", "#", "."],
        [".", ".", ".", "G"]
      ];
      const done = step === 0 ? [[0, 0]] : step === 1 ? [[0, 0], [0, 1], [1, 1]] : [[0, 0], [0, 1], [1, 1], [2, 1], [2, 2]];
      const frontier = step === 0 ? [[0, 0]] : step === 1 ? [[0, 1], [1, 1]] : [[2, 2], [2, 3]];
      const rows = grid.map((row, r) => `
        <div class="grid-row">
          ${row.map((value, c) => {
            const blocked = value === "#";
            const isDone = hasPoint(done, r, c);
            const isFrontier = hasPoint(frontier, r, c);
            return `<div class="cell ${blocked ? "blocked" : isFrontier ? "frontier" : isDone ? "done" : ""}">${value}</div>`;
          }).join("")}
        </div>
      `).join("");
      const queue = step === 0 ? "(0,0)" : step === 1 ? "(0,1), (1,1)" : "(2,2), (2,3)";
      return `${rows}<div class="queue-line">Queue: ${queue}</div>`;
    }
  },
  dp: {
    title: "DP Table",
    captions: [
      "상태를 먼저 정의합니다. 예: dp[i]는 i번째 칸까지 오는 경우의 수입니다.",
      "이전 상태에서 현재 상태로 값이 넘어오는 관계를 표시합니다.",
      "표를 채우면 마지막 상태가 문제의 답이 됩니다."
    ],
    render(step) {
      const values = step === 0 ? [1, "", "", "", "", ""] : step === 1 ? [1, 1, 2, 3, "", ""] : [1, 1, 2, 3, 5, 8];
      return `
        <div class="dp-row">
          ${values.map((value, index) => cell(value, step === 1 && [2, 3].includes(index), step === 2 && value !== "")).join("")}
        </div>
        <div class="queue-line">transition: dp[i] = dp[i - 1] + dp[i - 2]</div>
      `;
    }
  }
};

let currentChapter = "prefix";
let currentStep = 0;

document.addEventListener("DOMContentLoaded", () => {
  renderCurriculumTree();
  renderStages("all");
  bindStageFilters();
  bindChapterButtons();
  bindVisualControls();
  renderVisual();
});

function renderCurriculumTree() {
  const container = document.getElementById("curriculum-tree");
  if (!container) {
    return;
  }
  container.innerHTML = renderTreeNodes(curriculumTree, []);
  container.querySelectorAll(".tree-children").forEach((list) => list.classList.add("collapsed"));
  container.querySelectorAll(".tree-toggle").forEach((button) => {
    button.addEventListener("click", () => {
      const target = document.getElementById(button.getAttribute("aria-controls"));
      const isCollapsed = target.classList.toggle("collapsed");
      button.textContent = isCollapsed ? "+" : "-";
      button.setAttribute("aria-expanded", String(!isCollapsed));
    });
  });
  container.querySelectorAll(".tree-node").forEach((button) => {
    button.addEventListener("click", () => {
      container.querySelectorAll(".tree-node").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      updatePathPanel(JSON.parse(button.dataset.node));
    });
  });
  document.getElementById("expand-tree").addEventListener("click", () => setTreeCollapsed(false));
  document.getElementById("collapse-tree").addEventListener("click", () => setTreeCollapsed(true));
}

function renderTreeNodes(nodes, path) {
  return `<ul>${nodes.map((node, index) => {
    const nextPath = [...path, node.title];
    const childId = `tree-${nextPath.join("-").replace(/[^a-zA-Z0-9가-힣]/g, "-")}-${index}`;
    const nodeData = {
      title: node.title,
      stage: node.stage,
      action: node.action,
      description: node.description,
      path: nextPath,
      resources: node.resources || [],
      questions: node.questions || []
    };
    return `
      <li>
        <div class="tree-row">
          ${node.children ? `<button class="tree-toggle" type="button" aria-expanded="false" aria-controls="${childId}">+</button>` : `<span class="tree-spacer"></span>`}
          <button class="tree-node" type="button" data-node='${escapeAttribute(JSON.stringify(nodeData))}'>
            <span>${node.title}</span>
            <small>${node.stage}</small>
          </button>
        </div>
        ${node.children ? `<div id="${childId}" class="tree-children">${renderTreeNodes(node.children, nextPath)}</div>` : ""}
      </li>
    `;
  }).join("")}</ul>`;
}

function updatePathPanel(node) {
  document.getElementById("path-title").textContent = node.title;
  document.getElementById("path-description").textContent = node.description;
  document.getElementById("path-stage").textContent = node.stage;
  document.getElementById("path-action").textContent = node.action;
  document.getElementById("path-steps").innerHTML = node.path.map((item) => `<li>${item}</li>`).join("");
  document.getElementById("path-resources").innerHTML = renderResources(node.resources);
  document.getElementById("path-questions").innerHTML = renderQuestions(node.questions);
}

function renderResources(resources) {
  if (!resources || resources.length === 0) {
    return `<span>아직 연결된 추천 문제가 없습니다.</span>`;
  }
  return resources.map((resource) => `
    <a href="${resource.href}" target="${resource.href.startsWith("http") ? "_blank" : "_self"}" rel="noreferrer">
      <strong>${resource.source}</strong>
      <span>${resource.title}</span>
    </a>
  `).join("");
}

function renderQuestions(questions) {
  const fallback = ["이 개념이 필요한 문제 신호는 무엇인가요?", "비슷한 문제를 다시 만나면 먼저 무엇을 확인할 건가요?"];
  return (questions && questions.length ? questions : fallback).map((question) => `<li>${question}</li>`).join("");
}

function setTreeCollapsed(collapsed) {
  document.querySelectorAll(".tree-children").forEach((list) => {
    list.classList.toggle("collapsed", collapsed);
  });
  document.querySelectorAll(".tree-toggle").forEach((button) => {
    button.textContent = collapsed ? "+" : "-";
    button.setAttribute("aria-expanded", String(!collapsed));
  });
}

function escapeAttribute(value) {
  return value.replace(/&/g, "&amp;").replace(/'/g, "&#39;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function renderStages(filter) {
  const container = document.getElementById("stage-grid");
  const visibleStages = filter === "all" ? stages : stages.filter((stage) => stage.group === filter);
  container.innerHTML = visibleStages.map((stage) => `
    <article class="stage-card">
      <strong>${stage.id}</strong>
      <span>${stage.title}</span>
      <p>${stage.body}</p>
    </article>
  `).join("");
}

function bindStageFilters() {
  document.querySelectorAll(".filter-button").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".filter-button").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      renderStages(button.dataset.filter);
    });
  });
}

function bindChapterButtons() {
  document.querySelectorAll(".chapter-button").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".chapter-button").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      currentChapter = button.dataset.chapter;
      currentStep = 0;
      renderVisual();
    });
  });
}

function bindVisualControls() {
  document.getElementById("prev-step").addEventListener("click", () => {
    currentStep = (currentStep + 2) % 3;
    renderVisual();
  });
  document.getElementById("next-step").addEventListener("click", () => {
    currentStep = (currentStep + 1) % 3;
    renderVisual();
  });
}

function renderVisual() {
  const visual = visuals[currentChapter];
  document.getElementById("visual-title").textContent = visual.title;
  document.getElementById("visual-canvas").innerHTML = visual.render(currentStep);
  document.getElementById("visual-caption").textContent = visual.captions[currentStep];
}

function cell(value, active, done) {
  return `<div class="cell ${done ? "done" : active ? "active" : ""}">${value}</div>`;
}

function hasPoint(points, r, c) {
  return points.some(([row, col]) => row === r && col === c);
}
