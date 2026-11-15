"""
components/docs_view.py
MultiFactor 인터랙티브 도서 및 패키지 문서 뷰
출판 도서 《데이터와 AI로 앞서가는 주식 투자》 2장 & 3장 완벽 연계
"""

import streamlit as st

def render_docs_view():
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); padding: 24px; border-radius: 12px; margin-bottom: 24px; border-left: 5px solid #3B82F6; color: white;">
        <h2 style="margin: 0; color: #FFFFFF; font-size: 24px;">📚 MultiFactor 공식 인터랙티브 도서 & 패키지 가이드</h2>
        <p style="margin: 8px 0 0 0; color: #94A3B8; font-size: 15px;">
            출판 도서 <b>《데이터와 AI로 앞서가는 주식 투자》</b>(길벗, 2026)의 핵심 퀀트 프레임워크와 오픈소스 패키지 <code>MultiFactor</code>의 사용법 및 실전 투자 전략을 총정리한 인터랙티브 가이드입니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "🌟 패키지 개요 및 설치",
        "🇰🇷 CHAPTER 02. 국내 주식 분석",
        "🇺🇸 CHAPTER 03. 미국 주식 멀티팩터",
        "💡 퀀트 실전 운용 조언"
    ])

    with tab1:
        st.subheader("1. MultiFactor 패키지란?")
        st.markdown("""
        **MultiFactor**는 나익희/일등박사가 제작하여 PyPI에 공식 배포한 파이썬 오픈소스 퀀트 패키지입니다.
        
        복잡하고 시간이 오래 걸리는 재무 데이터 수집 및 전처리, 팩터 산출, 종합 스코어링 과정을 몇 줄의 파이썬 코드로 자동화하여, 
        초보 투자자부터 전문 퀀트 분석가까지 객관적인 데이터 기반 투자를 실행할 수 있도록 지원합니다.

        #### 🧩 핵심 3대 팩터 모델
        1. **모멘텀 (Momentum)**: 주가 상승률과 거래량 회전율을 결합하여 시장의 강력한 추세를 추종합니다.
        2. **밸류 (Value)**: PER(주가수익비율)과 PBR(주가순자산비율)을 결합하여 기업 내재가치 대비 저평가된 우량주를 발굴합니다.
        3. **퀄리티 (Quality)**: ROE(자기자본이익률)와 매출액·영업이익·당기순이익 성장률을 결합하여 이익 체력과 펀더멘털을 검증합니다.
        """)

        st.markdown("---")
        st.subheader("2. 설치 및 필수 요구사항")
        col_inst1, col_inst2 = st.columns([3, 2])
        with col_inst1:
            st.code("""# 터미널 또는 주피터 노트북에서 설치
pip install MultiFactor

# 최신 버전으로 업데이트
pip install --upgrade MultiFactor
            """, language="bash")
        with col_inst2:
            st.info("""
            **주요 의존 패키지:**
            - `finance-datareader` (국내외 시세 및 재무제표)
            - `yfinance` (미국 시세 및 해외 금융)
            - `pandas`, `numpy`, `plotly`, `seaborn`
            """)

        st.markdown("---")
        st.subheader("3. 30초 퀵스타트 예제")
        st.code("""from MultiFactor import MultiFactorKR, MultiFactorUS, Visual

# 1. 국내 주식 시가총액 상위 50개 종목 멀티팩터 종합점수 산출
mf_kr = MultiFactorKR(N=50)
df_score = mf_kr.get_score()

# 상위 10개 유망 종목 확인
print(df_score[['scode', 'sname', '종합점수', '종합순위']].head(10))

# 2. 투자 스타일에 맞춘 가중치 조정 ('추세성장', '가치성장', '역발상', '균등')
df_adj = mf_kr.get_score_adj_weight(df_score, weight='추세성장')

# 3. 5개 그룹으로 분류하여 포트폴리오 유니버스 추출
mf_kr.get_Ngroup(df_adj, Ngroup=5)
        """, language="python")

    with tab2:
        st.subheader("🇰🇷 CHAPTER 02. 국내 주식 분석하기 (도서 연계)")
        st.markdown("""
        > *"결정을 내릴 때는 스스로에게 물어보라. 내 판단을 뒷받침하는 명확한 사실을 제시할 수 있는가? 그렇지 않다면, 당신의 판단은 단지 감정에 불과하다."*
        
        출판 도서 2장에서는 국내 상장사(KOSPI, KOSDAQ)를 대상으로 데이터 정제부터 최종 멀티팩터 포트폴리오를 구성하는 5단계 프로세스를 다룹니다.
        """)

        st.markdown("#### 🔍 1단계: 유니버스 선별 및 필터링 규칙")
        st.markdown("""
        멀티팩터 분석의 신뢰성을 높이고 왜곡을 방지하기 위해 `MultiFactor`는 엄격한 필터링 기준을 적용합니다:
        - **소형주 제외**: 시가총액 1,000억 원 미만 종목 배제 (유동성 리스크 차단)
        - **저유동성 제외**: 일일 거래량 2,000주 미만 종목 배제
        - **동전주 제외**: 주가 1,000원 미만 종목 배제 (높은 이상 변동성 회피)
        - **우선주 제외**: 본주와의 주가 괴리율 한계로 종목코드 끝자리가 `5`, `7`, `9`, `K`인 종목 필터링
        - **특수 목적 법인 제외**: 스팩(SPAC), 리츠(REITs), 인프라, 유전, 벤처투자 등 재무 데이터 왜곡 유발 기업 제외
        """)

        st.markdown("#### 📐 2단계: 8대 세부 팩터 계산 수식")
        st.markdown(r"""
        * **모멘텀 (클수록 우수 $\rightarrow$ 내림차순 순위화)**
          $$\text{모멘텀\_주가} = \frac{\text{Rank}(\text{mom\_price}, \text{desc})}{N} \times 100$$
          $$\text{모멘텀\_거래량} = \frac{\text{Rank}(\text{mom\_vol}, \text{desc})}{N} \times 100$$
        * **밸류 (작을수록 저평가 $\rightarrow$ 오름차순 순위화)**
          $$\text{밸류\_PER} = \frac{\text{Rank}(\text{PER}, \text{asc})}{N} \times 100, \quad \text{밸류\_PBR} = \frac{\text{Rank}(\text{PBR}, \text{asc})}{N} \times 100$$
        * **퀄리티 (클수록 우수 $\rightarrow$ 내림차순 순위화)**
          $$\text{퀄리티\_ROE} = \frac{\text{Rank}(\text{ROE}, \text{desc})}{N} \times 100$$
          $$\text{매출/영업익/순익 증가율} = \frac{\text{Rank}(\text{성장률}, \text{desc})}{N} \times 100$$
        * **종합점수 (8개 백분위 순위의 산술 평균 $\rightarrow$ 낮을수록 최상위 1등)**
          $$\text{종합점수} = \frac{1}{8} \sum_{i=1}^{8} \text{Factor}_i$$
        """)

        st.markdown("#### 💻 2장 실습 예제 코드")
        st.code("""from MultiFactor import MultiFactorKR

# 시가총액 상위 200개 종목 대상 분석
mf = MultiFactorKR(N=200)

# (1) 종목 리스트 확인
stock_info = mf.get_stockinfo()

# (2) 멀티팩터 마스터 자동 계산
score_df = mf.get_score()

# (3) 최상위 1그룹(상위 20%) 종목군 추출
mf.get_Ngroup(score_df, Ngroup=5)
        """, language="python")

    with tab3:
        st.subheader("🇺🇸 CHAPTER 03. 미국 주식 멀티팩터 실전 투자 전략 (도서 연계)")
        st.markdown("""
        > *"미국에 반대하는 베팅은 하지 마라 (Never bet against America)."* — 워런 버핏
        
        출판 도서 3장에서는 S&P 500 및 나스닥 주요 대형주를 대상으로 글로벌 기축 통화 시장에서 승리하는 멀티팩터 전략을 전개합니다.
        """)

        st.markdown("#### 🌐 1. 미국 주식 심볼 클리닝 (`clean_us_symbol`)")
        st.markdown("""
        미국 주식은 브로커와 데이터 제공자마다 클래스 주식(Class A, Class B) 표기가 다릅니다 (`BRK.B`, `BRK/B`, `BRKB`). 
        `MultiFactorUS`는 이를 `BRK-B`, `BF-B`와 같이 `yfinance` 표준 규격으로 자동 표준화하여 결측치 발생을 방지합니다.
        """)

        st.markdown("#### 🎯 2. 투자 스타일별 가중치 최적화 포트폴리오")
        st.markdown(r"""
        | 투자 전략 | 핵심 가중 지표 조합 | 목표 및 투자 스타일 |
        | :--- | :--- | :--- |
        | **⚖️ 균등 전략** | 8대 팩터 각 $1/8$ 동일 배분 | 시장 전반의 균형 잡힌 팩터 분산 |
        | **💎 가치 성장** | 밸류(PER, PBR) + 퀄리티(ROE, 성장률) | 튼튼한 실적을 내면서도 주가가 싼 우량 가치주 |
        | **🚀 추세 성장** | 모멘텀(주가, 거래량) + 퀄리티(ROE, 성장률) | 엔비디아(NVDA)처럼 강력한 상승 추세의 실적 주도주 |
        | **🔄 역발상 전략** | 밸류(PER, PBR) + 모멘텀(주가, 거래량) | 소외되었다가 바닥을 다지고 반등하는 턴어라운드 종목 |
        """)

        st.code("""from MultiFactor import MultiFactorUS

mf_us = MultiFactorUS(N=500)
us_scores = mf_us.get_score()

# 추세성장 전략 적용: 모멘텀과 실적 성장이 겸비된 글로벌 테크 주도주 선별
growth_picks = mf_us.get_score_adj_weight(us_scores, weight='추세성장')
print(growth_picks[['scode', 'sname', '종합점수', '종합순위']].head(10))
        """, language="python")

    with tab4:
        st.subheader("💡 저자가 전하는 실전 퀀트 투자 3대 핵심 조언")
        st.markdown("""
        1. **흔들리지 않는 고정 리밸런싱 주기를 준수하세요**
           - 매일 시세를 보며 일희일비할 필요가 없습니다. 
           - 1개월(월간), 3개월(분기별 실적 발표 직후) 리밸런싱이 거래 비용과 세금을 절감하면서도 팩터 프리미엄을 온전히 누리는 가장 검증된 주기입니다.
        
        2. **적정 분산(10~25종목)을 유지하세요**
           - 1~2개 종목에 몰빵하는 것은 퀀트 투자가 아닌 도박입니다.
           - `get_Ngroup(Ngroup=10)`으로 상위 1그룹(Decile 1)에서 15~20개 종목을 동일 가중(Equal Weight)으로 편입하는 것이 비체계적 리스크를 제거하는 최선의 방법입니다.
        
        3. **시장 국면에 따라 스타일 가중치를 탄력적으로 운용하세요**
           - **유동성 확장기/강세장**: `추세성장`(모멘텀 + 퀄리티) 전략으로 시장 주도주 비중을 극대화합니다.
           - **고금리/침체기/조정장**: `가치성장`(밸류 + 퀄리티) 전략으로 하방 경직성과 안전마진을 확보합니다.
        """)
