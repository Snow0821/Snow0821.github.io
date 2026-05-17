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
  renderStages("all");
  bindStageFilters();
  bindChapterButtons();
  bindVisualControls();
  renderVisual();
});

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
