# 코드 구조와 유지 기준

검토일: 2026-10-16 · 저장소: `Snow0821/Snow0821.github.io`

이 문서는 간결성 리뷰 결과와 유지한 코드의 역할을 기록합니다. 민트위키에 전달할 문서 원본으로도 사용합니다.

## 간결성 평가

기본 구조는 작고 적절합니다. Python 빌드와 정적 HTML·CSS·JavaScript만 사용하며, 웹 프레임워크·서버 API·데이터베이스·Node 패키지 설치가 필요하지 않습니다. 줄 수를 줄이기 위해 현재 화면을 위한 규칙이나 접근성을 없애기보다, 호출되지 않는 과거 구현을 제거했습니다.

| 기준 | 검토 결과와 조치 |
| --- | --- |
| 의존성 | PDF 생성에만 ReportLab이 필요합니다. `pypdf`는 완성 PDF 검사에 사용합니다. 웹 생성과 데이터 검사는 Python 표준 라이브러리, UI 로직 검사는 Node 기본 모듈을 사용합니다. |
| 사용되지 않는 구현 | 과거 4쪽 국문 CV 생성기·전용 데이터, 분야별 교육 이력 분할 조회, 그 조회만 지원하던 함수와 화면을 제거했습니다. |
| 중복 | 한 함수에서 반복하던 학교별 과정 묶기, 공통 데이터 재로딩, 여러 값을 계산해 일부만 사용하던 조회를 정리했습니다. |
| 출력 관리 | 문서 HTML도 공통 `write_if_changed()`를 사용합니다. 결과가 같으면 내용과 수정 시각을 유지합니다. |
| 가독성 | 조회·HTML·PDF·UI의 경계는 유지합니다. 일부 HTML 구성식은 여전히 길지만, 실제 화면을 표현하므로 줄 수만을 위해 별도 프레임워크나 범용 템플릿 계층을 추가하지 않았습니다. |
| 검증 | 현재 화면·PDF·공개 사실을 검증하는 112개 Python 테스트와 2종 Node 테스트를 유지합니다. 폐기한 분류별 조회를 호출하던 검사는 통합 원본과 실제 렌더링을 검사하도록 바꿨습니다. |

Python·CSS·JavaScript 운영 소스는 **2,066줄 → 1,765줄**, **301줄(14.6%) 감소**했습니다. 범위는 `scripts/*.py`, `assets/site.js`, `assets/site.css`이며, 문서·테스트·JSON·생성 HTML은 이 수치에서 제외했습니다. 과거 CV 전용 JSON 768줄도 별도로 제거했습니다.

## 생성 흐름

```text
data/portfolio.json + locales/*.json
  → content.py: 조회·검증·공통 표현
  → site_sections.py + publications.py + html_components.py
  → build_site.py + src/index.template.html → index.html
  → build_cv.py + data/design.json + assets/fonts → 영문 CV PDF

data/cv-public.json + data/career-statement-public.json
  → build_documents.py → cv/index.html + career-statement/index.html

scripts/build.py: 위 생성을 실행하되 검토된 국문 PDF는 보존
```

`data/design.json`은 `design.py`를 거쳐 웹 CSS 변수와 PDF의 글꼴·색상·열 비율을 제공합니다. 한국어 CV와 경력기술서 PDF는 별도 검토된 출판물이며 기본 빌드의 출력 대상이 아닙니다.

## 유지한 코드

