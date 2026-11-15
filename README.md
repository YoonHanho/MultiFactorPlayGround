# 📈 MultiFactor 인터랙티브 웹 문서 및 퀀트 플레이그라운드

> **오픈소스 퀀트 패키지 `MultiFactor`와 도서 《데이터와 AI로 앞서가는 주식 투자》(길벗, 2026)를 위한 통합 인터랙티브 플랫폼**  
> **소프트웨어 공학의 하네스(Harness) 기법**을 적용하여 수식의 엄격한 수학적 정합성과 고속 시뮬레이션을 구현했습니다.

---

## 🌟 프로젝트 개요

본 프로젝트는 파이썬 오픈소스 퀀트 분석 라이브러리 **`MultiFactor`**(개발자: 나익희, 일등박사)의 사용법, 8대 팩터 스코어링 수식, 함수 레퍼런스, 도서 예제 코드를 한눈에 모아보고, 웹 화면에서 직접 파라미터와 가중치를 조절하며 퀀트 랭킹을 시뮬레이션할 수 있는 **Streamlit 기반 인터랙티브 웹 문서 및 플레이그라운드**입니다.

### 🔗 공식 참조 리소스
1. **PyPI MultiFactor:** https://pypi.org/project/MultiFactor/
2. **GitHub 저장소:** https://github.com/YoonHanho/MultiFactor
3. **출판 도서:** 《데이터와 AI로 앞서가는 주식 투자》(길벗, 2026) https://www.yes24.com/product/goods/197279828
4. **도서 예제 깃헙:** https://github.com/DrFirstLee/python_investments_notebooks/blob/main/2%EC%9E%A5.ipynb

---

## 🛡️ 하네스(Harness) 기법 적용 내용

본 프로젝트에는 신뢰성 높은 퀀트 엔진과 즉각적인 사용자 반응성을 위해 **하네스 아키텍처(Harness Architecture)**가 전면 적용되었습니다.

1. **표준 픽스처(Fixtures) 기반 고속 시뮬레이션 (`harness/fixtures.py`)**:
   - 대규모 웹 크롤링 및 외부 API 지연 없이 0.05초 만에 팩터 계산과 랭킹 변동을 테스트할 수 있도록 국내(KOSPI/KOSDAQ) 및 미국(S&P 500) 표준 데이터셋 구축.
2. **이중 모드 실행 엔진 (`harness/engine.py`)**:
   - 고속 픽스처 하네스 모드와 실제 `MultiFactor` 패키지 라이브 연동 모드를 통합.
   - 원본 패키지 알고리즘(`score.py`, `score_adj_weight.py`)과 100% 동일한 수식으로 연산.
3. **자동화 검증 스위트 (`harness/test_suite.py`, `run_harness.py`)**:
   - `test_01_factor_ranking_directions`: 모멘텀/ROE(내림차순) 및 PER/PBR(오름차순) 방향성 검증
   - `test_02_style_weight_presets`: 균등, 가치성장, 추세성장, 역발상 4대 전략 정합성 검증
   - `test_03_custom_weights_rescaling`: 슬라이더 가중치 자동 정규화(합 100%) 검증
   - `test_04_missing_and_infinite_value_handling`: NaN 및 Inf 중앙값(Median) 대체 견고성 검증
   - `test_05_ngroup_partitioning`: N-그룹 포트폴리오 분위 분할 및 상/하위 그룹 변별력 검증
   - `test_06_package_import_parity`: 실제 설치된 패키지 API 시그니처 호환성 검증
   - `test_07_krx_desc_sector_merge`: MultiFactor 결과의 scode에 fdr.StockListing('KRX-DESC') 표준 업종 컬럼 병합 검증

---

## 🚀 빠른 시작 (Quick Start)

### 1. 가상환경 활성화 및 패키지 설치
```bash
# 가상환경 활성화 (Windows PowerShell 기준)
.venv\Scripts\Activate.ps1

# 의존 패키지 설치
pip install -r requirements.txt
```

