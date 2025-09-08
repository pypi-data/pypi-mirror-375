"""
최종 테스트 요약 및 검증
모든 예제 파일들이 정상 동작하는지 확인
"""

import subprocess
import sys
from pathlib import Path


def run_test_file(filename: str) -> tuple[bool, str]:
    """테스트 파일 실행"""
    try:
        result = subprocess.run(
            [sys.executable, filename],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "테스트 시간 초과"
    except Exception as e:
        return False, f"실행 오류: {str(e)}"


def main():
    """모든 테스트 파일 실행"""
    print("🔍 UpNote 클라이언트 최종 검증 시작\n")
    
    test_files = [
        ("종합 기능 테스트", "tests/test_all_features.py"),
        ("기본 사용 예제", "examples/example_usage.py"),
        ("마크다운 테스트", "tests/test_markdown.py"),
        ("고급 기능 예제", "examples/advanced_example.py"),
        ("종합 기능 예제", "examples/comprehensive_example.py")
    ]
    
    results = []
    
    for test_name, filename in test_files:
        if not Path(filename).exists():
            print(f"❌ {test_name}: 파일 없음 ({filename})")
            results.append(False)
            continue
            
        print(f"🧪 {test_name} 실행 중...")
        success, output = run_test_file(filename)
        
        if success:
            print(f"✅ {test_name}: 성공")
            results.append(True)
        else:
            print(f"❌ {test_name}: 실패")
            print(f"   오류 내용: {output[:200]}...")
            results.append(False)
    
    # 결과 요약
    passed = sum(results)
    total = len(results)
    success_rate = (passed / total) * 100
    
    print(f"\n📊 최종 검증 결과:")
    print(f"✅ 성공: {passed}/{total}")
    print(f"❌ 실패: {total - passed}/{total}")
    print(f"📈 성공률: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("\n🎉 모든 예제가 완벽하게 동작합니다!")
        print("\n📋 제공되는 기능:")
        print("   • 기본 노트 생성 (25+ 파라미터 지원)")
        print("   • 마크다운 최적화 노트")
        print("   • 특수 노트 타입 (할일, 회의록, 프로젝트, 일기)")
        print("   • 고급 검색 및 필터링")
        print("   • 노트북 관리")
        print("   • 파일 가져오기/내보내기")
        print("   • 헬퍼 함수 (체크리스트, 테이블, 포맷팅)")
        print("   • 크로스 플랫폼 지원 (macOS, Windows, Linux)")
        print("   • 완전한 URL 인코딩 및 에러 처리")
        
        print("\n🚀 사용 준비 완료!")
        return True
    else:
        print(f"\n⚠️ {total - passed}개의 예제에서 문제가 발견되었습니다.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)