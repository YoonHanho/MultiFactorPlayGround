"""
run_harness.py
MultiFactor 테스트 하네스 러너 (CLI Verification Runner)
"""

import sys
import time
from harness.test_suite import run_all_harness_tests

def main():
    print("=" * 60)
    print("🚀 [MultiFactor] 하네스 기법 기반 자동화 정합성 검증 시작")
    print("=" * 60)
    start_time = time.time()
    
    result = run_all_harness_tests()
    elapsed = round(time.time() - start_time, 4)
    
    print("\n" + "=" * 60)
    print(f"📊 검증 결과 요약 (소요시간: {elapsed}초)")
    print(f" - 총 테스트 케이스: {result['total']}")
    print(f" - 성공(Passed):    {result['passed']}")
    print(f" - 실패(Failures):  {result['failures']}")
    print(f" - 에러(Errors):    {result['errors']}")
    print("=" * 60)

    if result['was_successful']:
        print("✅ 하네스 검증 통과! 모든 팩터 수식 및 패키지 인터페이스가 완벽하게 정합합니다.\n")
        return 0
    else:
        print("❌ 하네스 검증 실패! 오류 세부사항을 확인하세요.\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