| 파일 | 역할과 유지 이유 |
| --- | --- |
| `scripts/build.py` | 권장 생성 명령. `--site-only`는 PDF 패키지 없이 웹을 생성하고, 전체 빌드는 영문 CV까지 갱신합니다. |
| `scripts/content.py` | 원본 로딩, 언어 처리, 현재 활동·교육·경력 조회, 날짜·기관 관계·논문 인용 표현, 원본 검증을 한곳에서 관리합니다. 웹과 PDF가 같은 사실을 사용하기 위해 필요합니다. |
| `scripts/design.py` | 공통 디자인 값을 읽고 CSS 변수를 생성합니다. 웹과 PDF 사이의 디자인 값 복사를 줄입니다. |
| `scripts/html_components.py` | HTML 이스케이프, 번역 쌍, 모바일 접기, 링크·아이콘을 공유합니다. 반복 마크업과 접근성 속성이 어긋나는 것을 줄입니다. |
| `scripts/site_sections.py` | 프로필, 현재 활동, 학위·자격, 문서 카드, 교육·경력 화면을 조합합니다. 요약과 펼친 상세가 같은 원본을 사용합니다. |
| `scripts/publications.py` | 논문 요약·상세, 연구 태그, 인용 UI의 HTML을 만듭니다. 저자·학회·인용 사실은 `content.py`에 둡니다. |
| `scripts/build_site.py` | 위 화면과 템플릿을 결합합니다. CSS·JS 해시를 URL에 넣어 배포 후 이전 파일 캐시가 남는 문제를 줄입니다. |
| `scripts/build_documents.py` | 검토된 공개 문서 원본에서 두 읽기 화면을 생성합니다. 두 문서가 렌더링을 공유하며 원문과 논문 링크를 보존합니다. |
| `scripts/build_cv.py` | ReportLab으로 CV를 구성하고 글꼴을 내장합니다. 표의 분할 방지, 연구 태그의 줄바꿈, 쪽 배치 등 PDF에 필요한 처리를 담당합니다. |
| `src/index.template.html` | 사이트 문서 구조와 홈·연구·경력 탭을 정의합니다. 생성된 `index.html` 대신 이 파일을 수정합니다. |
| `assets/site.js` | 탭·키보드 탐색, 모바일 접기, 경력 상세, 논문 인용·복사, 한영 전환만 처리합니다. 공개 콘텐츠를 네트워크에서 가져오지 않습니다. |
| `assets/site.css` | 로컬 글꼴, 공통 배치, 모바일 반응형 규칙, 포커스와 숨김 상태를 표현합니다. UI 동작에 필요한 상태 선택자는 유지합니다. |
| `learn/prompt-engineering/index.html` | 독립된 한국어 학습 자료입니다. 자체 콘텐츠·스타일과 짧은 `<details>` 제어 코드로 동작하므로 별도 빌드 체계로 옮길 필요가 없습니다. |
| `scripts/layout-check.html` | 실제 사이트를 320·375·430px 프레임에서 확인하는 수동 검토 도구입니다. 검색 제외 상태이며 사이트 메뉴에는 노출하지 않습니다. |

### 핵심 조회와 표현 규칙

- `teaching_records()`는 각 교육 사업을 한 번씩 반환하고 전체 학교·트랙 상세를 유지합니다. 폐기한 `teaching_records(group)` 인자는 더 이상 지원하지 않습니다.
- `current_role_records()`는 확인된 진행 중 역할만 조회합니다. `teaching_history_records()`는 이 현재 활동과 별도 경력에 연결된 교육을 제외해 중복 표시를 막습니다.
- `experience_records()`는 프로젝트·경력·기타 활동을 조회하며, 민코딩처럼 연결된 출강을 한 경력 안에서 묶습니다.
- `detail_program_titles()`와 `school_program_groups()`는 검증된 수업명과 학교를 연결합니다. 같은 사업 안에서 수업명·역할이 일치하는 경우에만 합칩니다.
- `teaching_columns()`는 프로그램·대상·과목·기관 관계를 구분합니다. `teaching_display_columns()`는 읽기 쉬운 요약을, `teaching_detail_context()`는 관계 역할을 구분한 상세 정보를 제공합니다.
- `period()`는 확인된 연도·월, 진행 중·종료 예정 상태, 불연속 활동월을 표현합니다. 추측한 날짜를 만들지 않습니다.
- `validate()`는 참조·번역·날짜·트랙·저자 표기 오류를 생성 전에 검사합니다. 길이가 길더라도 공개 이력의 정확성을 지키는 규칙이므로 유지합니다.
- `authors()`, `display_authors()`, `reference()`, `bibtex()`는 화면의 저자 역할 표시와 인용문을 구분합니다.
- `write_if_changed()`는 동일한 생성 결과를 다시 쓰지 않습니다.

### UI에서 유지할 동작

`initTabs()`는 탭 선택과 방향키·Home·End 탐색을, `initDisclosures()`는 모바일 영역 접기를 담당합니다. `initCareerDetails()`는 각 이력 상세의 독립 상태와 번역된 접근성 이름을 관리합니다. `initPublications()`는 논문 상세·인용 형식·복사 실패 시 텍스트 선택을, `initLanguage()`는 문서 언어·번역 노출·PDF 다운로드·접근성 이름을 함께 바꿉니다. 이 코드는 방문자가 직접 사용하는 동작이므로 남깁니다.

## 유지한 데이터와 배포 파일

