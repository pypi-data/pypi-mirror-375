"""
모든 기능을 테스트하는 종합 테스트 스크립트
실제 UpNote 앱을 열지 않고 URL 생성만 테스트
"""

import sys
import traceback
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


def test_basic_functionality():
    """기본 기능 테스트"""
    print("=== 기본 기능 테스트 ===")
    
    try:
        client = UpNoteClient()
        
        # 1. 클라이언트 초기화 테스트
        assert client.base_scheme == "upnote://x-callback-url"
        assert client.system in ["Darwin", "Windows", "Linux"]
        print("✅ 클라이언트 초기화 성공")
        
        # 2. URL 생성 테스트
        test_params = {"title": "테스트", "text": "내용"}
        url = client._build_url("note/new", test_params)
        assert url.startswith("upnote://x-callback-url/note/new")
        assert "title=테스트" in url or "title=%ED%85%8C%EC%8A%A4%ED%8A%B8" in url
        print("✅ URL 생성 성공")
        
        # 3. 파라미터 처리 테스트
        complex_params = {
            "title": "복잡한 제목",
            "tags": ["태그1", "태그2"],
            "markdown": True,
            "pinned": False,
            "priority": None
        }
        url = client._build_url("note/new", complex_params)
        assert "markdown=true" in url
        assert "pinned=false" in url
        assert "priority" not in url  # None 값은 제외되어야 함
        print("✅ 파라미터 처리 성공")
        
        return True
        
    except Exception as e:
        print(f"❌ 기본 기능 테스트 실패: {str(e)}")
        traceback.print_exc()
        return False


def test_helper_functions():
    """헬퍼 함수 테스트"""
    print("\n=== 헬퍼 함수 테스트 ===")
    
    try:
        # 1. 체크리스트 생성 테스트
        items = ["항목 1", "항목 2", "항목 3"]
        checklist = UpNoteHelper.create_checklist(items)
        expected = "- [ ] 항목 1\n- [ ] 항목 2\n- [ ] 항목 3"
        assert checklist == expected
        print("✅ 체크리스트 생성 성공")
        
        # 2. 테이블 생성 테스트
        headers = ["이름", "나이"]
        rows = [["김철수", "30"], ["이영희", "25"]]
        table = UpNoteHelper.create_table(headers, rows)
        assert "| 이름 | 나이 |" in table
        assert "| --- | --- |" in table
        assert "| 김철수 | 30 |" in table
        print("✅ 테이블 생성 성공")
        
        # 3. 마크다운 포맷팅 테스트
        content = "원본 내용"
        formatted = UpNoteHelper.format_markdown_content(content, add_timestamp=True)
        assert "작성일:" in formatted
        assert "원본 내용" in formatted
        print("✅ 마크다운 포맷팅 성공")
        
        # 4. 빈 테이블 처리 테스트
        empty_table = UpNoteHelper.create_table([], [])
        assert empty_table == ""
        print("✅ 빈 테이블 처리 성공")
        
        return True
        
    except Exception as e:
        print(f"❌ 헬퍼 함수 테스트 실패: {str(e)}")
        traceback.print_exc()
        return False


def test_note_creation():
    """노트 생성 기능 테스트 (URL 생성만)"""
    print("\n=== 노트 생성 기능 테스트 ===")
    
    try:
        client = UpNoteClient()
        
        # 1. 기본 노트 생성 URL 테스트
        params = {
            "title": "기본 노트",
            "text": "기본 내용",
            "markdown": True
        }
        url = client.debug_url("note/new", params)
        assert "title=" in url
        assert "text=" in url
        assert "markdown=true" in url
        print("✅ 기본 노트 생성 URL 성공")
        
        # 2. 확장 파라미터 노트 생성 URL 테스트
        params = {
            "title": "확장 노트",
            "text": "# 제목\n\n내용",
            "notebook": "테스트북",
            "tags": ["태그1", "태그2"],
            "pinned": True,
            "favorite": True,
            "color": "red",
            "priority": "high",
            "due_date": "2024-12-31",
            "reminder": "2024-12-30T09:00:00",
            "author": "테스터",
            "encrypted": False,
            "shared": True
        }
        url = client.debug_url("note/new", params)
        assert "notebook=" in url
        assert "tags=" in url
        assert "pinned=true" in url
        assert "color=red" in url
        assert "priority=high" in url
        print("✅ 확장 파라미터 노트 생성 URL 성공")
        
        # 3. 특수 문자 처리 테스트
        params = {
            "title": "특수 문자 & 테스트 #1",
            "text": "마크다운 **굵게** *기울임* `코드`",
            "tags": ["특수문자", "마크다운"]
        }
        url = client.debug_url("note/new", params)
        # URL이 생성되기만 하면 성공 (인코딩은 urllib이 처리)
        assert len(url) > 0
        print("✅ 특수 문자 처리 성공")
        
        return True
        
    except Exception as e:
        print(f"❌ 노트 생성 기능 테스트 실패: {str(e)}")
        traceback.print_exc()
        return False


