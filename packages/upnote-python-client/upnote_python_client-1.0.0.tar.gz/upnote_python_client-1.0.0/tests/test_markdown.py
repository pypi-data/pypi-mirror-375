"""
마크다운 테스트 스크립트
UpNote에서 마크다운이 제대로 렌더링되는지 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 패키지 import 시도
try:
    from upnote_python_client import UpNoteClient, UpNoteHelper
except ImportError:
    # 개발 환경에서 실행할 때 - 직접 모듈 로드
    import importlib.util
    import os
    
    # upnote_python_client/__init__.py 파일 경로
    module_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              'upnote_python_client', '__init__.py')
    
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location("upnote_python_client", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        UpNoteClient = module.UpNoteClient
        UpNoteHelper = module.UpNoteHelper
    else:
        raise ImportError("upnote_python_client 모듈을 찾을 수 없습니다. 'pip install -e .' 를 실행해주세요.")


def test_markdown_features():
    """다양한 마크다운 기능 테스트"""
    client = UpNoteClient()
    
    # 1. 기본 마크다운 테스트
    print("1. 기본 마크다운 테스트...")
    basic_markdown = """# 제목 1
## 제목 2
### 제목 3

**굵은 글씨**와 *기울임 글씨*

`인라인 코드`

```python
# 코드 블록
def hello():
    print("Hello UpNote!")
```

> 인용문입니다.

- 목록 항목 1
- 목록 항목 2
  - 하위 항목 1
  - 하위 항목 2

1. 번호 목록 1
2. 번호 목록 2

