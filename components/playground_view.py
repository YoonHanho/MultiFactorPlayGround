"""
components/playground_view.py
MultiFactor 인터랙티브 미니 플레이그라운드
사용자가 파라미터를 실시간으로 조작하며 팩터 스코어링 및 포트폴리오 분할을 테스트하는 인터랙티브 환경
"""

import streamlit as st
import pandas as pd
import numpy as np

from harness.engine import MultiFactorHarnessEngine, FACTOR_COLS, STYLE_WEIGHT_PRESETS
from .charts import (
    render_radar_chart, 
    render_factor_scatter, 
    render_correlation_heatmap, 
    render_ngroups_bar, 
    render_rank_change_waterfall
)

def render_playground_view():
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); padding: 22px; border-radius: 12px; margin-bottom: 20px; border-left: 5px solid #F59E0B; color: white;">
        <h2 style="margin: 0; color: #FFFFFF; font-size: 24px;">🧪 MultiFactor 인터랙티브 미니 플레이그라운드</h2>
        <p style="margin: 8px 0 0 0; color: #94A3B8; font-size: 15px;">
            시장 유니버스, 투자 스타일, 8대 팩터 세부 가중치 및 $N$-그룹 분할 파라미터를 직접 변경하면서 실시간으로 산출되는 퀀트 랭킹과 포트폴리오 프로파일을 탐색하세요.
        </p>
    </div>
    """, unsafe_allow_html=True)

    engine = MultiFactorHarnessEngine()

    # 상단 컨트롤 패널
    st.markdown("### 🎛️ 1. 데이터 소스 및 분석 전략 설정")
    
    col_mode, col1, col2, col3 = st.columns([1.3, 1.1, 1.1, 1.5])

    with col_mode:
        data_mode = st.radio(
            "데이터 소스 모드",
            ["⚡ 고속 하네스 모드 (스냅샷)", "🌐 MultiFactor 실시간 라이브"],
            index=0,
            help="⚡ 고속 하네스 모드는 0.05초 만에 실시간 슬라이더 반응을 제공합니다. 🌐 실시간 라이브는 MultiFactor 패키지가 직접 네이버/다음/KRX에서 실시간 데이터를 수집합니다."
        )
        use_live_flag = ("실시간" in data_mode)
        force_refresh_clicked = False
        if use_live_flag:
            force_refresh_clicked = st.button("🔄 실시간 데이터 다시 수집", help="이미 수집된 데이터를 비우고 거래소/네이버/다음의 최신 시세를 처음부터 다시 크롤링합니다.")

    with col1:
        market = st.selectbox(
            "시장 선택",
            ["🇰🇷 국내 주식 (KRX)", "🇺🇸 미국 주식 (S&P 500)"],
            index=0
        )
        market_code = "KR" if "국내" in market else "US"

    with col2:
        if use_live_flag:
            n_stocks = st.slider(
                "유니버스 크기 (N)",
                min_value=5,
                max_value=30,
                value=15,
                step=5,
                help="실시간 라이브 모드는 웹 크롤링 딜레이(종목당 1초 time.sleep)로 인해 5~30개 범위로 안전 제한됩니다."
            )
        else:
            n_stocks = st.slider(
                "유니버스 크기 (N)",
                min_value=10,
                max_value=200,
                value=100,
                step=10,
                help="⚡ 고속 하네스 모드에서는 200개 전 종목을 0.02초 만에 초고속으로 실시간 분석 및 랭킹 산출합니다."
            )

    with col3:
        strategy_preset = st.selectbox(
            "투자 스타일 프리셋",
            ["⚖️ 균등 가중치 (기본)", "💎 가치성장 전략", "🚀 추세성장 전략", "🔄 역발상 전략", "🎛️ 직접 커스텀 가중치 설정"],
            index=0
        )

    # 커스텀 가중치 슬라이더 (직접 설정 선택 시)
    custom_weights_dict = None
    if strategy_preset == "🎛️ 직접 커스텀 가중치 설정":
        st.markdown("#### ⚖️ 8대 팩터 세부 가중치 슬라이더 (0.0 ~ 5.0)")
        c1, c2, c3, c4 = st.columns(4)
        c5, c6, c7, c8 = st.columns(4)

        with c1:
            w_mom_p = st.slider("주가 모멘텀", 0.0, 5.0, 1.0, 0.5)
        with c2:
            w_mom_v = st.slider("거래량 모멘텀", 0.0, 5.0, 1.0, 0.5)
        with c3:
            w_val_per = st.slider("저PER (가치)", 0.0, 5.0, 1.0, 0.5)
        with c4:
            w_val_pbr = st.slider("저PBR (가치)", 0.0, 5.0, 1.0, 0.5)
        with c5:
            w_qual_roe = st.slider("고ROE (수익성)", 0.0, 5.0, 1.0, 0.5)
        with c6:
            w_qual_rev = st.slider("매출액 성장", 0.0, 5.0, 1.0, 0.5)
        with c7:
            w_qual_oper = st.slider("영업이익 성장", 0.0, 5.0, 1.0, 0.5)
        with c8:
            w_qual_net = st.slider("순이익 성장", 0.0, 5.0, 1.0, 0.5)

        custom_weights_dict = {
            '모멘텀_주가': w_mom_p,
            '모멘텀_거래량': w_mom_v,
            '밸류_PER': w_val_per,
            '밸류_PBR': w_val_pbr,
            '퀄리티_ROE': w_qual_roe,
            '퀄리티_매출증가': w_qual_rev,
            '퀄리티_영업이익증가': w_qual_oper,
            '퀄리티_순이익증가': w_qual_net,
        }
        total_w = sum(custom_weights_dict.values())
        if total_w > 0:
            st.caption(f"가중치 정규화 합계: 100% (원래 합: {total_w:.1f})")
    else:
        style_key = "균등"
        if "가치성장" in strategy_preset:
            style_key = "가치성장"
        elif "추세성장" in strategy_preset:
            style_key = "추세성장"
        elif "역발상" in strategy_preset:
            style_key = "역발상"

    # 1. 기초 데이터(base_df) 캐싱 및 수집 (세션 상태 활용)
    base_cache_key = f"base_data_{market_code}_{n_stocks}_{use_live_flag}"
    needs_fetch = False

    if force_refresh_clicked or base_cache_key not in st.session_state:
        needs_fetch = True

    if needs_fetch:
        if use_live_flag:
            spinner_msg = f"🌐 MultiFactor 패키지({market_code})를 실행하여 실시간 증권 데이터를 수집 중입니다 (상위 {n_stocks}개, 최초 1회만 수집)..."
            with st.spinner(spinner_msg):
                df_base, meta_base = engine.get_base_dataframe(
                    market=market_code,
                    n_stocks=n_stocks,
                    use_live=True,
                    force_refresh=True
                )
        else:
            df_base, meta_base = engine.get_base_dataframe(
                market=market_code,
                n_stocks=n_stocks,
                use_live=False,
                force_refresh=False
            )
        st.session_state[base_cache_key] = (df_base, meta_base)
    else:
        df_base, meta_base = st.session_state[base_cache_key]

    # 2. 투자 스타일 및 가중치 적용 (기존 수집 데이터를 재사용하여 0.001초 만에 즉시 계산)
    scored_df, meta = engine.run_scoring(
        market=market_code,
        n_stocks=n_stocks,
        style=style_key if not custom_weights_dict else "균등",
        custom_weights=custom_weights_dict,
        base_df=df_base
    )
    meta["mode"] = meta_base.get("mode")
    meta["fetch_elapsed_sec"] = meta_base.get("elapsed_sec")
    meta["is_cached"] = not needs_fetch

    # 데이터 소스 상태 안내 배너
    if meta.get("mode") == "live_package":
        if meta.get("is_cached"):
            st.success(f"⚡ **기존 수집 데이터 유지 (초고속 가중치 재적용)**: {meta['market']} {meta['total_stocks']}개 종목의 기 수집 데이터를 유지한 채 변경된 스타일 가중치만 0.001초 만에 재적용했습니다. (새로고침을 원하시면 상단의 '🔄 실시간 데이터 다시 수집' 버튼을 누르세요)")
        else:
            st.success(f"✅ **MultiFactor 라이브 패키지 최초 수집 완료**: {meta['market']} {meta['total_stocks']}개 종목의 실시간 데이터를 패키지에서 직접 추출했습니다 (소요시간: {meta.get('fetch_elapsed_sec', 0)}초). 이제 프리셋을 자유롭게 변경하셔도 재수집 없이 즉시 계산됩니다.")
    elif "fallback" in meta.get("mode", ""):
        st.warning(f"⚠️ **외부 서버/네트워크 연결 제한으로 하네스 픽스처 데이터로 자동 전환되었습니다**: {meta.get('mode')}")
    else:
        st.info(f"⚡ **고속 하네스 모드(검증 스냅샷)**: 실제 퀀트 지표 기반의 표준 픽스처 데이터셋을 사용하여 0.02초 만에 실시간 슬라이더 반응성을 제공합니다. (상단 라디오 버튼에서 'MultiFactor 실시간 라이브'로 전환 가능)")

    # 섹터 필터 및 검색
    all_sectors = sorted(list(scored_df['sector'].unique())) if 'sector' in scored_df.columns else []
    f_col1, f_col2 = st.columns([2, 1])
    with f_col1:
        sel_sectors = st.multiselect("섹터 필터링 (선택 시 해당 섹터만 표시)", all_sectors, default=all_sectors)
    with f_col2:
        search_kw = st.text_input("종목명/티커 검색", placeholder="예: 삼성전자, NVDA")

    filtered_df = scored_df.copy()
    if sel_sectors and 'sector' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['sector'].isin(sel_sectors)]
    if search_kw:
        filtered_df = filtered_df[
            filtered_df['sname'].str.contains(search_kw, case=False, na=False) |
            filtered_df['scode'].str.contains(search_kw, case=False, na=False)
        ]

    st.markdown("---")

    # 상위 3위 카드 (메달)
    top_3 = scored_df.head(3).to_dict(orient='records')
    medals = ["🥇 1위 (최우수)", "🥈 2위", "🥉 3위"]
    card_cols = st.columns(3)
    for idx, (col_item, card_stock) in enumerate(zip(card_cols, top_3)):
        with col_item:
            st.markdown(f"""
            <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 16px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <div style="font-size: 16px; font-weight: bold; color: #1E293B;">{medals[idx]}</div>
                <div style="font-size: 20px; font-weight: 800; color: #2563EB; margin: 4px 0;">{card_stock['sname']} <span style="font-size: 12px; color: #64748B;">({card_stock['scode']})</span></div>
                <div style="font-size: 13px; color: #475569;">섹터: <b>{card_stock.get('sector', 'N/A')}</b></div>
                <div style="margin-top: 8px; font-size: 14px; font-weight: 600; color: #0F172A;">종합점수: <span style="color: #059669;">{card_stock['종합점수']:.1f}점</span></div>
                <div style="font-size: 11px; color: #64748B;">PER: {card_stock.get('PER', 0):.1f}x | ROE: {card_stock.get('ROE', 0):.1f}% | 모멘텀: {card_stock.get('mom_price', 0):+.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 플레이그라운드 탭 구성
    tab_rank, tab_radar, tab_scatter, tab_group, tab_corr, tab_code, tab_raw = st.tabs([
        "🏆 종합 순위 리더보드",
        "🕸️ 종목 팩터 레이더 비교",
        "🔍 팩터 산점도 탐색",
        "📊 N-그룹 포트폴리오",
        "🌡️ 팩터 상관관계 매트릭스",
        "💻 실시간 파이썬 재현 코드",
        "📥 원본 데이터 & CSV 다운로드"
    ])

    with tab_rank:
        st.subheader("🏆 멀티팩터 최종 종합 순위")
        st.caption("※ 종합점수는 8대 지표 백분위 순위(1.0~100.0)의 가중 평균으로, **낮을수록 최상위 우수 기업**입니다.")

        # 테이블 뷰 포맷팅
        display_cols = [
            '종합순위', '순위변동', 'scode', 'sname', 'sector', '종합점수', 
            'mom_price', 'PER', 'PBR', 'ROE'
        ]
        display_df = filtered_df[[c for c in display_cols if c in filtered_df.columns]].copy()
        display_df.rename(columns={
            '종합순위': '순위',
            '순위변동': '변동',
            'scode': '종목코드',
            'sname': '종목명',
            'sector': '섹터',
            '종합점수': '종합점수',
            'mom_price': '주가상승률(%)',
            'PER': 'PER(배)',
            'PBR': 'PBR(배)',
            'ROE': 'ROE(%)'
        }, inplace=True)

        st.dataframe(
            display_df.style.format({
                '종합점수': '{:.1f}',
                '주가상승률(%)': '{:+.1f}%',
                'PER(배)': '{:.1f}x',
                'PBR(배)': '{:.2f}x',
                'ROE(%)': '{:.1f}%'
            }),
            use_container_width=True,
            height=420
        )

        if '순위변동' in filtered_df.columns and filtered_df['순위변동'].abs().sum() > 0:
            st.markdown("#### 🚀 가중치 조정으로 인한 순위 변동 효과")
            st.plotly_chart(render_rank_change_waterfall(filtered_df), use_container_width=True)

    with tab_radar:
        st.subheader("🕸️ 종목별 8대 팩터 레이더 프로파일 비교")
        st.caption("비교하고 싶은 2~3개 종목을 선택하여 팩터 강도(0~100, 바깥쪽일수록 우수)를 직관적으로 비교하세요.")
        
        available_stocks = filtered_df['sname'].tolist()
        default_picks = available_stocks[:2] if len(available_stocks) >= 2 else available_stocks
        selected_stocks = st.multiselect("비교 종목 선택 (최대 3개)", available_stocks, default=default_picks, max_selections=3)

        if selected_stocks:
            radar_fig = render_radar_chart(scored_df, selected_stocks)
            st.plotly_chart(radar_fig, use_container_width=True)
        else:
            st.info("비교할 종목을 위 목록에서 선택하세요.")

    with tab_scatter:
        st.subheader("🔍 팩터 간 관계 및 이상치 분석 산점도")
        s_col1, s_col2 = st.columns(2)
        with s_col1:
            x_ax = st.selectbox("X축 팩터", ['PER', 'PBR', 'mom_price', 'mom_vol', 'ROE', 'revenue_rate'], index=0)
        with s_col2:
            y_ax = st.selectbox("Y축 팩터", ['ROE', 'mom_price', 'PER', 'PBR', 'oper_income_rate', '종합점수'], index=0)

        scatter_fig = render_factor_scatter(filtered_df, x_ax, y_ax)
        st.plotly_chart(scatter_fig, use_container_width=True)

    with tab_group:
        st.subheader("📊 N-그룹 포트폴리오 (도서 get_Ngroup 연계)")
        st.caption("선택한 유니버스를 $N$개 분위 그룹으로 나누어 1그룹(상위 주도주)과 하위 그룹의 펀더멘털 차이를 확인합니다.")

        n_group_input = st.slider("분할 그룹 수 (Ngroup)", 2, 10, 5, 1)
        target_df = filtered_df if len(filtered_df) >= n_group_input else scored_df
        groups = engine.get_ngroups(target_df, n_groups=n_group_input)

        group_bar_fig = render_ngroups_bar(groups)
        st.plotly_chart(group_bar_fig, use_container_width=True)

        st.markdown("#### 📋 각 그룹별 상세 종목 구성")
        for g in groups:
            with st.expander(f"{g['label']} — {g['count']}개 종목 (평균점수: {g['avg_score']}점, ROE: {g['avg_roe']}%, PER: {g['avg_per']}x)", expanded=(g['group_number']==1)):
                st.write("**포함 종목:** " + ", ".join(g['stocks']))

    with tab_corr:
        st.subheader("🌡️ 8대 팩터 간 상관관계 매트릭스")
        st.caption("팩터 간의 양/음의 상관성을 파악하여 분산 투자 효과를 극대화할 수 있습니다.")
        corr_fig = render_correlation_heatmap(scored_df)
        st.plotly_chart(corr_fig, use_container_width=True)

    with tab_code:
        st.subheader("💻 화면 설정 그대로 재현하는 파이썬 코드")
        st.caption("플레이그라운드에서 선택한 파라미터와 가중치를 그대로 패키지 코드로 생성합니다. 복사하여 로컬 파이썬에서 즉시 실행할 수 있습니다.")

        if custom_weights_dict:
            weights_repr = [custom_weights_dict[col] for col in FACTOR_COLS]
            weight_script = f"""# 커스텀 가중치 벡터 설정
custom_weights = {weights_repr}
# MultiFactor의 score_adj_weight 로직으로 재계산
import numpy as np
cols = ['모멘텀_주가', '모멘텀_거래량', '밸류_PER', '밸류_PBR', '퀄리티_ROE', '퀄리티_매출증가', '퀄리티_영업이익증가', '퀄리티_순이익증가']
scores['종합점수'] = np.average(scores[cols], axis=1, weights=custom_weights)
scores['종합순위'] = scores['종합점수'].rank(ascending=True)
scores.sort_values(by='종합순위', inplace=True)"""
        else:
            weight_script = f"""# 스타일 가중치 적용 ({strategy_preset})
scores_adj = mf.get_score_adj_weight(scores, weight='{style_key}')"""

        python_code = f"""# ============================================================
# MultiFactor 플레이그라운드 자동 생성 코드
# 시장: {market} | 종목수: {n_stocks}개
# ============================================================
from MultiFactor import {'MultiFactorKR' if market_code=='KR' else 'MultiFactorUS'}

# 1. 멀티팩터 객체 초기화 및 기초 데이터 수집
mf = {'MultiFactorKR' if market_code=='KR' else 'MultiFactorUS'}(N={n_stocks})

# 2. 8대 세부 팩터 및 마스터 종합점수 산출
scores = mf.get_score()

# 3. 투자 스타일에 따른 점수 재계산
{weight_script}

# 4. N-그룹 분할 포트폴리오 추출
mf.get_Ngroup({'scores' if custom_weights_dict else 'scores_adj'}, Ngroup=5)
"""
        st.code(python_code, language="python")

    with tab_raw:
        st.subheader("📥 원본 퀀트 데이터셋 확인 및 다운로드")
        st.dataframe(filtered_df, use_container_width=True)
        csv_data = filtered_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="💾 현재 팩터 스코어링 데이터 CSV 다운로드",
            data=csv_data,
            file_name=f"multifactor_scores_{market_code.lower()}_{n_stocks}.csv",
            mime="text/csv"
        )