### 2. 하네스 자동화 검증 실행
```bash
python run_harness.py
```

### 3. 인터랙티브 웹 애플리케이션 실행
```bash
streamlit run app.py
```
브라우저에서 `http://localhost:8501`로 접속하여 플레이그라운드를 이용할 수 있습니다.

---

## 📱 웹 애플리케이션 주요 화면 구성

### 1. 🧪 인터랙티브 미니 플레이그라운드
- **시장 유니버스 선택**: 🇰🇷 국내 주식(코스피/코스닥) vs 🇺🇸 미국 주식(S&P 500)
- **전략 프리셋**: 균등 가중치, 가치성장(밸류+퀄리티), 추세성장(모멘텀+퀄리티), 역발상(밸류+모멘텀)
- **커스텀 가중치 슬라이더**: 8대 팩터의 가중치를 0.0~5.0 범위로 조작 시 실시간 순위 재계산
- **인터랙티브 시각화**:
  - 🏆 **종합 순위 리더보드**: 상위 3위 메달 카드, 순위 변동($\Delta$) 워터폴
  - 🕸️ **종목 팩터 레이더 비교**: 2~3개 종목의 8대 팩터 강도 비교
  - 🔍 **팩터 산점도 탐색**: X/Y축을 자유롭게 지정하여 팩터 간 관계 및 이상치 분석
  - 📊 **$N$-그룹 포트폴리오**: 1그룹(상위 주도주) vs 하위 그룹 성과 비교
  - 🌡️ **팩터 상관관계 매트릭스**: 8개 팩터 간 상관계수 히트맵
  - 💻 **실시간 파이썬 재현 코드**: 슬라이더 조작 상태를 그대로 재현하는 복사 가능한 파이썬 스크립트 실시간 생성
  - 📥 **CSV 다운로드**: 계산된 스코어링 데이터 내보내기

### 2. 📚 도서 가이드 & 개요
- 개발자 나익희, 일등박사의 퀀트 투자 철학 및 패키지 아키텍처
- 출판 도서 **《데이터와 AI로 앞서가는 주식 투자》** 2장(국내) 및 3장(미국) 핵심 내용 수록
- 필터링 기준(동전주, 우선주, 스팩/리츠 제외) 및 실전 퀀트 조언

### 3. 📖 인터랙티브 API 레퍼런스
- `MultiFactorKR`, `MultiFactorUS`, `Visual`, `daum_consensus`의 모든 함수 시그니처와 예제 제공

### 4. 🛡️ 하네스 검증 센터
- 웹 UI 상에서 버튼 클릭 한 번으로 6개 핵심 단위 테스트를 즉시 수행하고 검증 리포트 확인

---

## 📂 디렉터리 구조

```
멀티팩터_플레이그라운드/
├── app.py                     # Streamlit 메인 진입점
├── run_harness.py             # CLI 하네스 테스트 러너
├── requirements.txt           # 패키지 의존성 명세
├── README.md                  # 프로젝트 설명서
├── components/                # UI 뷰 및 시각화 컴포넌트
│   ├── charts.py              # Plotly 레이더, 산점도, 히트맵, 막대차트
│   ├── docs_view.py           # 도서 가이드 & 패키지 소개 뷰
│   ├── reference_view.py      # 인터랙티브 API 레퍼런스 뷰
│   └── playground_view.py     # 인터랙티브 미니 플레이그라운드 뷰
├── harness/                   # 하네스 기법 아키텍처
│   ├── engine.py              # 팩터 계산, 가중치 정규화, N-그룹 분할 엔진
│   ├── fixtures.py            # KR/US 표준 데이터셋 픽스처
│   └── test_suite.py          # 자동화 검증 스위트 (unittest)
└── data/                      # 캐시된 픽스처 데이터
    ├── kr_stocks_sample.csv
    └── us_stocks_sample.csv
```
