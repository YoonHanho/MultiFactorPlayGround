"""
components/charts.py
Plotly 기반 인터랙티브 퀀트 시각화 모듈 (레이더 차트, 산점도, 히트맵, N그룹 성과 비교)
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import List, Dict, Any

from harness.engine import FACTOR_COLS

def render_radar_chart(df: pd.DataFrame, selected_stocks: List[str]) -> go.Figure:
    """
    선택된 종목(최대 3개)의 8대 팩터 상대 강도(100 - 백분위 점수: 높을수록 우수) 레이더 차트
    """
    categories = [
        '주가 모멘텀', '거래량 모멘텀', 
        '저PER(가치)', '저PBR(가치)', 
        '고ROE(수익성)', '매출액 성장', 
        '영업이익 성장', '순이익 성장'
    ]

    fig = go.Figure()
    colors = ['#2563EB', '#10B981', '#F59E0B', '#8B5CF6']

    for i, sname in enumerate(selected_stocks):
        row = df[df['sname'] == sname]
        if row.empty:
            continue
        row = row.iloc[0]
        # MultiFactor에서는 백분위 순위(1.0이 최상위 1등, 100.0이 꼴등)이므로
        # 직관적인 레이더 차트 표시를 위해 (100 - 점수)를 '팩터 강도'로 환산
        values = [
            max(0, 100 - row['모멘텀_주가']),
            max(0, 100 - row['모멘텀_거래량']),
            max(0, 100 - row['밸류_PER']),
            max(0, 100 - row['밸류_PBR']),
            max(0, 100 - row['퀄리티_ROE']),
            max(0, 100 - row['퀄리티_매출증가']),
            max(0, 100 - row['퀄리티_영업이익증가']),
            max(0, 100 - row['퀄리티_순이익증가']),
        ]
        values.append(values[0]) # 다각형 닫기

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            fill='toself',
            name=f"{sname} (종합 {int(row['종합순위'])}위)",
            line=dict(color=colors[i % len(colors)], width=2.5),
            fillcolor=colors[i % len(colors)].replace('rgb', 'rgba').replace(')', ', 0.15)') if 'rgb' in colors[i % len(colors)] else None
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10, color='#64748B'),
                gridcolor='#E2E8F0',
            ),
            angularaxis=dict(
                tickfont=dict(size=12, family="sans-serif", weight='bold'),
                gridcolor='#E2E8F0',
            )
        ),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        margin=dict(l=40, r=40, t=30, b=40),
        height=450,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def render_factor_scatter(df: pd.DataFrame, x_metric: str, y_metric: str) -> go.Figure:
    """
    모멘텀 vs 밸류 vs 퀄리티 팩터 산점도 (종합순위에 따른 색상 매핑)
    """
    metric_labels = {
        'mom_price': '주가 모멘텀(%)',
        'mom_vol': '거래량 모멘텀(%)',
        'PER': 'PER (주가수익비율, 배)',
        'PBR': 'PBR (주가순자산비율, 배)',
        'ROE': 'ROE (자기자본이익률, %)',
        'revenue_rate': '매출액 증가율(%)',
        'oper_income_rate': '영업이익 증가율(%)',
        'net_income_rate': '당기순이익 증가율(%)',
        '종합점수': '멀티팩터 종합점수 (낮을수록 우수)',
        '종합순위': '최종 종합순위 (1등이 최고)'
    }

    x_title = metric_labels.get(x_metric, x_metric)
    y_title = metric_labels.get(y_metric, y_metric)

    hover_data = {
        'scode': True,
        'sname': True,
        'sector': True if 'sector' in df.columns else False,
        '종합순위': True,
        '종합점수': ':.1f',
        x_metric: ':.1f',
        y_metric: ':.1f',
    }

    fig = px.scatter(
        df,
        x=x_metric,
        y=y_metric,
        color='종합순위',
        color_continuous_scale='Viridis_r', # 상위 순위(1위)가 밝은 색상
        hover_name='sname',
        hover_data=hover_data,
        text='sname',
        labels={'종합순위': '종합순위'},
        title=f"<b>{x_title} vs {y_title}</b>"
    )

    fig.update_traces(
        textposition='top center',
        textfont=dict(size=10),
        marker=dict(size=12, opacity=0.85, line=dict(width=1, color='white'))
    )

    fig.update_layout(
        xaxis=dict(title=x_title, gridcolor='#F1F5F9', zerolinecolor='#CBD5E1'),
        yaxis=dict(title=y_title, gridcolor='#F1F5F9', zerolinecolor='#CBD5E1'),
        height=480,
        margin=dict(l=40, r=40, t=50, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def render_correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    """8대 팩터 간 상관관계 매트릭스 히트맵"""
    cols = FACTOR_COLS
    corr = df[cols].corr().round(2)

    short_labels = [
        '주가모멘텀', '거래량모멘텀', 
        'PER(밸류)', 'PBR(밸류)', 
        'ROE(퀄리티)', '매출증가', 
        '영업익증가', '순익증가'
    ]

    fig = px.imshow(
        corr,
        x=short_labels,
        y=short_labels,
        color_continuous_scale='RdBu_r',
        zmin=-1,
        zmax=1,
        text_auto=True,
        title="<b>8대 팩터 지표 간 상관계수(Correlation) 히트맵</b>"
    )

    fig.update_layout(
        height=420,
        margin=dict(l=40, r=40, t=50, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def render_ngroups_bar(groups: List[Dict[str, Any]]) -> go.Figure:
    """N-그룹별 핵심 지표(ROE, PER, 모멘텀) 평균 비교 막대차트"""
    labels = [g['label'] for g in groups]
    avg_scores = [g['avg_score'] for g in groups]
    avg_roes = [g['avg_roe'] for g in groups]
    avg_pers = [g['avg_per'] for g in groups]
    avg_moms = [g['avg_mom_price'] for g in groups]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=labels,
        y=avg_roes,
        name='평균 ROE (%)',
        marker_color='#10B981',
        text=[f"{v:.1f}%" for v in avg_roes],
        textposition='outside'
    ))

    fig.add_trace(go.Bar(
        x=labels,
        y=avg_moms,
        name='평균 주가상승률 (%)',
        marker_color='#2563EB',
        text=[f"{v:.1f}%" for v in avg_moms],
        textposition='outside'
    ))

    fig.add_trace(go.Bar(
        x=labels,
        y=avg_pers,
        name='평균 PER (배)',
        marker_color='#F59E0B',
        text=[f"{v:.1f}x" for v in avg_pers],
        textposition='outside'
    ))

    fig.update_layout(
        barmode='group',
        title="<b>N-그룹별 핵심 팩터 프로파일 비교 (최상위 1그룹 vs 하위 그룹)</b>",
        xaxis=dict(title="분할 그룹", gridcolor='#F1F5F9'),
        yaxis=dict(title="지표 수치", gridcolor='#F1F5F9'),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        height=450,
        margin=dict(l=40, r=40, t=50, b=50),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def render_rank_change_waterfall(df: pd.DataFrame) -> go.Figure:
    """가중치 변경으로 순위가 가장 크게 상승/하락한 상위 10개 종목"""
    if '순위변동' not in df.columns:
        return go.Figure()

    top_movers = df.sort_values(by='순위변동', ascending=False)
    winners = top_movers.head(5)
    losers = top_movers.tail(5)
    movers = pd.concat([winners, losers]).drop_duplicates(subset=['scode'])

    colors = ['#10B981' if v > 0 else ('#EF4444' if v < 0 else '#94A3B8') for v in movers['순위변동']]

    fig = go.Figure(go.Bar(
        x=movers['sname'],
        y=movers['순위변동'],
        marker_color=colors,
        text=[f"{'+' if v>0 else ''}{v}위" for v in movers['순위변동']],
        textposition='outside'
    ))

    fig.update_layout(
        title="<b>가중치 조정에 따른 순위 변동폭 (순위 상승 ⬆ / 하락 ⬇)</b>",
        xaxis=dict(title="종목명"),
        yaxis=dict(title="순위 변동 (등수)"),
        height=380,
        margin=dict(l=40, r=40, t=50, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig
