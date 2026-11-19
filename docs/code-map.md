# 포트폴리오 코드 구조

2026.11.18 기준. 한국어와 영어 각각 메인, 포트폴리오, 전체 이력을 정적 HTML로 생성합니다. 국문 CV와 경력기술서는 같은 문서 원본을 웹과 PDF로 제공합니다.

| 경로 | 역할 |
| --- | --- |
| `data/portfolio.json` | 공개 프로필, 기관·역할, 학력·자격, 사업별·학교별 강의, 연구와 프로젝트 레코드 |
| `data/cv-public.json`, `data/career-statement-public.json`, `data/instructor-profile.json` | 국·영문 CV, 경력기술서, 한 장 강사 소개서의 편집 원본 |
| `locales/{ko,en}.json` | 탭·분류명, 접근성 안내, 자기소개와 화면 문구 |
| `scripts/content.py` | 언어, 날짜·기관·과정 관계와 검증, 저자·학회 표기 및 인용문·BibTeX |
| `scripts/build_site.py`, `src/index.template.html` | 여섯 고유 주소의 HTML, 제목·대체 언어·기준 주소 생성 |
| `scripts/html_components.py`, `scripts/site_sections.py`, `scripts/publications.py` | 공통 탐색, 현재 활동·문서, 일곱 이력 분류와 논문·프로젝트 목록 생성 |
| `data/design.json`, `scripts/design.py`, `assets/site.css` | 색·활자·여백, 밝고 어두운 배경, 좁은 화면의 행 배치와 키보드 포커스 |
| `assets/site.js` | 인용문 복사, 언어 전환 시 현재 항목 유지, 과거 홈 내부 링크 연결 |
| `scripts/build_documents.py`, `cv/documents.css` | 국문 문서 원본에서 두 열람본 생성 |
| `scripts/build_cv.py`, `scripts/build_instructor_profile.py` | ReportLab으로 네 종류의 검색 가능한 A4 PDF 생성 |
| `assets/fonts/`, `licenses/` | 웹 본문 Portfolio Sans(Pretendard v1.3.9의 전체 문자 범위를 3개 파일에 나누어 제공), 제목 나눔명조, PDF·문서 나눔 글꼴과 배포 라이선스 |
| `assets/ternary-quantization.png` | 메인에서 삼진 양자화를 설명하고 관련 논문으로 연결하는 정적 개념도 |
| `scripts/layout-check.html`, `tests/` | 반응형 화면 점검과 데이터·문서·내비게이션·인용 복사 회귀 검사 |

## 기록과 생성 결과

1. 공개할 이력의 기간·기관·역할과 한·영 표기를 확인하고 해당 레코드를 수정합니다. 학교의 전체 기간과 개별 트랙의 실제 수업일은 따로 기록합니다.
2. CV·경력기술서·소개서에도 등장하는 항목은 각 원본에서 같은 날짜·역할을 적용합니다. 국·영문 CV는 `pages`와 `english_pages`에 수록합니다.
3. `python3 scripts/build.py`로 페이지와 PDF 네 종을 재생성합니다. 웹만 바꿀 때는 `--site-only`로 여섯 페이지와 두 문서 열람본을 생성합니다.
4. [생성과 점검](../README.md#생성과-점검)의 자동 검사 후, 한국어·영어에서 탭 이동과 항목 링크, 작은 화면에서 긴 제목·학교별 목록, PDF의 페이지 끝을 확인합니다.

공개 화면에서 교안·학생 자료를 제공하지 않습니다. 기존 학습 자료의 사이트 내 주소는 포트폴리오 목록으로 연결합니다. 근거 메일·운영표와 공개 여부 확인 메모는 작업용 이력표에서 관리합니다.
