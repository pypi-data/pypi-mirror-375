#!/usr/bin/env python3
"""
UpNote 종합 기능 예제
확장된 파라미터들과 특수 노트 생성 기능들을 보여주는 예제
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


def test_extended_parameters():
    """확장된 파라미터들을 테스트"""
    client = UpNoteClient()
    
    print("=== 확장된 파라미터 테스트 ===")
    
    # 1. 모든 파라미터를 사용한 복합 노트
    print("1. 모든 파라미터를 사용한 복합 노트 생성...")
    
    comprehensive_content = """# 🚀 프로젝트 킥오프 미팅

## 프로젝트 개요
새로운 AI 기반 노트 앱 개발 프로젝트

## 주요 기능
- 자동 태그 생성
- 스마트 검색
- 음성 인식
- 다국어 지원

## 기술 스택
{tech_stack}

## 일정
{schedule}

## 팀 역할
{team_roles}

## 예산 계획
- 개발: $100,000
- 마케팅: $50,000
- 운영: $30,000
- **총합**: $180,000

## 위험 요소
- 기술적 복잡성
- 시장 경쟁
- 인력 부족

## 성공 지표
- 사용자 10,000명 달성
- 앱스토어 평점 4.5 이상
- 월 매출 $10,000 달성
""".format(
        tech_stack=UpNoteHelper.create_table(
            headers=["분야", "기술", "버전", "담당자"],
            rows=[
                ["Frontend", "React Native", "0.72", "김모바일"],
                ["Backend", "Node.js", "18.17", "박서버"],
                ["Database", "MongoDB", "6.0", "이디비"],
                ["AI/ML", "TensorFlow", "2.13", "최에이아이"],
                ["Cloud", "AWS", "Latest", "정클라우드"]
            ]
        ),
        schedule=UpNoteHelper.create_checklist([
            "요구사항 분석 (1주차)",
            "시스템 설계 (2-3주차)",
            "프로토타입 개발 (4-6주차)",
            "MVP 개발 (7-12주차)",
            "베타 테스트 (13-14주차)",
            "정식 출시 (15주차)"
        ]),
        team_roles=UpNoteHelper.create_table(
            headers=["이름", "역할", "경험", "책임"],
            rows=[
                ["김팀장", "Project Manager", "10년", "전체 관리"],
                ["박개발", "Lead Developer", "8년", "아키텍처 설계"],
                ["이디자인", "UI/UX Designer", "5년", "사용자 경험"],
                ["최마케팅", "Marketing", "6년", "시장 분석"],
                ["정품질", "QA Engineer", "4년", "품질 보증"]
            ]
        )
    )
    
    success = client.create_note(
        text=comprehensive_content,
        title="🚀 AI 노트앱 프로젝트 킥오프",
        notebook="프로젝트 관리",
        folder="2024/Q1",
        tags=["프로젝트", "킥오프", "AI", "모바일앱"],
        category="업무",
        markdown=True,
        pinned=True,
        favorite=True,
        starred=True,
        color="blue",
        priority="high",
        due_date="2024-06-30",
        reminder="2024-01-22T09:00:00",
        author="프로젝트 매니저",
        source="킥오프 미팅",
        url="https://company.com/projects/ai-note-app",
        shared=True,
        format="markdown",
        encoding="utf-8"
    )
    print(f"복합 노트 생성: {'성공' if success else '실패'}")
    
    # 2. 암호화된 기밀 노트
    print("\n2. 암호화된 기밀 노트 생성...")
    
    confidential_content = """# 🔒 기밀 정보

## 서버 접속 정보
- **호스트**: production.company.com
- **사용자**: admin
- **포트**: 22

## API 키
- **OpenAI**: sk-...
- **AWS**: AKIA...
- **Stripe**: pk_live_...

## 데이터베이스 정보
- **연결 문자열**: mongodb://...
- **백업 위치**: s3://backups/...

⚠️ **주의**: 이 정보는 절대 외부에 공유하지 마세요.
"""
    
    success = client.create_note(
        text=confidential_content,
        title="🔒 서버 및 API 정보",
        notebook="기밀",
        tags=["기밀", "서버", "API", "보안"],
        color="red",
        encrypted=True,
        password="secure123!",
        readonly=False,
        shared=False,
        public=False,
        priority="urgent"
    )
    print(f"기밀 노트 생성: {'성공' if success else '실패'}")
    
    # 3. 위치 정보가 있는 여행 노트
    print("\n3. 위치 정보가 있는 여행 노트 생성...")
    
    travel_content = """# ✈️ 제주도 여행 계획

## 여행 일정
**기간**: 2024년 3월 15일 ~ 3월 18일 (3박 4일)

## 숙소 정보
- **호텔**: 제주 신라호텔
- **주소**: 제주특별자치도 제주시 연동
- **체크인**: 15:00
- **체크아웃**: 11:00

## 방문 예정지
{places}

## 맛집 리스트
{restaurants}

## 준비물
{packing_list}

