#!/usr/bin/env python3
"""
UpNote URL Scheme 클라이언트 사용 예제
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
from datetime import datetime


def main():
    # UpNote 클라이언트 초기화 (API 키 불필요)
    client = UpNoteClient()
    
    try:
        # 1. 기본 노트 생성
        print("1. 기본 노트 생성...")
        success = client.create_note(
            text="- 프로젝트 계획서 작성\n- 회의 참석\n- 코드 리뷰",
            title="오늘의 할 일"
        )
        print(f"노트 생성 {'성공' if success else '실패'}")
        
        # 2. 상세 설정이 포함된 노트 생성
        print("\n2. 상세 설정 노트 생성...")
        
        # 체크리스트 생성
        checklist_items = ["Python 스크립트 작성", "테스트 코드 작성", "문서화"]
        checklist_content = UpNoteHelper.create_checklist(checklist_items)
        
        # 타임스탬프가 포함된 콘텐츠
        formatted_content = UpNoteHelper.format_markdown_content(
            f"# 개발 작업 목록\n\n{checklist_content}",
            add_timestamp=True,
            add_separator=True
        )
        
        success = client.create_note(
            text=formatted_content,
            title="개발 프로젝트 - UpNote URL Scheme",
            notebook="개발 프로젝트",
            tags=["개발", "Python", "URL-Scheme", "프로젝트"]
        )
        print(f"상세 노트 생성 {'성공' if success else '실패'}")
        
        # 3. 테이블이 포함된 노트 생성
        print("\n3. 테이블 포함 노트 생성...")
        
        # 테이블 데이터
        headers = ["작업", "담당자", "마감일", "상태"]
        rows = [
            ["API 설계", "김개발", "2024-01-15", "진행중"],
            ["UI 구현", "박디자인", "2024-01-20", "대기"],
            ["테스트", "이테스터", "2024-01-25", "대기"]
        ]
        
        table_content = UpNoteHelper.create_table(headers, rows)
        table_note_content = f"# 프로젝트 진행 현황\n\n{table_content}"
        
        success = client.create_note(
            text=table_note_content,
            title="프로젝트 진행 현황",
            tags=["프로젝트", "현황", "테이블"]
        )
        print(f"테이블 노트 생성 {'성공' if success else '실패'}")
        
        # 4. 노트북 생성
        print("\n4. 노트북 생성...")
        success = client.create_notebook("새 프로젝트")
        print(f"노트북 생성 {'성공' if success else '실패'}")
        
        # 5. 노트 검색
        print("\n5. 노트 검색...")
        success = client.search_notes("개발")
        print(f"검색 실행 {'성공' if success else '실패'}")
        
        # 6. UpNote 앱 열기
        print("\n6. UpNote 앱 열기...")
        success = client.open_upnote()
        print(f"앱 열기 {'성공' if success else '실패'}")
        
        # 7. 복잡한 노트 생성 예제
        print("\n7. 복잡한 노트 생성...")
        
        # 회의록 템플릿
        meeting_content = """# 팀 회의록
        
**일시:** {date}
**참석자:** 김개발, 박디자인, 이기획

## 안건
1. 프로젝트 진행 상황 점검
2. 다음 스프린트 계획
3. 기술적 이슈 논의

## 논의 내용
- 현재 진행률: 60%
- 주요 완료 작업:
  - 사용자 인증 시스템
  - 기본 UI 컴포넌트
  - 데이터베이스 스키마

## 액션 아이템
{checklist}

## 다음 회의
**일정:** 다음 주 금요일 오후 2시
        """.format(
            date=datetime.now().strftime("%Y년 %m월 %d일"),
            checklist=UpNoteHelper.create_checklist([
                "API 문서 업데이트 (김개발)",
                "UI 목업 완성 (박디자인)", 
                "테스트 시나리오 작성 (이기획)"
            ])
        )
        
        success = client.create_note(
            text=meeting_content,
            title=f"팀 회의록 - {datetime.now().strftime('%Y.%m.%d')}",
            notebook="회의록",
            tags=["회의", "팀", "프로젝트"]
        )
        print(f"회의록 생성 {'성공' if success else '실패'}")
        
    except Exception as e:
        print(f"오류 발생: {str(e)}")


def demo_url_generation():
    """URL 생성 데모"""
    print("\n=== URL 생성 데모 ===")
    client = UpNoteClient()
    
    # 다양한 URL 생성 예제
    examples = [
        {
            "name": "간단한 노트",
            "params": {"text": "Hello UpNote!"}
        },
        {
            "name": "제목과 내용이 있는 노트",
            "params": {"title": "테스트 노트", "text": "이것은 테스트입니다."}
        },
        {
            "name": "태그가 있는 노트",
            "params": {
                "title": "태그 테스트",
                "text": "태그 기능을 테스트합니다.",
                "tags": ["테스트", "개발"]
            }
        },
        {
            "name": "노트북 지정 노트",
            "params": {
                "title": "프로젝트 노트",
                "text": "프로젝트 관련 내용",
                "notebook": "개발 프로젝트",
                "tags": ["프로젝트"]
            }
        }
    ]
    
    for example in examples:
        url = client._build_url("note/new", example["params"])
        print(f"\n{example['name']}:")
        print(f"URL: {url}")


if __name__ == "__main__":
    main()
    demo_url_generation()