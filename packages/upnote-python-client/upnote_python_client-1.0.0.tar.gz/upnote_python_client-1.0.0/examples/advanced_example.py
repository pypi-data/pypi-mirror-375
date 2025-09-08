#!/usr/bin/env python3
"""
UpNote 고급 기능 사용 예제
최신 URL scheme 파라미터들을 활용한 예제
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
from datetime import datetime, timedelta


def advanced_note_creation():
    """고급 노트 생성 기능 테스트"""
    client = UpNoteClient()
    
    print("=== 고급 노트 생성 기능 테스트 ===")
    
    # 1. 색상과 고정이 있는 중요한 노트
    print("1. 중요한 노트 생성 (빨간색, 고정, 즐겨찾기)...")
    important_content = """# 🚨 긴급 공지사항

## 서버 점검 안내
- **일시**: 2024년 1월 20일 (토) 02:00 ~ 06:00
- **영향**: 모든 서비스 일시 중단
- **준비사항**: 데이터 백업 완료

## 체크리스트
{checklist}

> ⚠️ **주의**: 점검 시간 동안 서비스 이용이 불가능합니다.
""".format(
        checklist=UpNoteHelper.create_checklist([
            "사용자 공지 발송",
            "데이터베이스 백업",
            "서버 상태 모니터링",
            "점검 완료 후 서비스 확인"
        ])
    )
    
    success = client.create_markdown_note(
        title="🚨 서버 점검 공지",
        content=important_content,
        notebook="운영",
        tags=["긴급", "공지", "서버점검"],
        pinned=True,
        favorite=True,
        color="red",
        reminder="2024-01-19T18:00:00"
    )
    print(f"중요한 노트 생성: {'성공' if success else '실패'}")
    
    # 2. 프로젝트 계획 노트 (파란색)
    print("\n2. 프로젝트 계획 노트 생성 (파란색)...")
    project_content = """# 📋 Q1 프로젝트 계획

## 목표
새로운 기능 출시를 통한 사용자 경험 개선

## 주요 마일스톤
{milestones}

## 팀 구성
{team_table}

## 예산 계획
- 개발비: $50,000
- 마케팅: $20,000
- 운영비: $10,000
- **총합**: $80,000
""".format(
        milestones=UpNoteHelper.create_checklist([
            "요구사항 분석 완료 (1/15)",
            "UI/UX 디자인 완료 (1/30)",
            "백엔드 API 개발 (2/15)",
            "프론트엔드 개발 (2/28)",
            "테스트 및 QA (3/15)",
            "배포 및 런칭 (3/31)"
        ]),
        team_table=UpNoteHelper.create_table(
            headers=["역할", "담당자", "경험", "할당률"],
            rows=[
                ["PM", "김프로", "5년", "100%"],
                ["Backend", "박개발", "3년", "100%"],
                ["Frontend", "이코더", "4년", "100%"],
                ["Designer", "최디자인", "2년", "50%"],
                ["QA", "정테스터", "3년", "70%"]
            ]
        )
    )
    
    success = client.create_markdown_note(
        title="📋 Q1 프로젝트 계획",
        content=project_content,
        notebook="프로젝트",
        tags=["계획", "Q1", "프로젝트"],
        color="blue",
        favorite=True
    )
    print(f"프로젝트 계획 노트 생성: {'성공' if success else '실패'}")
    
    # 3. 회의록 템플릿 (녹색)
    print("\n3. 회의록 템플릿 생성 (녹색)...")
    meeting_template = """# 📝 회의록 템플릿

**회의명**: [회의 제목]
**일시**: [날짜 및 시간]
**장소**: [회의 장소/온라인]
**참석자**: [참석자 목록]

## 📋 안건
1. [안건 1]
2. [안건 2]
3. [안건 3]

## 💬 논의 내용
### [안건 1]
- 논의 내용 작성

### [안건 2]
- 논의 내용 작성

## ✅ 결정 사항
- [결정 사항 1]
- [결정 사항 2]

## 📝 액션 아이템
{action_items}

