# 최순호 · Choi Soon Ho

GitHub Pages에서 제공하는 한·영 포트폴리오입니다. 방문자에게는 완성된 HTML과 PDF를 제공하며, 프레임워크나 실시간 데이터 요청은 사용하지 않습니다.

## 어디를 수정하나요?

| 수정할 내용 | 원본 |
| --- | --- |
| 이름, 직함, 소개, 이메일, 외부 링크 | `data/portfolio.json` → `profile` |
| 홈의 현직 요약 | `currentRoles` |
| 학력, 자격, 연구 관심사 | `education`, `qualifications`, `interests` |
| 강의 기관, 과정 설명, 역할 | `organizations`, `courses`, `roles` |
| 강의 기간과 기관·과정·역할 연결 | `teaching` |
| 논문, 저자, 학회 | `papers`, `authors`, `venues` |
| 메뉴, 제목, 버튼, 접근성 안내, PDF 표 제목 | `locales/ko.json`, `locales/en.json` |
| 최종 내용 갱신일 | `data/portfolio.json` → `updated` |
| 전체 페이지 배치 | `src/index.template.html` |
| 색상·간격·모바일 배치 | `assets/site.css` |

같은 사실을 웹과 CV용으로 두 번 적지 않습니다. 홈의 요약, 상세 탭, PDF가 같은 레코드를 사용합니다. `index.html`과 PDF는 생성 결과이므로 직접 편집하지 않습니다.

## 학습 자료

경력 탭의 **학습 자료**에서 인터랙티브 개념 지도로 이동할 수 있습니다.

- 공개 주소: <https://snow0821.github.io/learn/prompt-engineering/>
- 내용과 동작: `learn/prompt-engineering/index.html`을 직접 편집합니다. 별도 빌드나 외부 스크립트 없이 동작하는 정적 페이지입니다.
- 포트폴리오의 연결 위치: `src/index.template.html`. 링크 제목과 설명은 `locales/ko.json`, `locales/en.json`에서 관리합니다.
- 개념 지도 본문은 한국어이며, 시기별 펼침·접기와 원 논문·공식 문서 링크를 제공합니다.

## 이력 추가하기

`teaching`의 한 레코드는 기관·과정·역할 ID와 기간만 참조합니다. `end: null`은 현재 활동이며, 시작일과 종료일이 같으면 단일 기간으로 표시합니다. 날짜는 `2026` 또는 `2026-08` 형식을 사용합니다. 기존 과정의 여러 업체 이력은 같은 과정 ID를 참조하는 별도 레코드로 추가합니다.

학력과 자격은 서로 다른 배열입니다. 학력의 `field`가 전공, `degree`가 전체 학위명, `degreeShort`가 모바일 요약용 표기이며, `institution`은 학교명, `school`은 소속 단위를 포함한 정식 표기입니다.

항목 개수, 표시 연도 범위, 현재/이전 구분, 모바일의 최신 항목은 데이터에서 계산합니다. 번역 파일에 숫자나 이력을 복사할 필요가 없습니다. 번역은 일반 텍스트이며 필요한 줄바꿈에는 `\n`을 사용합니다. 논문 제목·저자는 영문, 학회명은 선택 언어에 맞춰 표시하고 BibTeX는 영문을 사용합니다.

### 홈의 현직

`currentRoles`는 확인된 현재 역할만 모은 홈 전용 요약입니다. 연결된 교육 활동이 있는 역할은 `teaching` ID를 참조해 기관·시작월·종료월을 재사용하며, 엘리스 프리랜서 활동처럼 개별 과정과 기간이 다른 역할은 별도 기간을 기록합니다. `title`은 역할, 선택 항목 `context`는 과정 맥락이며 한·영을 함께 적습니다. 종료월이 생긴 역할은 현직 영역에서 자동으로 제외됩니다. 프리랜서 활동을 상근·연속 고용으로 표시하지 않고, 과정 수나 전체 경력 수에도 더하지 않습니다. 현직은 모바일에서도 접지 않고 표시하며 기존 분야별 강의·개발 이력은 그대로 유지합니다.

### 학교·업체별 상세 이력

