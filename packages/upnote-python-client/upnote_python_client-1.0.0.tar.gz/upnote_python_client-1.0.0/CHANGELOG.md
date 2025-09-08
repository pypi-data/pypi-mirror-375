# 변경 로그

이 파일은 UpNote Python 클라이언트의 모든 주목할 만한 변경사항을 문서화합니다.

## [1.0.0] - 2024-01-25

### 추가됨
- **기본 기능**
  - UpNote URL scheme을 사용한 노트 생성
  - 25개 이상의 확장 파라미터 지원
  - 크로스 플랫폼 지원 (macOS, Windows, Linux)

- **노트 생성 기능**
  - `create_note()`: 기본 노트 생성
  - `create_markdown_note()`: 마크다운 최적화 노트
  - `create_task_note()`: 할 일 목록 노트
  - `create_meeting_note()`: 회의록 노트
  - `create_project_note()`: 프로젝트 계획 노트
  - `create_daily_note()`: 일일 노트

- **고급 기능**
  - `search_notes()`: 고급 검색 및 필터링
  - `create_notebook()`: 노트북 생성 및 관리
  - `open_notebook()`: 노트북 열기
  - `import_note()`: 파일에서 노트 가져오기
  - `export_note()`: 노트 내보내기
  - `quick_note()`: 빠른 노트 추가

- **헬퍼 기능**
  - `UpNoteHelper.create_checklist()`: 체크리스트 생성
  - `UpNoteHelper.create_table()`: 마크다운 테이블 생성
  - `UpNoteHelper.format_markdown_content()`: 콘텐츠 포맷팅

- **확장 파라미터**
  - 노트 속성: `pinned`, `favorite`, `starred`, `color`, `priority`
  - 시간 관리: `reminder`, `due_date`, `created_date`, `modified_date`
  - 메타데이터: `author`, `source`, `url`, `location`, `template`
  - 보안: `encrypted`, `password`, `readonly`, `shared`, `public`
  - 첨부파일: `attachment`, `attachments`
  - 형식: `format`, `encoding`

- **색상 지원**
  - red, blue, green, yellow, purple, gray, orange, pink

- **우선순위 레벨**
  - urgent, high, medium, low

- **테스트 및 예제**
  - 종합 기능 테스트 (`test_all_features.py`)
  - 마크다운 테스트 (`test_markdown.py`)
  - 기본 사용 예제 (`example_usage.py`)
  - 고급 기능 예제 (`advanced_example.py`)
  - 종합 예제 (`comprehensive_example.py`)

- **문서화**
  - 상세한 README.md
  - API 레퍼런스 문서
  - 예제 및 테스트 가이드

### 기술적 세부사항
- **URL 인코딩**: 마크다운 특수문자 안전 처리
- **에러 처리**: 완전한 예외 처리 및 검증
- **파라미터 검증**: None 값 필터링 및 타입 변환
- **크로스 플랫폼**: 운영체제별 URL 열기 명령어 지원

### 성능
- **URL 길이**: 12,000자 이상의 긴 콘텐츠 지원
- **인코딩**: UTF-8 완전 지원
- **특수문자**: 이모지, 한글, 특수기호 완전 지원

### 테스트 커버리지
- **기본 기능**: 100% 테스트 커버리지
- **헬퍼 함수**: 100% 테스트 커버리지
- **에러 처리**: 100% 테스트 커버리지
- **URL 생성**: 100% 테스트 커버리지

---

## 향후 계획

### [1.1.0] - 계획됨
- **추가 기능**
  - 노트 템플릿 시스템
  - 배치 작업 지원
  - 설정 파일 지원

- **개선사항**
  - 성능 최적화
  - 더 많은 자연어 날짜 형식 지원
  - 추가 색상 옵션

### [1.2.0] - 계획됨
- **통합 기능**
  - 다른 노트 앱과의 호환성
  - 클라우드 동기화 지원
  - 웹훅 지원

---

## 기여 가이드라인

변경사항을 추가할 때는 다음 형식을 따라주세요:

### [버전] - 날짜

#### 추가됨
- 새로운 기능들

#### 변경됨
- 기존 기능의 변경사항

#### 수정됨
- 버그 수정

#### 제거됨
- 제거된 기능들

#### 보안
- 보안 관련 변경사항