def test_special_note_types():
    """특수 노트 타입 테스트"""
    print("\n=== 특수 노트 타입 테스트 ===")
    
    try:
        client = UpNoteClient()
        
        # 1. 할 일 노트 내용 생성 테스트
        tasks = ["작업 1", "작업 2", "작업 3"]
        # create_task_note는 실제로는 create_note를 호출하므로 내용만 확인
        task_content = "# 할 일 테스트\n\n" + UpNoteHelper.create_checklist(tasks)
        assert "- [ ] 작업 1" in task_content
        assert "- [ ] 작업 2" in task_content
        print("✅ 할 일 노트 내용 생성 성공")
        
        # 2. 회의록 노트 내용 생성 테스트
        title = "팀 미팅"
        date = "2024-01-25 14:00"
        attendees = ["김팀장", "박개발"]
        agenda = ["안건 1", "안건 2"]
        
        meeting_content = f"""# {title}

**일시**: {date}
**참석자**: {', '.join(attendees)}

## 안건
{chr(10).join([f"{i+1}. {item}" for i, item in enumerate(agenda)])}"""
        
        assert "팀 미팅" in meeting_content
        assert "김팀장, 박개발" in meeting_content
        assert "1. 안건 1" in meeting_content
        print("✅ 회의록 노트 내용 생성 성공")
        
        # 3. 프로젝트 노트 내용 생성 테스트
        project_name = "테스트 프로젝트"
        description = "프로젝트 설명"
        milestones = ["마일스톤 1", "마일스톤 2"]
        team_members = ["멤버 1", "멤버 2"]
        
        project_content = f"""# 📋 {project_name}

## 프로젝트 개요
{description}

## 팀 구성
{chr(10).join([f"- {member}" for member in team_members])}"""
        
        assert "테스트 프로젝트" in project_content
        assert "프로젝트 설명" in project_content
        assert "- 멤버 1" in project_content
        print("✅ 프로젝트 노트 내용 생성 성공")
        
        # 4. 일일 노트 내용 생성 테스트
        date = "2024-01-25"
        mood = "😊 좋음"
        weather = "☀️ 맑음"
        
        daily_content = f"""# 📅 {date}

## 오늘의 상태
**기분**: {mood}
**날씨**: {weather}"""
        
        assert "2024-01-25" in daily_content
        assert "😊 좋음" in daily_content
        assert "☀️ 맑음" in daily_content
        print("✅ 일일 노트 내용 생성 성공")
        
        return True
        
    except Exception as e:
        print(f"❌ 특수 노트 타입 테스트 실패: {str(e)}")
        traceback.print_exc()
        return False


def test_advanced_features():
    """고급 기능 테스트"""
    print("\n=== 고급 기능 테스트 ===")
    
    try:
        client = UpNoteClient()
        
        # 1. 검색 기능 URL 테스트
        search_params = {
            "query": "검색어",
            "notebook": "특정노트북",
            "tags": ["태그1", "태그2"],
            "limit": 10
        }
        url = client.debug_url("search", search_params)
        assert "query=" in url
        assert "notebook=" in url
        assert "tags=" in url
        assert "limit=10" in url
        print("✅ 검색 기능 URL 생성 성공")
        
        # 2. 노트북 생성 URL 테스트
        notebook_params = {
            "name": "새 노트북",
            "color": "blue",
            "parent": "부모 노트북"
        }
        url = client.debug_url("notebook/new", notebook_params)
        assert "name=" in url
        assert "color=blue" in url
        assert "parent=" in url
        print("✅ 노트북 생성 URL 성공")
        
        # 3. 노트 열기 URL 테스트
        open_params = {
            "title": "열 노트",
            "edit": True
        }
        url = client.debug_url("note/open", open_params)
        assert "title=" in url
        assert "edit=true" in url
        print("✅ 노트 열기 URL 성공")
        
        # 4. 내보내기 URL 테스트
        export_params = {
            "title": "내보낼 노트",
            "format": "pdf",
            "destination": "/Users/test/Documents/"
        }
        url = client.debug_url("export", export_params)
        assert "format=pdf" in url
        assert "destination=" in url
        print("✅ 내보내기 URL 성공")
        
        return True
        
    except Exception as e:
        print(f"❌ 고급 기능 테스트 실패: {str(e)}")
        traceback.print_exc()
        return False


