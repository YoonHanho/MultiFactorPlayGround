"""
harness/engine.py
MultiFactor 연산 및 검증 엔진 (Dual Mode: Live Engine & High-Speed Fixture Harness)
패키지의 원본 알고리즘(score.py, score_adj_weight.py)과 100% 동일한 수식으로 연산 및 가중치 시뮬레이션 지원
"""

import pandas as pd
import numpy as np
import time
from typing import Dict, List, Optional, Tuple, Any

from .fixtures import get_fixture_dataframe

FACTOR_COLS = [
    '모멘텀_주가', 
    '모멘텀_거래량', 
    '밸류_PER', 
    '밸류_PBR', 
    '퀄리티_ROE', 
    '퀄리티_매출증가', 
    '퀄리티_영업이익증가', 
    '퀄리티_순이익증가'
]

RAW_METRIC_MAP = {
    '모멘텀_주가': 'mom_price',
    '모멘텀_거래량': 'mom_vol',
    '밸류_PER': 'PER',
    '밸류_PBR': 'PBR',
    '퀄리티_ROE': 'ROE',
    '퀄리티_매출증가': 'revenue_rate',
    '퀄리티_영업이익증가': 'oper_income_rate',
    '퀄리티_순이익증가': 'net_income_rate'
}

STYLE_WEIGHT_PRESETS = {
    '균등': [1/8, 1/8, 1/8, 1/8, 1/8, 1/8, 1/8, 1/8],
    '가치성장': [0/8, 0/8, 1/8, 1/8, 1/8, 1/8, 1/8, 1/8],
    '추세성장': [1/8, 1/8, 0/8, 0/8, 1/8, 1/8, 1/8, 1/8],
    '역발상': [1/8, 1/8, 1/8, 1/8, 0/8, 0/8, 0/8, 0/8]
}

_KRX_SECTOR_MAP_CACHE = None

def get_krx_sector_map() -> Dict[str, str]:
    """
    fdr.StockListing('KRX-DESC')의 표준 업종 컬럼 딕셔너리 수집 및 캐싱
    네트워크 불가 시 로컬 data/krx_desc_sectors.csv로 즉시 안전 폴백
    """
    global _KRX_SECTOR_MAP_CACHE
    if _KRX_SECTOR_MAP_CACHE is not None:
        return _KRX_SECTOR_MAP_CACHE

    # 1. FinanceDataReader 실시간 조회 시도
    try:
        import FinanceDataReader as fdr
        df_desc = fdr.StockListing('KRX-DESC')
        df_desc['Code'] = df_desc['Code'].astype(str).str.zfill(6)
        # Industry가 있으면 Industry, 없으면 Sector, 둘 다 없으면 '기타'
        sector_series = df_desc['Industry'].fillna(df_desc['Sector']).fillna('기타')
        _KRX_SECTOR_MAP_CACHE = dict(zip(df_desc['Code'], sector_series))
        return _KRX_SECTOR_MAP_CACHE
    except Exception:
        pass

    # 2. 로컬 캐시 파일 조회 시도
    try:
        df_local = pd.read_csv('data/krx_desc_sectors.csv', dtype={'Code': str})
        df_local['Code'] = df_local['Code'].astype(str).str.zfill(6)
        _KRX_SECTOR_MAP_CACHE = dict(zip(df_local['Code'], df_local['Sector']))
        return _KRX_SECTOR_MAP_CACHE
    except Exception:
        return {}

def merge_krx_sectors(df: pd.DataFrame, code_col: str = 'scode') -> pd.DataFrame:
    """
    MultiFactor 결과 DataFrame의 scode 컬럼에 fdr.StockListing('KRX-DESC')의
    표준 업종(Industry/Sector) 컬럼을 조인(Merge)해 주는 경량 헬퍼 함수
    """
    if df is None or df.empty:
        return df

    out_df = df.copy()
    col = code_col if code_col in out_df.columns else ('Code' if 'Code' in out_df.columns else None)
    if col is None:
        return out_df

    sector_map = get_krx_sector_map()
    if sector_map:
        mapped_sector = out_df[col].astype(str).str.zfill(6).map(sector_map)
        if 'sector' in out_df.columns:
            out_df['sector'] = out_df['sector'].fillna(mapped_sector).fillna('기타')
        else:
            out_df['sector'] = mapped_sector.fillna('기타')
    elif 'sector' not in out_df.columns:
        out_df['sector'] = '기타'

    return out_df