| 경로 | 유지 이유 |
| --- | --- |
| `data/portfolio.json` | 공통 공개 이력 원본. 교육 14개·세부 31개, 역할, 기관, 연구, 프로젝트를 보존합니다. 화면에 바로 나오지 않는 확인된 분류·연구 관심사·과거 요약도 원본 사실이므로 삭제하지 않았습니다. |
| `data/cv-public.json`, `data/career-statement-public.json` | 현재 국문 CV와 경력기술서의 별도 편집 원본입니다. 두 문서는 목적과 구성이 달라 공통 이력에 억지로 통합하지 않습니다. |
| `data/design.json`, `locales/*.json` | 디자인 기준과 한영 UI 문구입니다. 데이터에서 참조하는 분류 이름은 보존하며, 참조가 없는 문구만 제거했습니다. |
| `assets/fonts/`, `licenses/`, 아이콘·국기 파일과 라이선스 | 웹 글꼴 제공, PDF 글꼴 내장, 프로필 링크·언어 제어에 필요합니다. 라이선스도 함께 유지합니다. |
| `index.html`, `cv/index.html`, `career-statement/index.html`, `assets/*.pdf` | GitHub Pages가 그대로 제공하는 결과물입니다. 생성 파일이라는 이유로 제거하면 방문자에게 제공할 파일이 사라집니다. |
| `requirements.txt`, `.gitignore`, `.nojekyll` | PDF 생성 의존성, 로컬 부산물 제외, 정적 파일 배포 설정입니다. |

## 유지한 검사

| 검사 | 확인하는 동작 |
| --- | --- |
| `tests/test_content.py` | 공통 원본 수정의 전파, 사업·학교 중복 방지, 공개 이력 사실, 검증 오류, 동일 출력 보존 |
| `tests/test_current_roles.py`, `tests/test_unified_teaching.py` | 현재 활동과 교육·경력의 분리, 날짜·기관 관계, 통합 목록 순서 |
| `tests/test_verified_course_titles.py` | 실제 학교·수업명·트랙·수업 기간의 연결과 웹·PDF 전파 |
| `tests/test_compact_layout.py`, `tests/test_refined_editorial_content.py` | 요약과 상세의 사실 일치, 저자별 표기, 역할·기관·프로그램 구분 |
| `tests/test_design.py` | 대비, 글자 크기, 공통 디자인 값, 반응형 표 구조와 조작 표시 |
| `tests/test_pdf_layout.py` | PDF 태그·표의 경계, 쪽 수·내용·Unicode 매핑과 내장 글꼴 |
| `tests/test_ui.js`, `tests/test_navigation.js` | 경력 펼침 상태, 탭 키보드 탐색, 반복 전환, 한영 접근성 이름과 PDF 연결 |

실행 명령과 설치 절차는 [README](../README.md#생성과-점검)에 있습니다. Node 검사는 UI 로직 검사이며 실제 브라우저 렌더링 검사를 대신하지 않습니다.

## 제거 기록과 검증 근거

제거 전 기준 커밋은 `84bb0123639504dbbae233df6cd6ed3c2649c5af`입니다. 과거 `scripts/build_editorial_cv.py`와 `data/cv-ko-editorial.json`은 이 Git 이력에서 복구할 수 있습니다. 현재 검토된 2쪽 국문 CV·4쪽 경력기술서 PDF는 변경하지 않았습니다.

현재 화면에서 사용하지 않는 분야별 조회와 전용 `sourceId`·`sourceDetail`·`courseTracks` 표현, `teaching_values()`·`teaching_heading()`·`teaching_title()`·`school_teaching_summaries()`·`school_names()`, `teaching_list()`·`unclassified_teaching()`, 미사용 GitHub 템플릿 슬롯과 import를 제거했습니다. 미사용 PDF 스타일·표현 옵션, CSS 선택자, 언어별 16개의 미사용 문구도 정리했습니다. 프로필의 실제 GitHub 링크는 유지합니다.

검증 결과:

- Python **112개 통과**, 건너뜀·실패 없음. Node UI·탐색 **2종 통과**.
- 정리 전·후 전체 빌드의 문서 HTML 2개와 PDF 3개가 바이트 단위로 동일합니다.
- 홈 HTML도 CSS 캐시 해시를 제외하면 바이트 단위로 동일합니다. 제거한 CSS 선택자는 현재 생성 HTML의 요소와 일치하지 않습니다.
- 전체 빌드를 다시 실행해 출력 파일 6개의 내용과 수정 시각이 모두 유지되는 것을 확인했습니다.
- 기본 빌드는 기존 영문 PDF의 하단 날짜를 공통 원본 날짜로 갱신할 수 있습니다. 이번 비교는 같은 원본을 빌드한 정리 전·후 결과를 비교했고, 날짜만 다른 기존 영문 PDF를 덮어쓰지 않았습니다.
- 실제 브라우저 시각 검토는 이번 작업에 포함하지 않았습니다.

향후에도 현재 사용 경로, 원본 사실 보존, 생성 결과, 회귀 검사를 함께 확인한 뒤 코드를 제거합니다. 분류·편집 옵션이 다시 필요하면 추측으로 호환 계층을 유지하기보다 구체적인 화면 요구를 기준으로 추가합니다.