## 예산
- 항공료: 400,000원
- 숙박비: 600,000원
- 식비: 300,000원
- 관광비: 200,000원
- **총 예산**: 1,500,000원
""".format(
        places=UpNoteHelper.create_checklist([
            "성산일출봉 (일출 보기)",
            "한라산 국립공원 (등산)",
            "우도 (자전거 투어)",
            "천지연 폭포 (산책)",
            "협재해수욕장 (해변 휴식)",
            "제주 민속촌 (문화 체험)"
        ]),
        restaurants=UpNoteHelper.create_table(
            headers=["식당명", "음식", "위치", "예산"],
            rows=[
                ["흑돼지 맛집", "흑돼지 구이", "제주시", "50,000원"],
                ["해녀의 집", "전복죽", "성산", "30,000원"],
                ["올레국수", "고기국수", "서귀포", "15,000원"],
                ["카페 델문도", "커피", "애월", "20,000원"]
            ]
        ),
        packing_list=UpNoteHelper.create_checklist([
            "여권/신분증",
            "항공권 출력본",
            "카메라 및 충전기",
            "편한 신발 (등산화)",
            "선크림 및 모자",
            "우산 (날씨 대비)"
        ])
    )
    
    success = client.create_note(
        text=travel_content,
        title="✈️ 제주도 여행 계획",
        notebook="여행",
        tags=["여행", "제주도", "휴가", "계획"],
        color="green",
        location="제주특별자치도",
        due_date="2024-03-15",
        reminder="2024-03-10T10:00:00",
        attachments=["flight_ticket.pdf", "hotel_reservation.pdf"],
        template="travel"
    )
    print(f"여행 노트 생성: {'성공' if success else '실패'}")


def test_special_note_types():
    """특수 노트 타입들 테스트"""
    client = UpNoteClient()
    
    print("\n=== 특수 노트 타입 테스트 ===")
    
    # 1. 할 일 노트
    print("1. 할 일 노트 생성...")
    success = client.create_task_note(
        title="주간 업무 계획",
        tasks=[
            "프로젝트 제안서 작성",
            "클라이언트 미팅 준비",
            "코드 리뷰 완료",
            "문서 업데이트",
            "팀 회의 참석"
        ],
        notebook="업무",
        due_date="2024-01-26",
        priority="high",
        tags=["업무", "주간계획"],
        reminder="2024-01-22T09:00:00"
    )
    print(f"할 일 노트 생성: {'성공' if success else '실패'}")
    
    # 2. 회의록 노트
    print("\n2. 회의록 노트 생성...")
    success = client.create_meeting_note(
        title="Q1 전략 회의",
        date="2024년 1월 25일 (목) 14:00",
        attendees=["김대표", "박이사", "이부장", "최팀장"],
        agenda=[
            "Q4 실적 리뷰",
            "Q1 목표 설정",
            "신규 프로젝트 논의",
            "예산 계획 승인"
        ],
        notebook="회의록",
        location="본사 대회의실",
        tags=["전략회의", "Q1", "경영진"]
    )
    print(f"회의록 노트 생성: {'성공' if success else '실패'}")
    
    # 3. 프로젝트 노트
    print("\n3. 프로젝트 노트 생성...")
    success = client.create_project_note(
        project_name="모바일 앱 리뉴얼",
        description="기존 모바일 앱의 UI/UX를 개선하고 새로운 기능을 추가하는 프로젝트",
        milestones=[
            "사용자 리서치 완료",
            "와이어프레임 설계",
            "UI 디자인 완성",
            "프론트엔드 개발",
            "백엔드 API 연동",
            "테스트 및 QA",
            "앱스토어 배포"
        ],
        team_members=[
            "김기획 (기획자)",
            "박디자인 (UI/UX 디자이너)",
            "이개발 (프론트엔드 개발자)",
            "최서버 (백엔드 개발자)",
            "정테스트 (QA 엔지니어)"
        ],
        due_date="2024-06-30",
        notebook="프로젝트",
        priority="high"
    )
    print(f"프로젝트 노트 생성: {'성공' if success else '실패'}")
    
    # 4. 일일 노트
    print("\n4. 일일 노트 생성...")
    success = client.create_daily_note(
        mood="😊 좋음",
        weather="☀️ 맑음",
        goals=[
            "운동 30분 하기",
            "독서 1시간",
            "프로젝트 진행상황 정리",
            "가족과 저녁 식사"
        ],
        reflections="오늘은 새로운 기술을 배우는 재미있는 하루였다. 특히 UpNote API를 활용한 자동화가 매우 유용했다.",
        notebook="일기"
    )
    print(f"일일 노트 생성: {'성공' if success else '실패'}")


def test_url_debugging():
    """URL 생성 디버깅"""
    print("\n=== URL 디버깅 ===")
    client = UpNoteClient()
    
    # 복잡한 파라미터 조합 테스트
    complex_params = {
        "title": "복잡한 노트 테스트",
        "text": "# 제목\n\n**굵은 글씨**와 *기울임*\n\n- 목록 1\n- 목록 2",
        "notebook": "테스트 노트북",
        "tags": ["테스트", "복잡함", "디버깅"],
        "markdown": True,
        "pinned": True,
        "favorite": True,
        "color": "purple",
        "priority": "high",
        "reminder": "2024-01-25T15:30:00",
        "location": "서울특별시 강남구",
        "author": "테스터",
        "encrypted": False,
        "shared": True,
        "format": "markdown"
    }
    
    url = client.debug_url("note/new", complex_params)
    print(f"\n복잡한 파라미터 URL:")
    print(f"길이: {len(url)} 문자")
    print(f"URL: {url[:100]}..." if len(url) > 100 else f"URL: {url}")
    
    # 간단한 파라미터 테스트
    simple_params = {
        "title": "간단한 노트",
        "text": "간단한 내용",
        "markdown": True
    }
    
    simple_url = client.debug_url("note/new", simple_params)
    print(f"\n간단한 파라미터 URL:")
    print(f"URL: {simple_url}")


if __name__ == "__main__":
    test_extended_parameters()
    test_special_note_types()
    test_url_debugging()