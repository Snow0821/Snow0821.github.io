# 최순호 · Choi Soon Ho

GitHub Pages에서 제공하는 한·영 포트폴리오입니다. 방문자에게는 완성된 HTML과 PDF를 제공하며, 프레임워크나 실시간 데이터 요청은 사용하지 않습니다.

## 어디를 수정하나요?

| 수정할 내용 | 원본 |
| --- | --- |
| 이름, 직함, 소개, 이메일, 외부 링크 | `data/portfolio.json` → `profile` |
| 학력, 자격, 연구 관심사 | `education`, `qualifications`, `interests` |
| 강의 기관, 과정 설명, 역할 | `organizations`, `courses`, `roles` |
| 강의 기간과 기관·과정·역할 연결 | `teaching` |
| 논문, 저자, 학회 | `papers`, `authors`, `venues` |
| 메뉴, 제목, 버튼, 접근성 안내, PDF 표 제목 | `locales/ko.json`, `locales/en.json` |
| 최종 내용 갱신일 | `data/portfolio.json` → `updated` |
| 전체 페이지 배치 | `src/index.template.html` |
| 색상·간격·모바일 배치 | `assets/site.css` |

같은 사실을 웹과 CV용으로 두 번 적지 않습니다. 홈의 요약, 상세 탭, PDF가 같은 레코드를 사용합니다. `index.html`과 PDF는 생성 결과이므로 직접 편집하지 않습니다.

## 이력 추가하기

`teaching`의 한 레코드는 기관·과정·역할 ID와 기간만 참조합니다. `end: null`은 현재 활동이며, 시작일과 종료일이 같으면 단일 기간으로 표시합니다. 날짜는 `2026` 또는 `2026-08` 형식을 사용합니다. 기존 과정의 여러 업체 이력은 같은 과정 ID를 참조하는 별도 레코드로 추가합니다.

학력과 자격은 서로 다른 배열입니다. 학력의 `field`가 전공, `degree`가 전체 학위명, `degreeShort`가 모바일 요약용 표기이며, `institution`은 학교명, `school`은 소속 단위를 포함한 정식 표기입니다.

항목 개수, 표시 연도 범위, 현재/이전 구분, 모바일의 최신 항목은 데이터에서 계산합니다. 번역 파일에 숫자나 이력을 복사할 필요가 없습니다. 번역은 일반 텍스트이며 필요한 줄바꿈에는 `\n`을 사용합니다. 논문 제목·저자는 영문, 학회명은 선택 언어에 맞춰 표시하고 BibTeX는 영문을 사용합니다.

## 생성과 점검

웹만 수정했다면 Python 표준 라이브러리만 있으면 됩니다.

```sh
python3 scripts/build.py --site-only
python3 -m unittest discover -s tests
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