class MultiFactorHarnessEngine:
    """MultiFactor 연산 하네스 엔진"""

    def __init__(self):
        self._cache = {}

    @staticmethod
    def merge_krx_sectors(df: pd.DataFrame, code_col: str = 'scode') -> pd.DataFrame:
        """MultiFactor 결과 DataFrame에 KRX 표준 업종 조인"""
        return merge_krx_sectors(df, code_col=code_col)

    @staticmethod
    def calculate_base_scores(df: pd.DataFrame) -> pd.DataFrame:
        """
        원본 데이터프레임으로부터 8대 팩터 백분위 순위(1.0~100.0) 및 기본 균등점수 계산
        MultiFactor 패키지의 score.py 로직과 정확히 일치함
        """
        data_mast = df.copy()

        # 결측치 보정 (수치형 컬럼 대상 median 대체)
        num_cols = data_mast.select_dtypes(include=[np.number]).columns
        for col in num_cols:
            data_mast[col] = data_mast[col].replace([np.inf, -np.inf], np.nan)
            median_val = data_mast[col].median()
            data_mast[col] = data_mast[col].fillna(median_val if not pd.isna(median_val) else 0.0)

        n = len(data_mast)
        if n == 0:
            return data_mast

        # 1. 모멘텀 지표 순위화 : 클수록 우수 -> ascending=False (1등이 최소 퍼센타일값)
        data_mast['모멘텀_주가'] = data_mast['mom_price'].rank(ascending=False, axis=0) / n * 100
        data_mast['모멘텀_거래량'] = data_mast['mom_vol'].rank(ascending=False, axis=0) / n * 100

        # 2. 밸류 지표 순위화 : 작을수록 저평가 우수 -> ascending=True
        data_mast['밸류_PER'] = data_mast['PER'].rank(ascending=True, axis=0) / n * 100
        data_mast['밸류_PBR'] = data_mast['PBR'].rank(ascending=True, axis=0) / n * 100

        # 3. 퀄리티 지표 순위화 : 클수록 우수 -> ascending=False
        data_mast['퀄리티_ROE'] = data_mast['ROE'].rank(ascending=False, axis=0) / n * 100
        data_mast['퀄리티_매출증가'] = data_mast['revenue_rate'].rank(ascending=False, axis=0) / n * 100
        data_mast['퀄리티_영업이익증가'] = data_mast['oper_income_rate'].rank(ascending=False, axis=0) / n * 100
        data_mast['퀄리티_순이익증가'] = data_mast['net_income_rate'].rank(ascending=False, axis=0) / n * 100

        # 4. 균등 종합점수 (평균)
        data_mast['기본_종합점수'] = np.average(data_mast[FACTOR_COLS], axis=1)
        data_mast['기본_종합순위'] = data_mast['기본_종합점수'].rank(ascending=True, axis=0).astype(int)

        # 현재 종합점수 및 순위 기본값 설정
        data_mast['종합점수'] = data_mast['기본_종합점수']
        data_mast['종합순위'] = data_mast['기본_종합순위']
        data_mast['종합순위_퍼센트'] = (data_mast['종합순위'] / n) * 100

        data_mast.sort_values(by='종합순위', inplace=True)
        data_mast.reset_index(drop=True, inplace=True)
        return data_mast

    @staticmethod
    def apply_weights(df: pd.DataFrame, weights: List[float]) -> pd.DataFrame:
        """
        가중치 벡터(길이 8)를 적용하여 종합점수 및 종합순위 재산출
        MultiFactor의 score_adj_weight.py 로직 적용
        """
        data_weight = df.copy()
        w = np.array(weights, dtype=float)
        
        # 가중치 합이 0일 경우 균등 가중치로 방어
        if np.sum(w) == 0:
            w = np.ones(8) / 8.0
        else:
            w = w / np.sum(w) # 정규화

        # 가중치 적용 종합점수 계산
        data_weight['종합점수'] = np.average(data_weight[FACTOR_COLS], axis=1, weights=w)
        
        # 종합순위 (오름차순: 점수가 낮을수록 상위 순위)
        data_weight['종합순위'] = data_weight['종합점수'].rank(ascending=True, axis=0).astype(int)
        data_weight['종합순위_퍼센트'] = (data_weight['종합순위'] / len(data_weight)) * 100
        
        # 기준 순위 대비 변동폭 (순위 상승: 양수)
        if '기본_종합순위' in data_weight.columns:
            data_weight['순위변동'] = data_weight['기본_종합순위'] - data_weight['종합순위']
        else:
            data_weight['순위변동'] = 0

        data_weight.sort_values(by='종합순위', inplace=True)
        data_weight.reset_index(drop=True, inplace=True)
        return data_weight

    def get_base_dataframe(
        self,
        market: str = "KR",
        n_stocks: int = 50,
        use_live: bool = False,
        force_refresh: bool = False
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        기초 데이터 및 8대 팩터 백분위 점수 수집/캐싱
        투자 스타일이나 가중치가 바뀌어도 데이터를 재수집하지 않고 캐시된 base DataFrame 재사용
        """
        cache_key = (market.upper(), n_stocks, use_live)
        if not force_refresh and cache_key in self._cache:
            df_cached, meta_cached = self._cache[cache_key]
            meta = meta_cached.copy()
            meta["from_cache"] = True
            return df_cached.copy(), meta

        start_time = time.time()
        meta = {"market": market, "mode": "fixture", "from_cache": False}

        if use_live:
            try:
                if market.upper() in ["KR", "KRX"]:
                    from MultiFactor import MultiFactorKR
                    mf = MultiFactorKR(N=min(n_stocks, 30))
                    df_raw = mf.get_score()
                    df_raw = merge_krx_sectors(df_raw, code_col='scode')
                    meta["mode"] = "live_package"
                else:
                    from MultiFactor import MultiFactorUS
                    mf = MultiFactorUS(N=min(n_stocks, 30))
                    df_raw = mf.get_score()
                    meta["mode"] = "live_package"

                df_base = df_raw.copy()
                if '종합순위' in df_base.columns and '기본_종합순위' not in df_base.columns:
                    df_base['기본_종합순위'] = df_base['종합순위'].astype(int)
                if '종합점수' in df_base.columns and '기본_종합점수' not in df_base.columns:
                    df_base['기본_종합점수'] = df_base['종합점수']
            except Exception as e:
                meta["mode"] = f"fallback_due_to_error: {str(e)}"
                df_raw = get_fixture_dataframe(market)
                df_base = self.calculate_base_scores(df_raw.iloc[:n_stocks])
        else:
            df_raw = get_fixture_dataframe(market)
            df_base = self.calculate_base_scores(df_raw.iloc[:n_stocks])

        meta["elapsed_sec"] = round(time.time() - start_time, 4)
        meta["total_stocks"] = len(df_base)
        self._cache[cache_key] = (df_base.copy(), meta.copy())
        return df_base, meta

    def run_scoring(
        self,
        market: str = "KR",
        n_stocks: int = 50,
        style: str = "균등",
        custom_weights: Optional[Dict[str, float]] = None,
        use_live: bool = False,
        base_df: Optional[pd.DataFrame] = None,
        force_refresh: bool = False
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        시장(KR/US), 종목수(N), 투자스타일, 커스텀 가중치에 따라 최종 스코어링 실행
        기존에 수집된 base_df가 주어지면 데이터 재수집 없이 0.001초 만에 가중치만 재적용
        """
        start_time = time.time()
        if base_df is not None:
            df_base = base_df.copy()
            meta = {"market": market, "style": style, "from_cached_base": True, "mode": "instant_weighting"}
        else:
            df_base, meta = self.get_base_dataframe(
                market=market,
                n_stocks=n_stocks,
                use_live=use_live,
                force_refresh=force_refresh
            )
            meta["style"] = style

        # 가중치 결정
        if custom_weights is not None:
            weights = [custom_weights.get(col, 1.0) for col in FACTOR_COLS]
            meta["applied_weights_type"] = "custom"
        else:
            weights = STYLE_WEIGHT_PRESETS.get(style, STYLE_WEIGHT_PRESETS['균등'])
            meta["applied_weights_type"] = f"preset_{style}"

        df_scored = self.apply_weights(df_base, weights)
        meta["scoring_elapsed_sec"] = round(time.time() - start_time, 4)
        meta["total_stocks"] = len(df_scored)
        return df_scored, meta

    @staticmethod
    def get_ngroups(df: pd.DataFrame, n_groups: int = 5) -> List[Dict[str, Any]]:
        """
        MultiFactor의 get_Ngroup 로직을 웹 인터랙티브용 구조체로 변환
        순위별로 n_groups 분할 후 그룹별 대표 통계량 산출
        """
        n_groups = int(n_groups)
        n = len(df)
        if n_groups <= 1 or n_groups > 100 or n_groups > n:
            n_groups = min(5, max(2, n))

        sorted_df = df.sort_values(by='종합순위').reset_index(drop=True)
        # NumPy 2.x 호환성을 위해 인덱스 기반 분할 후 DataFrame 슬라이싱 유지
        split_indices = np.array_split(range(n), n_groups)
        chunks = [sorted_df.iloc[idx] for idx in split_indices]

        groups_summary = []
        for i, chunk in enumerate(chunks, 1):
            group_info = {
                "group_number": i,
                "label": f"그룹 {i} (상위 {round((i-1)/n_groups*100)}% ~ {round(i/n_groups*100)}%)",
                "count": len(chunk),
                "stocks": chunk['sname'].tolist(),
                "top_tickers": chunk[['scode', 'sname']].head(5).to_dict(orient='records'),
                "avg_score": round(chunk['종합점수'].mean(), 2),
                "avg_per": round(chunk['PER'].mean(), 2) if 'PER' in chunk.columns else 0.0,
                "avg_pbr": round(chunk['PBR'].mean(), 2) if 'PBR' in chunk.columns else 0.0,
                "avg_roe": round(chunk['ROE'].mean(), 2) if 'ROE' in chunk.columns else 0.0,
                "avg_mom_price": round(chunk['mom_price'].mean(), 2) if 'mom_price' in chunk.columns else 0.0,
            }
            groups_summary.append(group_info)

        return groups_summary