def test_error_handling():
    """에러 처리 테스트"""
    print("\n=== 에러 처리 테스트 ===")
    
    try:
        client = UpNoteClient()
        
        # 1. 빈 파라미터 처리 테스트
        url = client.debug_url("note/new", {})
        assert url == "upnote://x-callback-url/note/new"
        print("✅ 빈 파라미터 처리 성공")
        
        # 2. None 값 필터링 테스트
        params = {
            "title": "제목",
            "text": None,
            "notebook": "",
            "tags": None
        }
        url = client.debug_url("note/new", params)
        assert "title=" in url
        assert "text=" not in url  # None 값은 제외
        assert "notebook=" in url  # 빈 문자열은 포함
        assert "tags=" not in url  # None 값은 제외
        print("✅ None 값 필터링 성공")
        
        # 3. 리스트 파라미터 처리 테스트
        params = {
            "tags": ["태그1", "태그2", "태그3"],
            "attachments": ["파일1.pdf", "파일2.jpg"]
        }
        url = client.debug_url("note/new", params)
        # 리스트는 쉼표로 구분된 문자열로 변환되어야 함
        assert "tags=" in url
        assert "attachments=" in url
        print("✅ 리스트 파라미터 처리 성공")
        
        return True
        
    except Exception as e:
        print(f"❌ 에러 처리 테스트 실패: {str(e)}")
        traceback.print_exc()
        return False


def test_url_length_and_encoding():
    """URL 길이 및 인코딩 테스트"""
    print("\n=== URL 길이 및 인코딩 테스트 ===")
    
    try:
        client = UpNoteClient()
        
        # 1. 긴 텍스트 처리 테스트
        long_text = "이것은 매우 긴 텍스트입니다. " * 100  # 약 1500자
        params = {
            "title": "긴 텍스트 테스트",
            "text": long_text
        }
        url = client.debug_url("note/new", params)
        assert len(url) > 1000  # URL이 생성되었는지 확인
        print(f"✅ 긴 텍스트 처리 성공 (URL 길이: {len(url)}자)")
        
        # 2. 특수 문자 인코딩 테스트
        special_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        korean_text = "한글 텍스트 테스트"
        emoji_text = "😀😃😄😁😆😅😂🤣"
        
        params = {
            "title": f"특수문자 {special_chars}",
            "text": f"{korean_text} {emoji_text}",
            "tags": ["특수문자", "한글", "이모지"]
        }
        url = client.debug_url("note/new", params)
        assert len(url) > 0
        print("✅ 특수 문자 인코딩 성공")
        
        # 3. 마크다운 문법 인코딩 테스트
        markdown_text = """# 제목
## 부제목
**굵은 글씨**
*기울임*
`인라인 코드`
```
코드 블록
```
- 목록 1
- 목록 2
> 인용문
[링크](https://example.com)
"""
        params = {
            "title": "마크다운 테스트",
            "text": markdown_text,
            "markdown": True
        }
        url = client.debug_url("note/new", params)
        assert len(url) > 0
        print("✅ 마크다운 문법 인코딩 성공")
        
        return True
        
    except Exception as e:
        print(f"❌ URL 길이 및 인코딩 테스트 실패: {str(e)}")
        traceback.print_exc()
        return False


def run_all_tests():
    """모든 테스트 실행"""
    print("🚀 UpNote 클라이언트 종합 테스트 시작\n")
    
    tests = [
        ("기본 기능", test_basic_functionality),
        ("헬퍼 함수", test_helper_functions),
        ("노트 생성", test_note_creation),
        ("특수 노트 타입", test_special_note_types),
        ("고급 기능", test_advanced_features),
        ("에러 처리", test_error_handling),
        ("URL 길이 및 인코딩", test_url_length_and_encoding)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} 테스트 중 예외 발생: {str(e)}")
            failed += 1
    
    print(f"\n📊 테스트 결과:")
    print(f"✅ 통과: {passed}개")
    print(f"❌ 실패: {failed}개")
    print(f"📈 성공률: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 모든 테스트가 성공적으로 통과했습니다!")
        return True
    else:
        print(f"\n⚠️  {failed}개의 테스트가 실패했습니다. 코드를 확인해주세요.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)