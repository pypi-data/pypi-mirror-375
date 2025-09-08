# UpNote 클라이언트 API 레퍼런스

## 클래스 개요

### UpNoteClient
UpNote의 x-callback-url을 사용하여 노트를 작성하고 관리하는 메인 클래스입니다.

### UpNoteHelper
마크다운 콘텐츠 생성과 포맷팅을 위한 헬퍼 클래스입니다.

---

## UpNoteClient 메서드

### 기본 노트 관리

#### `create_note(**kwargs) -> bool`
새로운 노트를 생성합니다.

**파라미터:**
- `text` (str, optional): 노트 내용
- `title` (str, optional): 노트 제목
- `notebook` (str, optional): 노트북 이름
- `tags` (List[str], optional): 태그 목록
- `markdown` (bool, optional): 마크다운 렌더링 여부 (기본값: True)

**노트 속성:**
- `pinned` (bool, optional): 노트 고정 여부
- `favorite` (bool, optional): 즐겨찾기 여부
- `starred` (bool, optional): 별표 표시 여부
- `color` (str, optional): 노트 색상 (red, blue, green, yellow, purple, gray, orange, pink)
- `priority` (str, optional): 우선순위 (high, medium, low, urgent)

**시간 관련:**
- `reminder` (str, optional): 알림 시간 (ISO 8601 형식 또는 자연어)
- `due_date` (str, optional): 마감일 (ISO 8601 형식)
- `created_date` (str, optional): 생성일 지정
- `modified_date` (str, optional): 수정일 지정

**메타데이터:**
- `author` (str, optional): 작성자 정보
- `source` (str, optional): 출처 정보
- `url` (str, optional): 관련 URL 링크
- `location` (str, optional): 위치 정보 또는 GPS 좌표
- `template` (str, optional): 사용할 템플릿 이름
- `folder` (str, optional): 폴더 경로
- `category` (str, optional): 카테고리 분류

**첨부파일:**
- `attachment` (str, optional): 단일 첨부파일 경로
- `attachments` (List[str], optional): 여러 첨부파일 경로 목록

**보안 및 접근 제어:**
- `encrypted` (bool, optional): 암호화 여부
- `password` (str, optional): 노트 비밀번호
- `readonly` (bool, optional): 읽기 전용 여부
- `shared` (bool, optional): 공유 여부
- `public` (bool, optional): 공개 여부

**형식 및 인코딩:**
- `format` (str, optional): 파일 형식 (markdown, html, txt, rtf)
- `encoding` (str, optional): 텍스트 인코딩 (utf-8, utf-16 등)

**콜백 URL:**
- `x_success` (str, optional): 성공시 콜백 URL
- `x_error` (str, optional): 실패시 콜백 URL
- `x_cancel` (str, optional): 취소시 콜백 URL

**반환값:** `bool` - 실행 성공 여부

**예제:**
```python
client = UpNoteClient()

# 기본 노트 생성
client.create_note(
    title="회의 노트",
    text="오늘 회의 내용을 정리합니다.",
    tags=["회의", "업무"]
)

# 고급 설정 노트 생성
client.create_note(
    title="중요 프로젝트",
    text="# 프로젝트 개요\n\n중요한 프로젝트입니다.",
    notebook="업무",
    priority="high",
    pinned=True,
    color="red",
    due_date="2024-12-31",
    reminder="2024-12-30T09:00:00"
)
```

#### `open_note(**kwargs) -> bool`
기존 노트를 엽니다.

**파라미터:**
- `note_id` (str, optional): 열 노트 ID
- `title` (str, optional): 노트 제목으로 검색하여 열기
- `edit` (bool, optional): 편집 모드로 열기 여부
- `x_success` (str, optional): 성공시 콜백 URL
- `x_error` (str, optional): 실패시 콜백 URL
- `x_cancel` (str, optional): 취소시 콜백 URL

**예제:**
```python
# ID로 노트 열기
client.open_note(note_id="12345")

# 제목으로 노트 찾아서 편집 모드로 열기
client.open_note(title="회의 노트", edit=True)
```

### 특수 노트 생성

#### `create_markdown_note(**kwargs) -> bool`
마크다운에 최적화된 노트를 생성합니다.

**파라미터:**
- `title` (str): 노트 제목
- `content` (str): 마크다운 콘텐츠
- `notebook` (str, optional): 노트북 이름
- `tags` (List[str], optional): 태그 목록
- `add_timestamp` (bool): 타임스탬프 추가 여부
- `pinned` (bool, optional): 노트 고정 여부
- `favorite` (bool, optional): 즐겨찾기 여부
- `color` (str, optional): 노트 색상
- `reminder` (str, optional): 알림 시간

