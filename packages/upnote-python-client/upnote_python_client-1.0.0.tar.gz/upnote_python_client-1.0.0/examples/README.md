# UpNote 클라이언트 예제

이 디렉토리에는 UpNote 클라이언트의 다양한 사용 예제가 포함되어 있습니다.

## 예제 파일들

### 📝 example_usage.py
기본적인 UpNote 클라이언트 사용법을 보여주는 예제입니다.

**포함된 기능:**
- 기본 노트 생성
- 마크다운 노트 생성
- 태그와 노트북 설정
- 체크리스트와 테이블 생성
- URL 생성 데모

**실행 방법:**
```bash
cd examples
python example_usage.py
```

### 🚀 advanced_example.py
고급 기능들을 활용한 예제입니다.

**포함된 기능:**
- 색상과 고정이 있는 중요한 노트
- 프로젝트 계획 노트
- 회의록 템플릿
- 노트북 생성 및 관리
- 고급 검색 기능
- 편집 모드로 노트 열기

**실행 방법:**
```bash
cd examples
python advanced_example.py
```

### 🌟 comprehensive_example.py
모든 확장된 파라미터를 사용하는 종합 예제입니다.

**포함된 기능:**
- 25개 이상의 파라미터를 사용한 복합 노트
- 암호화된 기밀 노트
- 위치 정보가 있는 여행 노트
- 특수 노트 타입들 (할일, 회의록, 프로젝트, 일기)
- URL 디버깅 기능

**실행 방법:**
```bash
cd examples
python comprehensive_example.py
```

## 사용 전 준비사항

1. **UpNote 앱 설치**: 실제 노트를 생성하려면 UpNote 앱이 설치되어 있어야 합니다.

2. **Python 환경**: Python 3.7 이상이 필요합니다.

3. **모듈 경로**: 예제를 실행하기 전에 상위 디렉토리의 `upnote_client.py`를 import할 수 있도록 경로를 설정해야 합니다.

## 주의사항

- 예제들은 실제로 UpNote 앱을 열고 노트를 생성합니다.
- 테스트 목적으로 많은 노트가 생성될 수 있으니 주의하세요.
- URL scheme 방식이므로 UpNote 앱이 설치되어 있어야 정상 동작합니다.

## 커스터마이징

각 예제 파일을 참고하여 자신만의 노트 생성 스크립트를 만들 수 있습니다. 
`upnote_client.py`의 모든 메서드와 파라미터를 활용해보세요!