## 📅 다음 회의
**일정**: [다음 회의 일정]
**안건**: [다음 회의 주요 안건]
""".format(
        action_items=UpNoteHelper.create_checklist([
            "[작업 내용] (담당자, 마감일)",
            "[작업 내용] (담당자, 마감일)",
            "[작업 내용] (담당자, 마감일)"
        ])
    )
    
    success = client.create_markdown_note(
        title="📝 회의록 템플릿",
        content=meeting_template,
        notebook="템플릿",
        tags=["템플릿", "회의록"],
        color="green"
    )
    print(f"회의록 템플릿 생성: {'성공' if success else '실패'}")


def test_advanced_features():
    """고급 기능들 테스트"""
    client = UpNoteClient()
    
    print("\n=== 고급 기능 테스트 ===")
    
    # 1. 노트북 생성 (색상 지정)
    print("1. 색상이 있는 노트북 생성...")
    success = client.create_notebook(
        name="📊 데이터 분석",
        color="purple"
    )
    print(f"노트북 생성: {'성공' if success else '실패'}")
    
    # 2. 하위 노트북 생성
    print("\n2. 하위 노트북 생성...")
    success = client.create_notebook(
        name="월간 리포트",
        parent="📊 데이터 분석",
        color="yellow"
    )
    print(f"하위 노트북 생성: {'성공' if success else '실패'}")
    
    # 3. 노트북 열기
    print("\n3. 노트북 열기...")
    success = client.open_notebook(name="📊 데이터 분석")
    print(f"노트북 열기: {'성공' if success else '실패'}")
    
    # 4. 고급 검색 (노트북과 태그 필터링)
    print("\n4. 고급 검색 실행...")
    success = client.search_notes(
        query="프로젝트",
        notebook="프로젝트",
        tags=["계획", "중요"],
        limit=10
    )
    print(f"고급 검색: {'성공' if success else '실패'}")
    
    # 5. 편집 모드로 노트 열기
    print("\n5. 편집 모드로 노트 열기...")
    success = client.open_note(
        title="📋 Q1 프로젝트 계획",
        edit=True
    )
    print(f"편집 모드 노트 열기: {'성공' if success else '실패'}")
    
    # 6. 빠른 노트 추가
    print("\n6. 빠른 노트 추가...")
    quick_text = f"""
---
**{datetime.now().strftime('%Y-%m-%d %H:%M')}** 추가 메모:
- 새로운 아이디어: AI 기반 자동 태그 생성
- 참고 링크: https://example.com/ai-tagging
"""
    success = client.quick_note(
        text=quick_text,
        append=True
    )
    print(f"빠른 노트 추가: {'성공' if success else '실패'}")


def test_url_generation():
    """URL 생성 테스트"""
    print("\n=== URL 생성 테스트 ===")
    client = UpNoteClient()
    
    # 다양한 파라미터 조합 테스트
    test_cases = [
        {
            "name": "기본 마크다운 노트",
            "action": "note/new",
            "params": {
                "title": "테스트 노트",
                "text": "# 제목\n\n**굵은 글씨**",
                "markdown": True,
                "tags": ["테스트", "마크다운"]
            }
        },
        {
            "name": "고정된 중요 노트",
            "action": "note/new",
            "params": {
                "title": "중요 공지",
                "text": "중요한 내용입니다.",
                "pinned": True,
                "favorite": True,
                "color": "red",
                "notebook": "공지사항"
            }
        },
        {
            "name": "알림이 있는 노트",
            "action": "note/new",
            "params": {
                "title": "미팅 준비",
                "text": "미팅 준비 사항들",
                "reminder": "2024-01-20T14:00:00",
                "tags": ["미팅", "준비"]
            }
        },
        {
            "name": "고급 검색",
            "action": "search",
            "params": {
                "query": "프로젝트 계획",
                "notebook": "업무",
                "tags": ["중요", "계획"],
                "limit": 5
            }
        }
    ]
    
    for case in test_cases:
        url = client.debug_url(case["action"], case["params"])
        print(f"\n{case['name']}:")
        print(f"URL: {url}")
        print(f"길이: {len(url)} 문자")


if __name__ == "__main__":
    advanced_note_creation()
    test_advanced_features()
    test_url_generation()