[링크](https://example.com)

---

구분선 위아래
"""
    
    success = client.create_markdown_note(
        title="마크다운 기본 기능 테스트",
        content=basic_markdown,
        tags=["테스트", "마크다운"],
        add_timestamp=True
    )
    print(f"기본 마크다운 노트 생성: {'성공' if success else '실패'}")
    
    # 2. 체크리스트 테스트
    print("\n2. 체크리스트 테스트...")
    checklist_content = """# 프로젝트 할 일 목록

## 개발 작업
{checklist}

## 완료된 작업
- [x] 프로젝트 초기 설정
- [x] 기본 구조 설계
- [x] 개발 환경 구축
""".format(
        checklist=UpNoteHelper.create_checklist([
            "API 설계 및 구현",
            "프론트엔드 UI 개발",
            "데이터베이스 스키마 설계",
            "테스트 코드 작성",
            "문서화 작업"
        ])
    )
    
    success = client.create_markdown_note(
        title="프로젝트 체크리스트",
        content=checklist_content,
        notebook="프로젝트 관리",
        tags=["할일", "체크리스트", "프로젝트"]
    )
    print(f"체크리스트 노트 생성: {'성공' if success else '실패'}")
    
    # 3. 테이블 테스트
    print("\n3. 테이블 테스트...")
    
    # 프로젝트 현황 테이블
    project_table = UpNoteHelper.create_table(
        headers=["기능", "담당자", "진행률", "마감일", "상태"],
        rows=[
            ["사용자 인증", "김개발", "90%", "2024-01-15", "🟡 진행중"],
            ["상품 관리", "박코더", "60%", "2024-01-20", "🟡 진행중"],
            ["주문 시스템", "이프로", "30%", "2024-01-25", "🔴 지연"],
            ["결제 연동", "최개발", "0%", "2024-01-30", "⚪ 대기"]
        ]
    )
    
    # 기술 스택 테이블
    tech_table = UpNoteHelper.create_table(
        headers=["분야", "기술", "버전", "용도"],
        rows=[
            ["Frontend", "React", "18.2.0", "UI 프레임워크"],
            ["Backend", "Node.js", "18.17.0", "서버 런타임"],
            ["Database", "PostgreSQL", "15.3", "메인 데이터베이스"],
            ["Cache", "Redis", "7.0", "세션 및 캐시"],
            ["Deploy", "Docker", "24.0", "컨테이너화"]
        ]
    )
    
    table_content = f"""# 프로젝트 현황 대시보드

## 📊 개발 진행 현황
{project_table}

## 🛠 기술 스택
{tech_table}

## 📈 주요 지표
- **전체 진행률**: 45%
- **완료된 기능**: 0개
- **진행중인 기능**: 2개
- **지연된 기능**: 1개

## 🚨 주의사항
> **주문 시스템**이 지연되고 있습니다. 리소스 재배치가 필요할 수 있습니다.

## 📅 다음 마일스톤
- [ ] 사용자 인증 완료 (1/15)
- [ ] 상품 관리 완료 (1/20)
- [ ] 주문 시스템 일정 재조정
"""
    
    success = client.create_markdown_note(
        title="프로젝트 현황 대시보드",
        content=table_content,
        notebook="프로젝트 관리",
        tags=["현황", "테이블", "대시보드"]
    )
    print(f"테이블 노트 생성: {'성공' if success else '실패'}")
    
    # 4. 복합 마크다운 테스트
    print("\n4. 복합 마크다운 테스트...")
    
    current_time = UpNoteHelper.format_markdown_content("", add_timestamp=True).split("*작성일: ")[1].split("*")[0]
    
    js_code = '''```javascript
// 이미지 레이지 로딩 구현 필요
const LazyImage = (props) => {
  const [loaded, setLoaded] = useState(false);
  
  return (
    <img 
      src={loaded ? props.src : placeholder}
      alt={props.alt}
      onLoad={() => setLoaded(true)}
    />
  );
};
```'''

    sql_code = '''```sql
-- 검색 성능 개선을 위한 인덱스 추가
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at);
```'''

    meeting_notes = f"""# 📋 주간 팀 미팅 노트

**일시**: {current_time}
**참석자**: 김팀장, 박개발, 이디자인, 최기획

## 🎯 주요 안건

### 1. 스프린트 리뷰
- ✅ **완료된 작업**
  - 사용자 로그인/회원가입 기능
  - 기본 UI 컴포넌트 라이브러리
  - API 문서 초안

- ⏳ **진행중인 작업**
  - 상품 카탈로그 페이지
  - 장바구니 기능
  - 결제 시스템 연동

### 2. 기술적 이슈

#### 성능 최적화
{js_code}

#### 데이터베이스 인덱싱
{sql_code}

### 3. 액션 아이템
{UpNoteHelper.create_checklist([
    "이미지 최적화 라이브러리 도입 검토 (박개발)",
    "데이터베이스 인덱스 적용 (김팀장)",
    "모바일 반응형 테스트 (이디자인)",
    "사용자 테스트 시나리오 작성 (최기획)"
])}

## 📊 스프린트 메트릭스

{UpNoteHelper.create_table(
    headers=["지표", "목표", "실제", "달성률"],
    rows=[
        ["스토리 포인트", "40", "35", "87.5%"],
        ["버그 수정", "15", "18", "120%"],
        ["코드 커버리지", "80%", "75%", "93.8%"],
        ["사용자 만족도", "4.5", "4.2", "93.3%"]
    ]
)}

## 🔮 다음 스프린트 계획

### 우선순위 높음
1. **결제 시스템 완성** - 매출 직결
2. **모바일 최적화** - 사용자 경험 개선
3. **성능 튜닝** - 로딩 시간 단축

### 우선순위 중간
- 관리자 대시보드 개선
- 알림 시스템 구축
- 다국어 지원 준비

---

> 💡 **회고**: 이번 스프린트는 전반적으로 목표를 달성했으나, 성능 이슈에 더 집중이 필요합니다.

**다음 미팅**: 2024년 1월 22일 (월) 오후 2시
"""
    
    success = client.create_markdown_note(
        title=f"주간 팀 미팅 - {UpNoteHelper.format_markdown_content('', add_timestamp=True).split('*작성일: ')[1].split('*')[0].split()[0]}",
        content=meeting_notes,
        notebook="회의록",
        tags=["회의", "팀", "스프린트", "리뷰"]
    )
    print(f"복합 마크다운 노트 생성: {'성공' if success else '실패'}")


def debug_urls():
    """생성되는 URL들을 확인"""
    print("\n=== URL 디버깅 ===")
    client = UpNoteClient()
    
    test_cases = [
        {
            "name": "기본 텍스트",
            "params": {"text": "Hello World", "title": "Test"}
        },
        {
            "name": "마크다운 헤더",
            "params": {"text": "# 제목\n## 부제목", "title": "Markdown Test"}
        },
        {
            "name": "마크다운 리스트",
            "params": {"text": "- [ ] 할일 1\n- [x] 완료된 일", "title": "Checklist"}
        },
        {
            "name": "코드 블록",
            "params": {"text": "```python\nprint('hello')\n```", "title": "Code"}
        }
    ]
    
    for case in test_cases:
        url = client.debug_url("note/new", case["params"])
        print(f"\n{case['name']}:")
        print(f"URL: {url}")


if __name__ == "__main__":
    test_markdown_features()
    debug_urls()