"""
components/reference_view.py
MultiFactor 패키지 인터랙티브 함수 레퍼런스 (API Reference)
모든 클래스, 메서드 시그니처, 파라미터 규격, 반환값 명세
"""

import streamlit as st

def render_reference_view():
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); padding: 24px; border-radius: 12px; margin-bottom: 24px; border-left: 5px solid #10B981; color: white;">
        <h2 style="margin: 0; color: #FFFFFF; font-size: 24px;">📖 MultiFactor 공식 인터랙티브 API 레퍼런스</h2>
        <p style="margin: 8px 0 0 0; color: #94A3B8; font-size: 15px;">
            패키지에서 제공하는 모든 클래스와 메서드의 시그니처, 파라미터 타입, 반환 객체 구조 및 실무 코드 스니펫을 검색하고 탐색할 수 있습니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

    module_choice = st.radio(
        "탐색할 모듈을 선택하세요:",
        ["MultiFactorKR (국내 주식)", "MultiFactorUS (미국 주식)", "Visual (시각화 모듈)", "daum_consensus (컨센서스 API)"],
        horizontal=True
    )

    if module_choice == "MultiFactorKR (국내 주식)":
        st.subheader("class `MultiFactor.MultiFactorKR(N: int)`")
        st.markdown("**설명:** 국내 상장 주식(KOSPI, KOSDAQ)을 대상으로 시가총액 상위 N개 종목을 선별하여 멀티팩터 분석을 수행하는 메인 클래스입니다.")
        
        st.markdown("#### 🛠️ 생성자 파라미터")
        st.table([
            {"파라미터": "N", "타입": "int", "기본값": "필수값", "설명": "분석 대상 시가총액 상위 종목 수 (예: 50, 100, 200)"}
        ])

        with st.expander("📌 `get_stockinfo(dtype='dataframe') -> pd.DataFrame | dict`", expanded=True):
            st.markdown("""
            **기능:** 필터링(소형주, 저유동성, 동전주, 우선주, 스팩/리츠 배제)을 거친 시가총액 상위 $N$개 종목의 기초 정보를 반환합니다.
            - `dtype='dataframe'`: `['Code', 'Name', 'Marcap', 'Close', ...]` 컬럼의 DataFrame 반환
            - `dtype='dic'`: `{코드: 종목명}` 딕셔너리 반환
            """)
            st.code("""mf = MultiFactorKR(N=50)
stocks_df = mf.get_stockinfo() # DataFrame
stocks_dict = mf.get_stockinfo(dtype='dic') # Dict""", language="python")

        with st.expander("📌 `get_score() -> pd.DataFrame` (★ 핵심 메서드)", expanded=True):
            st.markdown("""
            **기능:** 종목 선별 $\\rightarrow$ 모멘텀 지표 $\\rightarrow$ 밸류 지표 $\\rightarrow$ 퀄리티 지표를 순차적으로 자동 계산하여 8대 팩터 백분위 점수 및 종합순위가 포함된 마스터 데이터프레임을 반환합니다.
            
            **반환 컬럼:**
            - `scode`, `sname`: 종목코드 및 종목명
            - `mom_price`, `mom_vol`: 주가 수익률 및 거래량 회전율
            - `PER`, `PBR`: 주가수익비율 및 주가순자산비율
            - `revenue_rate`, `oper_income_rate`, `net_income_rate`, `ROE`: 성장률 및 자기자본이익률
            - `모멘텀_주가`, `모멘텀_거래량`, `밸류_PER`, `밸류_PBR`, `퀄리티_ROE`, `퀄리티_매출증가`, `퀄리티_영업이익증가`, `퀄리티_순이익증가`: 8대 백분위 점수
            - `종합점수`: 8개 지표의 산술 평균 (낮을수록 우수)
            - `종합순위`: 종합점수 오름차순 순위 (1등이 최고 유망 종목)
            """)
            st.code("""mf = MultiFactorKR(N=100)
scores = mf.get_score()
print(scores.head(10))""", language="python")

        with st.expander("📌 `get_score_adj_weight(data_mast, weight='균등') -> pd.DataFrame`", expanded=True):
            st.markdown("""
            **기능:** 기 계산된 멀티팩터 마스터 데이터에 투자 스타일별 가중치를 부여하여 종합점수와 종합순위를 재산출합니다.
            - `weight='균등'`: 8개 팩터 각각 동일 가중치 (1/8)
            - `weight='가치성장'`: 밸류(2/8) + 퀄리티(6/8), 모멘텀 0
            - `weight='추세성장'`: 모멘텀(2/8) + 퀄리티(6/8), 밸류 0
            - `weight='역발상'`: 모멘텀(4/8) + 밸류(4/8), 퀄리티 0
            """)
            st.code("""df_adj = mf.get_score_adj_weight(scores, weight='추세성장')""", language="python")

        with st.expander("📌 `get_Ngroup(data_mast, Ngroup=10)`", expanded=True):
            st.markdown("""
            **기능:** 종합순위 순으로 정렬된 데이터를 `Ngroup`개로 균등 분할하고 각 그룹에 속한 종목명을 콘솔에 출력합니다.
            """)
            st.code("""mf.get_Ngroup(scores, Ngroup=5) # 5개 그룹으로 분류""", language="python")

        with st.expander("📌 `merge_krx_sectors(df, code_col='scode') -> pd.DataFrame` (업종 조인 헬퍼)", expanded=True):
            st.markdown("""
            **기능:** `MultiFactorKR`의 `get_score()` 결과 DataFrame의 `scode`에 `fdr.StockListing('KRX-DESC')`의 표준 업종(Industry/Sector) 컬럼을 안전하게 매핑(Merge)하여 `sector` 컬럼을 생성합니다.
            """)
            st.code("""from harness import merge_krx_sectors

scores = mf_kr.get_score()
# KRX-DESC 표준 업종 컬럼 조인
scores_with_sector = merge_krx_sectors(scores)
print(scores_with_sector[['scode', 'sname', 'sector', '종합순위']].head(5))""", language="python")

        with st.expander("📌 단일 종목 및 세부 팩터 메서드"):
            st.markdown("""
            - `get_momentum(stock_list)`: 종목 리스트의 모멘텀 지표 산출
            - `get_momentum_one(scode)`: 단일 종목의 모멘텀 지표 산출
            - `get_value(stock_list)`: 종목 리스트의 PER/PBR 산출
            - `get_value_one(scode)`: 단일 종목의 PER/PBR 산출
            - `get_quality(stock_list)`: 종목 리스트의 실적 증가율 및 ROE 산출
            - `get_quality_one(scode)`: 단일 종목의 실적 증가율 및 ROE 산출
            - `get_score_by_data(data_mom, data_val, data_fin)`: 이미 수집된 3대 팩터 데이터프레임을 직접 결합
            """)

    elif module_choice == "MultiFactorUS (미국 주식)":
        st.subheader("class `MultiFactor.MultiFactorUS(N: int = 500)`")
        st.markdown("**설명:** 미국 S&P 500 및 나스닥/NYSE 주요 상장 종목을 대상으로 글로벌 퀀트 분석을 수행하는 클래스입니다.")
        
        st.table([
            {"파라미터": "N", "타입": "int", "기본값": "500", "설명": "분석 대상 시가총액 상위 티커 수 (기본값: S&P 500 전종목)"}
        ])

        with st.expander("📌 주요 메서드 목록", expanded=True):
            st.markdown("""
            - `get_stockinfo(dtype='dataframe')`: S&P 500 최신 티커 및 시가총액 정보 수집
            - `get_momentum(stock_list)`: `yfinance` 기반 미국 종목의 주가 및 거래량 모멘텀 산출
            - `get_value(stock_list)`: 미국 종목의 PER, PBR 밸류에이션 지표 수집
            - `get_quality(stock_list)`: 미국 기업의 분기 재무제표 기준 성장률 및 ROE 산출
            - `get_score()`: 미국 주식 8대 팩터 종합점수 및 순위 계산
            - `get_score_adj_weight(data_mast, weight='추세성장')`: 미국 시장 맞춤형 스타일 가중치 적용
            - `get_Ngroup(data_mast, Ngroup=10)`: 미국 포트폴리오 N분위 그룹 분할
            """)
            st.code("""from MultiFactor import MultiFactorUS

mf_us = MultiFactorUS(N=100)
us_scores = mf_us.get_score()
us_trend = mf_us.get_score_adj_weight(us_scores, weight='추세성장')
mf_us.get_Ngroup(us_trend, Ngroup=5)""", language="python")

    elif module_choice == "Visual (시각화 모듈)":
        st.subheader("class `MultiFactor.Visual()`")
        st.markdown("**설명:** 주식 시장 분석, 팩터 분포, 블룸버그 스타일 히트맵 및 트리맵을 시각화하는 고성능 시각화 모듈입니다.")
        
        methods = [
            ("multi_kr()", "국내 주식 기간별 복합 등락률 및 모멘텀 시각화"),
            ("multi_us()", "미국 주요 종목 기간별 성과 비교 차트"),
            ("multi_idx()", "국내외 주요 지수(KOSPI, KOSDAQ, S&P500, NASDAQ) 다중 비교"),
            ("heatmap_kr()", "국내 종목별 블룸버그 스타일 연간/월간 수익률 히트맵"),
            ("heatmap_us()", "미국 종목별 블룸버그 스타일 성과 히트맵"),
            ("treemap_us()", "미국 시장 섹터 및 시가총액 비중 트리맵 시각화"),
            ("targetprice_us()", "미국 애널리스트 목표주가 컨센서스 및 상승여력 차트"),
            ("compare_idx()", "지수 간 벤치마크 상관관계 분석"),
            ("ret_kr() / ret_us()", "개별 종목 일별/주별 누적 수익률 곡선"),
            ("finance_kr()", "국내 기업 주요 재무지표 추이 시각화")
        ]

        st.table([{"메서드명": m[0], "기능 설명": m[1]} for m in methods])

        st.code("""from MultiFactor import Visual

v = Visual()
# 블룸버그 스타일 국내 주식 성과 히트맵 출력
v.heatmap_kr()

# 미국 S&P 500 시장 트리맵 출력
v.treemap_us()""", language="python")

    elif module_choice == "daum_consensus (컨센서스 API)":
        st.subheader("module `MultiFactor.daum_consensus`")
        st.markdown("**설명:** 다음증권 금융 컨센서스 데이터를 파싱하여 연간 및 분기별 실적 추정치와 밸류에이션 지표를 추출하는 유틸리티입니다.")

        with st.expander("📌 `get_daum_consensus(stock_code, timeout=15)`", expanded=True):
            st.markdown("""
            **기능:** 특정 종목코드(예: `'A005930'`)의 연간 컨센서스와 분기 컨센서스를 `(df_annual, df_quarter)` 튜플 형태로 수집합니다.
            """)
            st.code("""from MultiFactor.daum_consensus import get_daum_consensus

df_annual, df_quarter = get_daum_consensus('A005930')
print("연간 추정 실적:")
print(df_annual[['매출액', '영업이익', 'PER(배)', 'ROE(%)']])""", language="python")