**예제:**
```python
client.create_markdown_note(
    title="마크다운 노트",
    content="# 제목\n\n**굵은 글씨**와 *기울임*",
    add_timestamp=True,
    color="blue"
)
```

#### `create_task_note(**kwargs) -> bool`
할 일 목록이 있는 노트를 생성합니다.

**파라미터:**
- `title` (str): 노트 제목
- `tasks` (List[str]): 할 일 목록
- `notebook` (str, optional): 노트북 이름
- `due_date` (str, optional): 마감일
- `priority` (str): 우선순위 (기본값: "medium")
- `tags` (List[str], optional): 태그 목록
- `reminder` (str, optional): 알림 시간

**예제:**
```python
client.create_task_note(
    title="주간 업무",
    tasks=["보고서 작성", "회의 참석", "코드 리뷰"],
    due_date="2024-01-31",
    priority="high"
)
```

#### `create_meeting_note(**kwargs) -> bool`
회의록 노트를 생성합니다.

**파라미터:**
- `title` (str): 회의 제목
- `date` (str): 회의 일시
- `attendees` (List[str]): 참석자 목록
- `agenda` (List[str]): 안건 목록
- `notebook` (str, optional): 노트북 이름
- `location` (str, optional): 회의 장소
- `tags` (List[str], optional): 태그 목록

**예제:**
```python
client.create_meeting_note(
    title="팀 미팅",
    date="2024-01-25 14:00",
    attendees=["김팀장", "박개발", "이디자인"],
    agenda=["프로젝트 진행상황", "다음 스프린트 계획"],
    location="회의실 A"
)
```

#### `create_project_note(**kwargs) -> bool`
프로젝트 계획 노트를 생성합니다.

**파라미터:**
- `project_name` (str): 프로젝트 이름
- `description` (str): 프로젝트 설명
- `milestones` (List[str]): 마일스톤 목록
- `team_members` (List[str]): 팀 멤버 목록
- `due_date` (str, optional): 프로젝트 마감일
- `notebook` (str, optional): 노트북 이름
- `priority` (str): 우선순위 (기본값: "medium")

**예제:**
```python
client.create_project_note(
    project_name="웹사이트 리뉴얼",
    description="기존 웹사이트의 UI/UX 개선",
    milestones=["기획", "디자인", "개발", "테스트"],
    team_members=["기획자", "디자이너", "개발자"],
    due_date="2024-06-30"
)
```

#### `create_daily_note(**kwargs) -> bool`
일일 노트를 생성합니다.

**파라미터:**
- `date` (str, optional): 날짜 (기본값: 오늘)
- `mood` (str, optional): 기분
- `weather` (str, optional): 날씨
- `goals` (List[str], optional): 오늘의 목표
- `reflections` (str, optional): 하루 돌아보기
- `notebook` (str, optional): 노트북 이름

**예제:**
```python
client.create_daily_note(
    mood="😊 좋음",
    weather="☀️ 맑음",
    goals=["운동하기", "독서하기", "프로젝트 진행"],
    reflections="오늘은 생산적인 하루였다."
)
```

### 검색 및 탐색

#### `search_notes(**kwargs) -> bool`
노트를 검색합니다.

**파라미터:**
- `query` (str): 검색어
- `notebook` (str, optional): 특정 노트북에서만 검색
- `tags` (List[str], optional): 특정 태그로 필터링
- `limit` (int, optional): 검색 결과 제한
- `x_success` (str, optional): 성공시 콜백 URL
- `x_error` (str, optional): 실패시 콜백 URL
- `x_cancel` (str, optional): 취소시 콜백 URL

**예제:**
```python
# 기본 검색
client.search_notes("프로젝트")

# 고급 검색
client.search_notes(
    query="회의",
    notebook="업무",
    tags=["중요", "진행중"],
    limit=10
)
```

### 노트북 관리

#### `create_notebook(**kwargs) -> bool`
새로운 노트북을 생성합니다.

**파라미터:**
- `name` (str): 노트북 이름
- `color` (str, optional): 노트북 색상
- `parent` (str, optional): 부모 노트북 이름 (하위 노트북 생성시)
- `x_success` (str, optional): 성공시 콜백 URL
- `x_error` (str, optional): 실패시 콜백 URL
- `x_cancel` (str, optional): 취소시 콜백 URL

**예제:**
```python
# 기본 노트북 생성
client.create_notebook("새 프로젝트")

# 색상이 있는 노트북 생성
client.create_notebook("데이터 분석", color="purple")

# 하위 노트북 생성
client.create_notebook("월간 리포트", parent="데이터 분석")
```

#### `open_notebook(**kwargs) -> bool`
노트북을 엽니다.

