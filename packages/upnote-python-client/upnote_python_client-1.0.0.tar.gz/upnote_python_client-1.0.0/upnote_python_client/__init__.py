"""
UpNote URL Scheme 클라이언트
UpNote의 x-callback-url을 사용하여 노트를 작성하고 관리할 수 있는 Python 클래스
"""

import subprocess
import urllib.parse
from typing import List, Optional, Dict, Any
from datetime import datetime
import platform


class UpNoteClient:
    """UpNote URL scheme을 사용하여 노트를 작성하고 관리하는 클래스"""
    
    def __init__(self):
        """
        UpNote 클라이언트 초기화
        """
        self.base_scheme = "upnote://x-callback-url"
        self.system = platform.system()
    
    def _open_url(self, url: str) -> bool:
        """
        시스템에 맞는 방법으로 URL 열기
        
        Args:
            url (str): 열 URL
            
        Returns:
            bool: 성공 여부
        """
        try:
            if self.system == "Darwin":  # macOS
                subprocess.run(["open", url], check=True)
            elif self.system == "Windows":
                subprocess.run(["start", url], shell=True, check=True)
            elif self.system == "Linux":
                subprocess.run(["xdg-open", url], check=True)
            else:
                raise Exception(f"지원하지 않는 운영체제: {self.system}")
            return True
        except subprocess.CalledProcessError as e:
            raise Exception(f"URL 열기 실패: {str(e)}")
    
    def _build_url(self, action: str, params: Dict[str, Any]) -> str:
        """
        UpNote URL scheme URL 생성
        
        Args:
            action (str): 액션 (예: note/new, note/open)
            params (Dict[str, Any]): URL 파라미터
            
        Returns:
            str: 완성된 URL
        """
        # None 값 제거 및 문자열 변환
        clean_params = {}
        for key, value in params.items():
            if value is not None:
                if isinstance(value, list):
                    clean_params[key] = ",".join(str(v) for v in value)
                elif isinstance(value, bool):
                    clean_params[key] = "true" if value else "false"
                else:
                    clean_params[key] = str(value)
        
        # URL 인코딩 (마크다운 문자들을 안전하게 처리)
        query_string = urllib.parse.urlencode(clean_params, safe='', quote_via=urllib.parse.quote)
        url = f"{self.base_scheme}/{action}"
        if query_string:
            url += f"?{query_string}"
        
        return url
    
    def debug_url(self, action: str, params: Dict[str, Any]) -> str:
        """
        디버깅용: 생성될 URL을 반환 (실제로 열지 않음)
        
        Args:
            action (str): 액션
            params (Dict[str, Any]): 파라미터
            
        Returns:
            str: 생성된 URL
        """
        return self._build_url(action, params)
    
    def create_note(
        self,
        text: Optional[str] = None,
        title: Optional[str] = None,
        notebook: Optional[str] = None,
        tags: Optional[List[str]] = None,
        markdown: Optional[bool] = True,
        pinned: Optional[bool] = None,
        favorite: Optional[bool] = None,
        starred: Optional[bool] = None,
        color: Optional[str] = None,
        reminder: Optional[str] = None,
        location: Optional[str] = None,
        attachment: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        template: Optional[str] = None,
        folder: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[str] = None,
        created_date: Optional[str] = None,
        modified_date: Optional[str] = None,
        author: Optional[str] = None,
        source: Optional[str] = None,
        url: Optional[str] = None,
        encrypted: Optional[bool] = None,
        password: Optional[str] = None,
        readonly: Optional[bool] = None,
        shared: Optional[bool] = None,
        public: Optional[bool] = None,
        format: Optional[str] = None,
        encoding: Optional[str] = None,
        x_success: Optional[str] = None,
        x_error: Optional[str] = None,
        x_cancel: Optional[str] = None
    ) -> bool:
        """
        새로운 노트 생성 (확장된 UpNote URL scheme 파라미터 지원)
        """
        params = {}
        
        # 기본 노트 정보
        if text:
            params["text"] = text
        if title:
            params["title"] = title
        if notebook:
            params["notebook"] = notebook
        if folder:
            params["folder"] = folder
        if tags:
            params["tags"] = tags
        if category:
            params["category"] = category
            
        # 노트 속성
        if markdown is not None:
            params["markdown"] = markdown
        if pinned is not None:
            params["pinned"] = pinned
        if favorite is not None:
            params["favorite"] = favorite
        if starred is not None:
            params["starred"] = starred
        if color:
            params["color"] = color
        if priority:
            params["priority"] = priority
            
        # 시간 관련
        if reminder:
            params["reminder"] = reminder
        if due_date:
            params["due_date"] = due_date
        if created_date:
            params["created_date"] = created_date
        if modified_date:
            params["modified_date"] = modified_date
            
        # 위치 및 첨부파일
        if location:
            params["location"] = location
        if attachment:
            params["attachment"] = attachment
        if attachments:
            params["attachments"] = attachments
            
        # 메타데이터
        if template:
            params["template"] = template
        if author:
            params["author"] = author
        if source:
            params["source"] = source
        if url:
            params["url"] = url
            
        # 보안 및 접근 제어
        if encrypted is not None:
            params["encrypted"] = encrypted
        if password:
            params["password"] = password
        if readonly is not None:
            params["readonly"] = readonly
        if shared is not None:
            params["shared"] = shared
        if public is not None:
            params["public"] = public
            
        # 형식 및 인코딩
        if format:
            params["format"] = format
        if encoding:
            params["encoding"] = encoding
            
        # 콜백 URL
        if x_success:
            params["x-success"] = x_success
        if x_error:
            params["x-error"] = x_error
        if x_cancel:
            params["x-cancel"] = x_cancel
        
        url = self._build_url("note/new", params)
        return self._open_url(url)
    
    def create_markdown_note(
        self,
        title: str,
        content: str,
        notebook: Optional[str] = None,
        tags: Optional[List[str]] = None,
        add_timestamp: bool = False,
        pinned: Optional[bool] = None,
        favorite: Optional[bool] = None,
        color: Optional[str] = None,
        reminder: Optional[str] = None
    ) -> bool:
        """
        마크다운 형식의 노트 생성 (특별히 마크다운 처리에 최적화)
        """
        # 마크다운 콘텐츠 포맷팅
        formatted_content = content
        
        if add_timestamp:
            formatted_content = UpNoteHelper.format_markdown_content(
                content, 
                add_timestamp=True
            )
        
        return self.create_note(
            text=formatted_content,
            title=title,
            notebook=notebook,
            tags=tags,
            markdown=True,
            pinned=pinned,
            favorite=favorite,
            color=color,
            reminder=reminder
        )
    
    def create_task_note(
        self,
        title: str,
        tasks: List[str],
        notebook: Optional[str] = None,
        due_date: Optional[str] = None,
        priority: str = "medium",
        tags: Optional[List[str]] = None,
        reminder: Optional[str] = None
    ) -> bool:
        """
        할 일 목록이 있는 노트 생성
        """
        task_content = "# " + title + "\n\n"
        task_content += UpNoteHelper.create_checklist(tasks)
        
        if due_date:
            task_content += f"\n\n**마감일**: {due_date}"
        
        return self.create_note(
            text=task_content,
            title=title,
            notebook=notebook,
            tags=tags or ["할일", "작업"],
            priority=priority,
            due_date=due_date,
            reminder=reminder,
            markdown=True
        )
    
    def create_meeting_note(
        self,
        title: str,
        date: str,
        attendees: List[str],
        agenda: List[str],
        notebook: Optional[str] = None,
        location: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        회의록 노트 생성
        """
        meeting_content = f"""# {title}

**일시**: {date}
**참석자**: {', '.join(attendees)}
{f"**장소**: {location}" if location else ""}

## 안건
{chr(10).join([f"{i+1}. {item}" for i, item in enumerate(agenda)])}

## 논의 내용
[논의 내용을 여기에 작성하세요]

## 결정 사항
- [결정 사항 1]
- [결정 사항 2]

## 액션 아이템
{UpNoteHelper.create_checklist([
    "[작업 내용] (담당자, 마감일)",
    "[작업 내용] (담당자, 마감일)"
])}

## 다음 회의
**일정**: [다음 회의 일정]
"""
        
        return self.create_note(
            text=meeting_content,
            title=title,
            notebook=notebook or "회의록",
            tags=tags or ["회의", "미팅"],
            location=location,
            markdown=True,
            template="meeting"
        )
    
    def create_project_note(
        self,
        project_name: str,
        description: str,
        milestones: List[str],
        team_members: List[str],
        due_date: Optional[str] = None,
        notebook: Optional[str] = None,
        priority: str = "medium"
    ) -> bool:
        """
        프로젝트 계획 노트 생성
        """
        project_content = f"""# 📋 {project_name}

## 프로젝트 개요
{description}

## 팀 구성
{chr(10).join([f"- {member}" for member in team_members])}

## 주요 마일스톤
{UpNoteHelper.create_checklist(milestones)}

## 진행 상황
- **시작일**: {datetime.now().strftime('%Y-%m-%d')}
{f"- **마감일**: {due_date}" if due_date else ""}
- **현재 상태**: 계획 단계

## 리소스
- 예산: [예산 정보]
- 도구: [사용할 도구들]
- 참고 자료: [관련 문서 링크]

## 위험 요소
- [위험 요소 1]
- [위험 요소 2]

## 다음 단계
{UpNoteHelper.create_checklist([
    "요구사항 분석",
    "기술 스택 결정",
    "개발 일정 수립"
])}
"""
        
        return self.create_note(
            text=project_content,
            title=f"📋 {project_name}",
            notebook=notebook or "프로젝트",
            tags=["프로젝트", "계획", priority],
            due_date=due_date,
            priority=priority,
            markdown=True,
            template="project"
        )
    
    def create_daily_note(
        self,
        date: Optional[str] = None,
        mood: Optional[str] = None,
        weather: Optional[str] = None,
        goals: Optional[List[str]] = None,
        reflections: Optional[str] = None,
        notebook: Optional[str] = None
    ) -> bool:
        """
        일일 노트 생성
        """
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        daily_content = f"""# 📅 {date}

## 오늘의 상태
{f"**기분**: {mood}" if mood else "**기분**: "}
{f"**날씨**: {weather}" if weather else "**날씨**: "}

## 오늘의 목표
{UpNoteHelper.create_checklist(goals) if goals else UpNoteHelper.create_checklist([
    "목표 1",
    "목표 2",
    "목표 3"
])}

## 중요한 일들
- [중요한 일 1]
- [중요한 일 2]

## 배운 것들
- [새로 배운 것 1]
- [새로 배운 것 2]

## 감사한 일들
- [감사한 일 1]
- [감사한 일 2]
- [감사한 일 3]

## 하루 돌아보기
{reflections if reflections else "[오늘 하루를 돌아보며 느낀 점을 적어보세요]"}

## 내일 계획
{UpNoteHelper.create_checklist([
    "내일 할 일 1",
    "내일 할 일 2"
])}
"""
        
        return self.create_note(
            text=daily_content,
            title=f"📅 {date}",
            notebook=notebook or "일기",
            tags=["일기", "데일리", date.replace('-', '')],
            created_date=date,
            markdown=True,
            template="daily"
        )
    
    def open_note(
        self,
        note_id: Optional[str] = None,
        title: Optional[str] = None,
        edit: Optional[bool] = None,
        x_success: Optional[str] = None,
        x_error: Optional[str] = None,
        x_cancel: Optional[str] = None
    ) -> bool:
        """
        기존 노트 열기
        """
        params = {}
        
        if note_id:
            params["id"] = note_id
        if title:
            params["title"] = title
        if edit is not None:
            params["edit"] = edit
        if x_success:
            params["x-success"] = x_success
        if x_error:
            params["x-error"] = x_error
        if x_cancel:
            params["x-cancel"] = x_cancel
        
        url = self._build_url("note/open", params)
        return self._open_url(url)
    
    def search_notes(
        self,
        query: str,
        notebook: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: Optional[int] = None,
        x_success: Optional[str] = None,
        x_error: Optional[str] = None,
        x_cancel: Optional[str] = None
    ) -> bool:
        """
        노트 검색
        """
        params = {"query": query}
        
        if notebook:
            params["notebook"] = notebook
        if tags:
            params["tags"] = tags
        if limit:
            params["limit"] = limit
        if x_success:
            params["x-success"] = x_success
        if x_error:
            params["x-error"] = x_error
        if x_cancel:
            params["x-cancel"] = x_cancel
        
        url = self._build_url("search", params)
        return self._open_url(url)
    
    def create_notebook(
        self,
        name: str,
        color: Optional[str] = None,
        parent: Optional[str] = None,
        x_success: Optional[str] = None,
        x_error: Optional[str] = None,
        x_cancel: Optional[str] = None
    ) -> bool:
        """
        새로운 노트북 생성
        """
        params = {"name": name}
        
        if color:
            params["color"] = color
        if parent:
            params["parent"] = parent
        if x_success:
            params["x-success"] = x_success
        if x_error:
            params["x-error"] = x_error
        if x_cancel:
            params["x-cancel"] = x_cancel
        
        url = self._build_url("notebook/new", params)
        return self._open_url(url)
    
    def open_notebook(
        self,
        name: Optional[str] = None,
        notebook_id: Optional[str] = None,
        x_success: Optional[str] = None,
        x_error: Optional[str] = None,
        x_cancel: Optional[str] = None
    ) -> bool:
        """
        노트북 열기
        """
        params = {}
        
        if name:
            params["name"] = name
        if notebook_id:
            params["id"] = notebook_id
        if x_success:
            params["x-success"] = x_success
        if x_error:
            params["x-error"] = x_error
        if x_cancel:
            params["x-cancel"] = x_cancel
        
        url = self._build_url("notebook/open", params)
        return self._open_url(url)
    
    def open_upnote(
        self,
        x_success: Optional[str] = None,
        x_error: Optional[str] = None
    ) -> bool:
        """
        UpNote 앱 열기
        """
        params = {}
        
        if x_success:
            params["x-success"] = x_success
        if x_error:
            params["x-error"] = x_error
        
        url = self._build_url("open", params)
        return self._open_url(url)
    
    def quick_note(
        self,
        text: str,
        append: Optional[bool] = None,
        prepend: Optional[bool] = None,
        x_success: Optional[str] = None,
        x_error: Optional[str] = None
    ) -> bool:
        """
        빠른 노트 추가 (기존 노트에 추가하거나 새 노트 생성)
        """
        params = {"text": text}
        
        if append is not None:
            params["append"] = append
        if prepend is not None:
            params["prepend"] = prepend
        if x_success:
            params["x-success"] = x_success
        if x_error:
            params["x-error"] = x_error
        
        url = self._build_url("quick", params)
        return self._open_url(url)
    
    def import_note(
        self,
        file_path: str,
        notebook: Optional[str] = None,
        format_type: Optional[str] = None,
        x_success: Optional[str] = None,
        x_error: Optional[str] = None,
        x_cancel: Optional[str] = None
    ) -> bool:
        """
        파일에서 노트 가져오기
        """
        params = {"file": file_path}
        
        if notebook:
            params["notebook"] = notebook
        if format_type:
            params["format"] = format_type
        if x_success:
            params["x-success"] = x_success
        if x_error:
            params["x-error"] = x_error
        if x_cancel:
            params["x-cancel"] = x_cancel
        
        url = self._build_url("import", params)
        return self._open_url(url)
    
    def export_note(
        self,
        note_id: Optional[str] = None,
        title: Optional[str] = None,
        format_type: str = "markdown",
        destination: Optional[str] = None,
        x_success: Optional[str] = None,
        x_error: Optional[str] = None,
        x_cancel: Optional[str] = None
    ) -> bool:
        """
        노트 내보내기
        """
        params = {"format": format_type}
        
        if note_id:
            params["id"] = note_id
        if title:
            params["title"] = title
        if destination:
            params["destination"] = destination
        if x_success:
            params["x-success"] = x_success
        if x_error:
            params["x-error"] = x_error
        if x_cancel:
            params["x-cancel"] = x_cancel
        
        url = self._build_url("export", params)
        return self._open_url(url)


class UpNoteHelper:
    """UpNote 작업을 위한 헬퍼 클래스"""
    
    @staticmethod
    def format_markdown_content(
        content: str,
        add_timestamp: bool = False,
        add_separator: bool = False
    ) -> str:
        """
        마크다운 콘텐츠 포맷팅
        """
        formatted_content = content
        
        if add_timestamp:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            formatted_content = f"*작성일: {timestamp}*\n\n{formatted_content}"
        
        if add_separator:
            formatted_content = f"{formatted_content}\n\n---\n"
        
        return formatted_content
    
    @staticmethod
    def create_checklist(items: List[str]) -> str:
        """
        체크리스트 생성
        """
        checklist = "\n".join([f"- [ ] {item}" for item in items])
        return checklist
    
    @staticmethod
    def create_table(headers: List[str], rows: List[List[str]]) -> str:
        """
        마크다운 테이블 생성
        """
        if not headers or not rows:
            return ""
        
        # 헤더 생성
        header_row = "| " + " | ".join(headers) + " |"
        separator_row = "| " + " | ".join(["---"] * len(headers)) + " |"
        
        # 데이터 행 생성
        data_rows = []
        for row in rows:
            if len(row) == len(headers):
                data_rows.append("| " + " | ".join(row) + " |")
        
        return "\n".join([header_row, separator_row] + data_rows)


# 패키지 정보
__version__ = "1.0.0"
__author__ = "UpNote Python Client Team"
__email__ = "upnote.python.client@gmail.com"
__description__ = "A Python client for UpNote using URL schemes"

# 메인 클래스들을 패키지 레벨에서 import 가능하게 함
__all__ = ["UpNoteClient", "UpNoteHelper"]