기존 `teaching` 항목의 `details` 배열에 학교·업체(`title`), 활동월(`start`, `end`), 역할 ID(`role`), 커리큘럼(`curriculum`)을 기록합니다. 경력 탭에서 각 사업 제목 옆 `+` 버튼으로 세부 이력을 펼칩니다. 다시 누르면 `−`에서 `+`로 돌아오며 접힙니다. 키보드 Enter·Space도 지원합니다. 홈과 PDF는 분야별 과정과 해당 학교를 요약합니다. `note`는 선택 항목입니다. 사업에 속하지 않는 개발·프로젝트 경력은 `otherExperience`에 별도로 기록합니다.

`teachingGroups`는 인공지능 교육, 데이터 교육, 프로그래밍·자료구조·알고리즘 교육 순서이며, `otherExperience`는 네 번째 개발 경력으로 표시합니다. 홈·경력 탭·한영 CV는 같은 분류를 사용합니다. 자료구조는 프로그래밍 분야에 포함하고, 코디세이의 AI Native 과정은 AI 교육으로 표시합니다.

디지털새싹과 엘리스 SW동행은 `courses`의 `classifyDetails` 및 학교별 `details[].group`을 사용합니다. 실제 내용이 확인된 복수 분야 과정은 `details[].tracks`로 나눕니다. 원본 사업·학교 이력은 한 번만 저장하고 `teaching_records(group)`이 분야별 화면을 만듭니다. 각 화면에 사업명·기관·학교를 남깁니다. 전체 경력 수는 원본 사업과 개발 경력의 고유 개수이며, 분야별 표시 수를 합산하지 않습니다.

한 학교의 여러 트랙에서 `start`·`end`를 생략하면 확인된 학교 전체 활동기간을 표시하며, 트랙별 실시월 미확인 안내를 붙입니다. 확인되지 않은 기간·시수는 만들지 않습니다. `group: null`인 상세는 임의 분류하지 않고 확인 대기 영역으로 보존합니다. 공개 데이터에는 계약서·계좌·학생 정보나 비공개 증빙 링크를 넣지 않습니다.

확인된 활동월만 사용하고 월이 불명확하면 연도만 적습니다. 배정·제안만 확인된 활동이나 비공개 증빙 링크는 공개 데이터에 포함하지 않습니다.

## 생성과 점검

웹 생성에는 Python 표준 라이브러리만 있으면 됩니다. 펼침·접힘 UI 회귀 테스트에는 Node.js를 사용합니다.

```sh
python3 scripts/build.py --site-only
python3 -m unittest discover -s tests
node tests/test_ui.js
```

CV까지 함께 갱신하려면 `reportlab`을 설치하고 `NanumGothic-Regular.ttf`, `NanumGothic-Bold.ttf`가 있는 폴더를 지정합니다.

```sh
python3 -m pip install -r requirements.txt
CV_FONT_DIR=/path/to/fonts python3 scripts/build.py
```

기본 PDF 출력 위치는 `assets/`입니다. `CV_OUTPUT_DIR`로 다른 폴더를 지정할 수 있습니다. 생성 결과가 같으면 파일을 다시 쓰지 않으며 PDF 생성 시각 때문에 불필요한 변경이 생기지 않습니다. 데이터 수정 후에는 원본과 생성된 HTML·PDF를 함께 커밋합니다.

`scripts/layout-check.html`은 실제 사이트를 320·375·430px 프레임에서 확인하는 개발용 페이지입니다. 검색 제외(`noindex`) 상태이며 사이트 메뉴에 노출되지 않습니다.

## 코드 구성

- `scripts/content.py`: 공통 조회·날짜·인용·검증 규칙
- `scripts/html_components.py`: 번역 쌍, 접기 영역, 링크 등 공통 HTML
- `scripts/site_sections.py`, `scripts/publications.py`: 영역별 화면 구성
- `scripts/build_site.py`, `scripts/build_cv.py`: 웹/PDF 출력
- `scripts/build.py`: 전체 생성 명령
- `assets/site.js`: 탭, 접기, 인용, 언어 전환을 각각 독립된 초기화 함수로 구성

언어를 추가할 때는 `languages`에 코드·이름·국기 경로를 넣고 같은 키를 가진 번역 파일과 데이터 번역을 추가합니다. 언어 전환, 접근성 안내, CV 연결은 이 설정에서 생성되므로 JavaScript에 언어별 조건문을 추가할 필요가 없습니다.