**파라미터:**
- `name` (str, optional): 노트북 이름
- `notebook_id` (str, optional): 노트북 ID
- `x_success` (str, optional): 성공시 콜백 URL
- `x_error` (str, optional): 실패시 콜백 URL
- `x_cancel` (str, optional): 취소시 콜백 URL

### 파일 작업

#### `import_note(**kwargs) -> bool`
파일에서 노트를 가져옵니다.

**파라미터:**
- `file_path` (str): 가져올 파일 경로
- `notebook` (str, optional): 대상 노트북
- `format_type` (str, optional): 파일 형식 (markdown, txt, html 등)
- `x_success` (str, optional): 성공시 콜백 URL
- `x_error` (str, optional): 실패시 콜백 URL
- `x_cancel` (str, optional): 취소시 콜백 URL

#### `export_note(**kwargs) -> bool`
노트를 내보냅니다.

**파라미터:**
- `note_id` (str, optional): 내보낼 노트 ID
- `title` (str, optional): 노트 제목으로 검색
- `format_type` (str): 내보낼 형식 (기본값: "markdown")
- `destination` (str, optional): 저장 경로
- `x_success` (str, optional): 성공시 콜백 URL
- `x_error` (str, optional): 실패시 콜백 URL
- `x_cancel` (str, optional): 취소시 콜백 URL

### 기타 기능

#### `quick_note(**kwargs) -> bool`
빠른 노트를 추가합니다.

**파라미터:**
- `text` (str): 추가할 텍스트
- `append` (bool, optional): 기존 노트 끝에 추가
- `prepend` (bool, optional): 기존 노트 앞에 추가
- `x_success` (str, optional): 성공시 콜백 URL
- `x_error` (str, optional): 실패시 콜백 URL

#### `open_upnote(**kwargs) -> bool`
UpNote 앱을 엽니다.

**파라미터:**
- `x_success` (str, optional): 성공시 콜백 URL
- `x_error` (str, optional): 실패시 콜백 URL

#### `debug_url(action: str, params: Dict[str, Any]) -> str`
디버깅용으로 생성될 URL을 반환합니다 (실제로 열지 않음).

**파라미터:**
- `action` (str): 액션 (예: "note/new", "search")
- `params` (Dict[str, Any]): URL 파라미터

**반환값:** `str` - 생성된 URL

---

## UpNoteHelper 메서드

### `format_markdown_content(content: str, add_timestamp: bool = False, add_separator: bool = False) -> str`
마크다운 콘텐츠를 포맷팅합니다.

**파라미터:**
- `content` (str): 원본 콘텐츠
- `add_timestamp` (bool): 타임스탬프 추가 여부
- `add_separator` (bool): 구분선 추가 여부

**반환값:** `str` - 포맷팅된 콘텐츠

### `create_checklist(items: List[str]) -> str`
체크리스트를 생성합니다.

**파라미터:**
- `items` (List[str]): 체크리스트 항목들

**반환값:** `str` - 마크다운 체크리스트

**예제:**
```python
checklist = UpNoteHelper.create_checklist([
    "할 일 1",
    "할 일 2", 
    "할 일 3"
])
# 결과: "- [ ] 할 일 1\n- [ ] 할 일 2\n- [ ] 할 일 3"
```

### `create_table(headers: List[str], rows: List[List[str]]) -> str`
마크다운 테이블을 생성합니다.

**파라미터:**
- `headers` (List[str]): 테이블 헤더
- `rows` (List[List[str]]): 테이블 행 데이터

**반환값:** `str` - 마크다운 테이블

**예제:**
```python
table = UpNoteHelper.create_table(
    headers=["이름", "나이", "직업"],
    rows=[
        ["김철수", "30", "개발자"],
        ["이영희", "25", "디자이너"]
    ]
)
```

---

## 지원하는 색상

- `red`: 빨간색 (긴급, 중요)
- `blue`: 파란색 (정보, 계획)
- `green`: 녹색 (완료, 성공)
- `yellow`: 노란색 (주의, 대기)
- `purple`: 보라색 (창작, 아이디어)
- `gray`: 회색 (보관, 참고)
- `orange`: 주황색 (경고, 알림)
- `pink`: 분홍색 (개인, 취미)

## 우선순위 레벨

- `urgent`: 긴급
- `high`: 높음
- `medium`: 보통 (기본값)
- `low`: 낮음

## 날짜 형식

### ISO 8601 형식
- `2024-01-25T14:30:00` (날짜와 시간)
- `2024-01-25` (날짜만)

### 자연어 형식 (reminder에서 지원)
- `"tomorrow 2pm"`
- `"next friday"`
- `"in 1 hour"`
- `"in 30 minutes"`