"""
harness/test_suite.py
하네스 기법 기반 자동화 검증 스위트 (MultiFactor Verification Suite)
패키지 수식, 순위화 방향성, 가중치 최적화, 결측치 보정, N그룹 분할의 정합성 보증
"""

import unittest
import numpy as np
import pandas as pd

from .engine import MultiFactorHarnessEngine, FACTOR_COLS, STYLE_WEIGHT_PRESETS
from .fixtures import get_fixture_dataframe

class MultiFactorHarnessTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = MultiFactorHarnessEngine()
        self.kr_df = get_fixture_dataframe("KR")
        self.us_df = get_fixture_dataframe("US")

    def test_01_factor_ranking_directions(self):
        """1. 팩터별 순위화 방향성 검증 (PER/PBR: 오름차순, 모멘텀/ROE: 내림차순)"""
        scored_kr = self.engine.calculate_base_scores(self.kr_df)

        # PER이 가장 낮은 종목이 밸류_PER 점수가 가장 낮아야 함 (상위 우수)
        min_per_idx = scored_kr['PER'].idxmin()
        self.assertEqual(scored_kr.loc[min_per_idx, '밸류_PER'], scored_kr['밸류_PER'].min())

        # mom_price가 가장 높은 종목이 모멘텀_주가 점수가 가장 낮아야 함 (상위 우수)
        max_mom_idx = scored_kr['mom_price'].idxmax()
        self.assertEqual(scored_kr.loc[max_mom_idx, '모멘텀_주가'], scored_kr['모멘텀_주가'].min())

        # ROE가 가장 높은 종목이 퀄리티_ROE 점수가 가장 낮아야 함
        max_roe_idx = scored_kr['ROE'].idxmax()
        self.assertEqual(scored_kr.loc[max_roe_idx, '퀄리티_ROE'], scored_kr['퀄리티_ROE'].min())

    def test_02_style_weight_presets(self):
        """2. 4대 투자 스타일별 가중치 적용 정합성 검증"""
        base_df = self.engine.calculate_base_scores(self.kr_df)

        # ① 균등 (Equal)
        equal_res = self.engine.apply_weights(base_df, STYLE_WEIGHT_PRESETS['균등'])
        self.assertEqual(len(equal_res), len(base_df))
        self.assertTrue((equal_res['종합순위'] >= 1).all())

        # ② 추세성장 (Momentum + Quality: Value 0)
        trend_res = self.engine.apply_weights(base_df, STYLE_WEIGHT_PRESETS['추세성장'])
        self.assertIn('종합순위', trend_res.columns)

        # ③ 가치성장 (Value + Quality: Momentum 0)
        val_res = self.engine.apply_weights(base_df, STYLE_WEIGHT_PRESETS['가치성장'])
        self.assertIn('종합순위', val_res.columns)

        # ④ 역발상 (Value + Momentum: Quality 0)
        con_res = self.engine.apply_weights(base_df, STYLE_WEIGHT_PRESETS['역발상'])
        self.assertIn('종합순위', con_res.columns)

    def test_03_custom_weights_rescaling(self):
        """3. 커스텀 가중치 자동 정규화 및 점수 재계산 검증"""
        base_df = self.engine.calculate_base_scores(self.kr_df)
        custom_weights = [10.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] # 100% 주가 모멘텀 올인
        res = self.engine.apply_weights(base_df, custom_weights)

        # 종합점수가 '모멘텀_주가' 백분위와 정확히 동일해야 함
        np.testing.assert_array_almost_equal(res['종합점수'].values, res['모멘텀_주가'].values)

    def test_04_missing_and_infinite_value_handling(self):
        """4. 결측치(NaN) 및 무한대(Inf) 입력 시 중앙값 대체 견고성 검증"""
        dirty_df = self.kr_df.copy()
        dirty_df.loc[0, 'PER'] = np.nan
        dirty_df.loc[1, 'ROE'] = np.inf
        dirty_df.loc[2, 'mom_price'] = -np.inf

        cleaned_scored = self.engine.calculate_base_scores(dirty_df)
        self.assertFalse(cleaned_scored['종합점수'].isna().any())
        self.assertFalse(np.isinf(cleaned_scored['종합점수']).any())

    def test_05_ngroup_partitioning(self):
        """5. N-그룹 분할 로직 검증 (array_split 및 그룹 통계량)"""
        scored_kr, _ = self.engine.run_scoring(market="KR", n_stocks=30, style="균등")
        groups = self.engine.get_ngroups(scored_kr, n_groups=5)

        self.assertEqual(len(groups), 5)
        total_stocks = sum(g['count'] for g in groups)
        self.assertEqual(total_stocks, 30)

        # 1그룹의 평균 종합점수가 5그룹보다 낮아야 함 (1그룹이 우수)
        self.assertLess(groups[0]['avg_score'], groups[-1]['avg_score'])

    def test_06_package_import_parity(self):
        """6. 실제 설치된 MultiFactor 패키지 인터페이스 호환성 검증"""
        import MultiFactor
        self.assertTrue(hasattr(MultiFactor, 'MultiFactorKR'))
        self.assertTrue(hasattr(MultiFactor, 'MultiFactorUS'))
        self.assertTrue(hasattr(MultiFactor, 'Visual'))
        self.assertTrue(hasattr(MultiFactor, 'get_daum_finstate'))
        self.assertTrue(hasattr(MultiFactor, 'get_daum_consensus'))

    def test_07_krx_desc_sector_merge(self):
        """7. KRX-DESC 표준 업종 헬퍼 함수 조인 정합성 검증"""
        from .engine import merge_krx_sectors
        sample_df = pd.DataFrame({'scode': ['005930', '000660', '005380']})
        merged = merge_krx_sectors(sample_df)
        self.assertIn('sector', merged.columns)
        self.assertEqual(len(merged), 3)
        # 005930(삼성전자) 또는 000660(SK하이닉스)의 sector가 정상 매핑되었는지 확인
        self.assertTrue(any("제조" in str(s) or "통신" in str(s) or "반도체" in str(s) for s in merged['sector']))

def run_all_harness_tests():
    """모든 하네스 단위 테스트 실행 및 결과 사전 반환"""
    suite = unittest.TestLoader().loadTestsFromTestCase(MultiFactorHarnessTestCase)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return {
        "total": result.testsRun,
        "passed": result.testsRun - len(result.failures) - len(result.errors),
        "failures": len(result.failures),
        "errors": len(result.errors),
        "was_successful": result.wasSuccessful()
    }
