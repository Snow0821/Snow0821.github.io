# 최순호 · Choi Soon Ho

독립연구자이자 AI·CS 강사인 최순호의 연구, 프로젝트, 강의 경력을 소개하는 한·영 포트폴리오입니다. GitHub Pages가 생성된 HTML·CSS·PDF를 정적으로 제공합니다.

## 페이지와 원본

| 페이지 | 구성 | 편집 원본 |
| --- | --- | --- |
| 메인 `/` · `/en/` | 자기소개, 대표 강의·연구, 현재 활동, 이력 문서 | `data/portfolio.json`, `locales/*.json` |
| 포트폴리오 `/portfolio/` · `/en/portfolio/` | 교육·연구·개발 활동 색인, 논문 서지정보, 프로젝트 | `papers`, `authors`, `venues`, `otherExperience` |
| 전체 이력 `/career/` · `/en/career/` | 학력, 경력, 강의 경력, 교육훈련, 자격증, 수상, 저서·기고 | `education`, `teaching`, `otherExperience`, `professionalDevelopment`, `qualifications` |
| 국문 CV `/cv/` · 경력기술서 `/career-statement/` | 웹 열람본과 PDF | `data/cv-public.json`, `data/career-statement-public.json` |
| 이력 PDF | 국문 CV 2쪽, 영문 CV 3쪽, 경력기술서 4쪽, 강사 소개서 1쪽 | 위 두 문서 원본과 `data/instructor-profile.json` |

메뉴와 목차는 표준 링크입니다. 언어를 바꾸면 같은 페이지와 활동 필터를 유지합니다. 논문의 인용문과 BibTeX는 각 논문 아래에서 복사할 수 있습니다.

## 이력 추가하기

- 포트폴리오 상단의 주제 순서와 대표·관련 작업은 `data/portfolio-themes.json`에 기존 이력 ID로 지정합니다. 제목·요약·상세 링크는 공개 원본에서 가져옵니다. 아래 전체 활동 색인은 그대로 유지됩니다.

- 강의는 `teaching`에 사업·과정 단위로 한 번 등록합니다. 학교별 과정명, 담당 역할, 트랙과 실제 활동일은 해당 과정의 `details`에 둡니다. 운영사·교육기관·수요기업이 다르면 관계를 구분해 적습니다.
- `currentRoles`에는 진행 중인 역할만 연결합니다. 종료를 확인한 활동에는 실제 종료일을, 진행 중인 과정의 예정 종료일에는 `plannedEnd`를 사용합니다. 날짜는 확인된 정밀도(연·월·일)까지 적습니다.
- 경력으로 분류한 교육 활동은 `careerCategory`로 구분합니다. 프로젝트의 상세 소개는 `portfolioProject`를 사용합니다. 개별 출강을 별도 재직 이력으로 합산하지 않습니다.
- 논문에는 공개 서지, 저자 순서와 역할을 기록합니다. 문서마다 선정한 이력이 달라도 기간, 소속, 역할은 같은 정보를 사용합니다.
- 교안과 수업용 파일, 개인 증빙은 이 공개 원본에 포함하지 않습니다. 새 공개 자료는 공개할 버전을 별도로 확인한 뒤 추가합니다.

## 생성과 점검

웹과 두 국문 문서의 열람본은 Python 표준 라이브러리로 생성합니다. PDF와 PDF 검사는 `requirements.txt`의 의존성을 사용합니다.

```sh
python3 -m pip install -r requirements.txt
python3 scripts/build.py --site-only
python3 scripts/build.py
python3 -m unittest discover -s tests
node tests/test_navigation.js
node tests/test_ui.js
```

로컬에서 `python3 -m http.server 8000`을 실행하면 루트 메뉴와 언어별 고유 주소를 확인할 수 있습니다. 화면 확인용 `scripts/layout-check.html`에서는 모바일 너비의 세 탭을 비교할 수 있습니다. 생성 결과는 Git에 함께 저장합니다. 게시 여부는 검토 후 별도로 결정합니다.

파일별 역할과 글꼴 정보는 [코드 구조와 유지 기준](docs/code-map.md)에 있습니다.
