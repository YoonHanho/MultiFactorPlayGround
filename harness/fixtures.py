"""
harness/fixtures.py
MultiFactor 테스트 및 즉각적인 시뮬레이션을 위한 고품질 표준 데이터셋(Fixtures)
국내(KRX KOSPI/KOSDAQ) 및 미국(S&P 500) 시가총액 상위 종목의 실제 퀀트 지표 기반
"""

import pandas as pd
import numpy as np

KR_SAMPLE_STOCKS = [
    {"scode": "005930", "sname": "삼성전자", "sector": "반도체/IT", "marcap": 4800000, "mom_price": 28.5, "mom_vol": 115.4, "PER": 13.8, "PBR": 1.25, "revenue_rate": 12.4, "oper_income_rate": 45.2, "net_income_rate": 38.6, "ROE": 11.2},
    {"scode": "000660", "sname": "SK하이닉스", "sector": "반도체/IT", "marcap": 1400000, "mom_price": 84.2, "mom_vol": 168.0, "PER": 9.4, "PBR": 1.82, "revenue_rate": 34.6, "oper_income_rate": 182.5, "net_income_rate": 154.0, "ROE": 19.8},
    {"scode": "373220", "sname": "LG에너지솔루션", "sector": "2차전지", "marcap": 920000, "mom_price": -15.4, "mom_vol": 82.1, "PER": 58.2, "PBR": 3.95, "revenue_rate": -8.5, "oper_income_rate": -24.2, "net_income_rate": -31.0, "ROE": 4.8},
    {"scode": "207940", "sname": "삼성바이오로직스", "sector": "바이오/헬스케어", "marcap": 710000, "mom_price": 35.8, "mom_vol": 94.6, "PER": 62.4, "PBR": 6.10, "revenue_rate": 22.1, "oper_income_rate": 28.4, "net_income_rate": 25.0, "ROE": 10.4},
    {"scode": "005380", "sname": "현대차", "sector": "자동차/운송", "marcap": 520000, "mom_price": 42.1, "mom_vol": 142.3, "PER": 5.4, "PBR": 0.68, "revenue_rate": 8.9, "oper_income_rate": 14.8, "net_income_rate": 12.3, "ROE": 13.5},
    {"scode": "000270", "sname": "기아", "sector": "자동차/운송", "marcap": 410000, "mom_price": 38.4, "mom_vol": 128.9, "PER": 4.8, "PBR": 0.79, "revenue_rate": 10.2, "oper_income_rate": 18.6, "net_income_rate": 15.4, "ROE": 17.8},
    {"scode": "068270", "sname": "셀트리온", "sector": "바이오/헬스케어", "marcap": 390000, "mom_price": 12.6, "mom_vol": 105.2, "PER": 45.1, "PBR": 2.85, "revenue_rate": 28.6, "oper_income_rate": 19.4, "net_income_rate": 18.2, "ROE": 7.5},
    {"scode": "105560", "sname": "KB금융", "sector": "금융/지주", "marcap": 360000, "mom_price": 55.4, "mom_vol": 132.5, "PER": 6.2, "PBR": 0.52, "revenue_rate": 7.4, "oper_income_rate": 11.2, "net_income_rate": 9.8, "ROE": 9.8},
    {"scode": "035420", "sname": "NAVER", "sector": "인터넷/플랫폼", "marcap": 310000, "mom_price": -6.2, "mom_vol": 89.4, "PER": 22.8, "PBR": 1.42, "revenue_rate": 11.5, "oper_income_rate": 16.8, "net_income_rate": 14.2, "ROE": 6.8},
    {"scode": "055550", "sname": "신한지주", "sector": "금융/지주", "marcap": 290000, "mom_price": 48.2, "mom_vol": 121.0, "PER": 5.8, "PBR": 0.48, "revenue_rate": 6.8, "oper_income_rate": 9.5, "net_income_rate": 8.7, "ROE": 9.2},
    {"scode": "005490", "sname": "POSCO홀딩스", "sector": "철강/소재", "marcap": 270000, "mom_price": -24.8, "mom_vol": 76.5, "PER": 18.4, "PBR": 0.62, "revenue_rate": -4.2, "oper_income_rate": -15.4, "net_income_rate": -18.6, "ROE": 3.8},
    {"scode": "035720", "sname": "카카오", "sector": "인터넷/플랫폼", "marcap": 190000, "mom_price": -18.9, "mom_vol": 72.3, "PER": 34.6, "PBR": 1.55, "revenue_rate": 6.2, "oper_income_rate": 8.4, "net_income_rate": 5.1, "ROE": 4.2},
    {"scode": "012330", "sname": "현대모비스", "sector": "자동차/운송", "marcap": 210000, "mom_price": 14.8, "mom_vol": 98.4, "PER": 6.8, "PBR": 0.54, "revenue_rate": 5.8, "oper_income_rate": 12.1, "net_income_rate": 10.5, "ROE": 8.4},
    {"scode": "051910", "sname": "LG화학", "sector": "화학/소재", "marcap": 220000, "mom_price": -32.5, "mom_vol": 68.9, "PER": 24.5, "PBR": 0.82, "revenue_rate": -3.5, "oper_income_rate": -28.5, "net_income_rate": -35.2, "ROE": 3.2},
    {"scode": "086790", "sname": "하나금융지주", "sector": "금융/지주", "marcap": 185000, "mom_price": 52.1, "mom_vol": 125.4, "PER": 4.9, "PBR": 0.42, "revenue_rate": 7.1, "oper_income_rate": 10.4, "net_income_rate": 9.2, "ROE": 9.5},
    {"scode": "028260", "sname": "삼성물산", "sector": "지주/종합상사", "marcap": 245000, "mom_price": 26.4, "mom_vol": 104.8, "PER": 12.2, "PBR": 0.74, "revenue_rate": 6.5, "oper_income_rate": 14.2, "net_income_rate": 13.0, "ROE": 6.5},
    {"scode": "032830", "sname": "삼성생명", "sector": "보험/금융", "marcap": 195000, "mom_price": 45.8, "mom_vol": 118.2, "PER": 9.8, "PBR": 0.58, "revenue_rate": 8.4, "oper_income_rate": 12.8, "net_income_rate": 11.5, "ROE": 6.8},
    {"scode": "009150", "sname": "삼성전기", "sector": "IT부품/전자", "marcap": 115000, "mom_price": 19.8, "mom_vol": 102.5, "PER": 16.4, "PBR": 1.48, "revenue_rate": 14.2, "oper_income_rate": 22.4, "net_income_rate": 18.5, "ROE": 9.6},
    {"scode": "018260", "sname": "삼성에스디에스", "sector": "IT서비스", "marcap": 125000, "mom_price": 8.4, "mom_vol": 88.6, "PER": 15.2, "PBR": 1.32, "revenue_rate": 7.8, "oper_income_rate": 11.5, "net_income_rate": 9.8, "ROE": 9.1},
    {"scode": "034730", "sname": "SK", "sector": "지주", "marcap": 110000, "mom_price": 11.5, "mom_vol": 92.4, "PER": 14.8, "PBR": 0.52, "revenue_rate": 5.2, "oper_income_rate": 10.8, "net_income_rate": 8.9, "ROE": 5.4},
    {"scode": "010130", "sname": "고려아연", "sector": "비철금속/소재", "marcap": 215000, "mom_price": 95.4, "mom_vol": 245.8, "PER": 28.5, "PBR": 2.15, "revenue_rate": 18.4, "oper_income_rate": 24.6, "net_income_rate": 21.0, "ROE": 8.2},
    {"scode": "003550", "sname": "LG", "sector": "지주", "marcap": 120000, "mom_price": 6.8, "mom_vol": 84.5, "PER": 8.9, "PBR": 0.56, "revenue_rate": 4.1, "oper_income_rate": 7.5, "net_income_rate": 6.8, "ROE": 6.9},
    {"scode": "316140", "sname": "우리금융지주", "sector": "금융/지주", "marcap": 125000, "mom_price": 41.2, "mom_vol": 114.2, "PER": 4.2, "PBR": 0.38, "revenue_rate": 6.5, "oper_income_rate": 8.9, "net_income_rate": 8.1, "ROE": 9.4},
    {"scode": "015760", "sname": "한국전력", "sector": "유틸리티", "marcap": 145000, "mom_price": 24.5, "mom_vol": 110.5, "PER": 8.4, "PBR": 0.45, "revenue_rate": 9.8, "oper_income_rate": 164.0, "net_income_rate": 142.0, "ROE": 7.8},
    {"scode": "033780", "sname": "KT&G", "sector": "음식료/필수소비", "marcap": 140000, "mom_price": 31.2, "mom_vol": 108.4, "PER": 12.8, "PBR": 1.15, "revenue_rate": 5.4, "oper_income_rate": 8.2, "net_income_rate": 7.5, "ROE": 9.2},
    {"scode": "000810", "sname": "삼성화재", "sector": "보험/금융", "marcap": 165000, "mom_price": 49.5, "mom_vol": 122.0, "PER": 8.2, "PBR": 0.88, "revenue_rate": 9.2, "oper_income_rate": 15.4, "net_income_rate": 14.1, "ROE": 11.5},
    {"scode": "011200", "sname": "HMM", "sector": "해운/운송", "marcap": 128000, "mom_price": 18.2, "mom_vol": 101.5, "PER": 6.5, "PBR": 0.65, "revenue_rate": 22.4, "oper_income_rate": 68.5, "net_income_rate": 62.0, "ROE": 12.4},
    {"scode": "009540", "sname": "HD한국조선해양", "sector": "조선/중공업", "marcap": 138000, "mom_price": 72.4, "mom_vol": 154.2, "PER": 18.2, "PBR": 1.28, "revenue_rate": 24.5, "oper_income_rate": 142.0, "net_income_rate": 125.0, "ROE": 8.5},
    {"scode": "042660", "sname": "한화오션", "sector": "조선/중공업", "marcap": 105000, "mom_price": 64.8, "mom_vol": 148.0, "PER": 24.5, "PBR": 2.45, "revenue_rate": 32.1, "oper_income_rate": 88.5, "net_income_rate": 78.4, "ROE": 6.8},
    {"scode": "010950", "sname": "S-Oil", "sector": "정유/에너지", "marcap": 78000, "mom_price": -11.2, "mom_vol": 82.5, "PER": 9.5, "PBR": 0.84, "revenue_rate": 2.5, "oper_income_rate": -12.4, "net_income_rate": -15.8, "ROE": 8.1},
]

US_SAMPLE_STOCKS = [
    {"scode": "NVDA", "sname": "NVIDIA", "sector": "Information Technology", "marcap": 3500000, "mom_price": 185.4, "mom_vol": 195.0, "PER": 55.4, "PBR": 42.5, "revenue_rate": 122.5, "oper_income_rate": 174.2, "net_income_rate": 168.0, "ROE": 88.5},
    {"scode": "AAPL", "sname": "Apple", "sector": "Information Technology", "marcap": 3450000, "mom_price": 24.8, "mom_vol": 112.5, "PER": 33.2, "PBR": 48.0, "revenue_rate": 6.2, "oper_income_rate": 9.8, "net_income_rate": 8.5, "ROE": 154.0},
    {"scode": "MSFT", "sname": "Microsoft", "sector": "Information Technology", "marcap": 3200000, "mom_price": 18.4, "mom_vol": 105.8, "PER": 34.8, "PBR": 11.8, "revenue_rate": 15.4, "oper_income_rate": 18.9, "net_income_rate": 16.5, "ROE": 38.2},
    {"scode": "AMZN", "sname": "Amazon", "sector": "Consumer Discretionary", "marcap": 2150000, "mom_price": 42.5, "mom_vol": 128.4, "PER": 42.1, "PBR": 8.4, "revenue_rate": 12.8, "oper_income_rate": 54.2, "net_income_rate": 48.6, "ROE": 21.4},
    {"scode": "GOOGL", "sname": "Alphabet (Google)", "sector": "Communication Services", "marcap": 2100000, "mom_price": 28.9, "mom_vol": 118.0, "PER": 23.5, "PBR": 6.5, "revenue_rate": 14.1, "oper_income_rate": 28.5, "net_income_rate": 32.4, "ROE": 31.5},
    {"scode": "META", "sname": "Meta Platforms", "sector": "Communication Services", "marcap": 1450000, "mom_price": 68.2, "mom_vol": 142.1, "PER": 26.8, "PBR": 8.8, "revenue_rate": 22.4, "oper_income_rate": 42.1, "net_income_rate": 38.5, "ROE": 34.8},
    {"scode": "TSLA", "sname": "Tesla", "sector": "Consumer Discretionary", "marcap": 1050000, "mom_price": 45.1, "mom_vol": 164.2, "PER": 84.5, "PBR": 14.2, "revenue_rate": 8.4, "oper_income_rate": 12.5, "net_income_rate": 9.4, "ROE": 18.5},
    {"scode": "AVGO", "sname": "Broadcom", "sector": "Information Technology", "marcap": 850000, "mom_price": 74.2, "mom_vol": 138.5, "PER": 36.5, "PBR": 12.4, "revenue_rate": 44.5, "oper_income_rate": 62.0, "net_income_rate": 58.2, "ROE": 24.8},
    {"scode": "BRK-B", "sname": "Berkshire Hathaway", "sector": "Financials", "marcap": 980000, "mom_price": 26.4, "mom_vol": 95.4, "PER": 19.8, "PBR": 1.62, "revenue_rate": 7.5, "oper_income_rate": 14.2, "net_income_rate": 12.8, "ROE": 12.4},
    {"scode": "JPM", "sname": "JPMorgan Chase", "sector": "Financials", "marcap": 680000, "mom_price": 38.6, "mom_vol": 122.4, "PER": 12.4, "PBR": 1.85, "revenue_rate": 9.8, "oper_income_rate": 16.5, "net_income_rate": 14.2, "ROE": 17.5},
    {"scode": "LLY", "sname": "Eli Lilly", "sector": "Health Care", "marcap": 780000, "mom_price": 54.8, "mom_vol": 131.0, "PER": 64.2, "PBR": 38.5, "revenue_rate": 38.4, "oper_income_rate": 68.2, "net_income_rate": 62.5, "ROE": 62.1},
    {"scode": "WMT", "sname": "Walmart", "sector": "Consumer Staples", "marcap": 690000, "mom_price": 52.4, "mom_vol": 116.8, "PER": 32.4, "PBR": 7.2, "revenue_rate": 5.8, "oper_income_rate": 9.2, "net_income_rate": 8.4, "ROE": 21.2},
    {"scode": "XOM", "sname": "ExxonMobil", "sector": "Energy", "marcap": 480000, "mom_price": 14.2, "mom_vol": 92.4, "PER": 14.1, "PBR": 2.1, "revenue_rate": 2.1, "oper_income_rate": 4.5, "net_income_rate": 3.8, "ROE": 16.4},
    {"scode": "UNH", "sname": "UnitedHealth Group", "sector": "Health Care", "marcap": 520000, "mom_price": 8.5, "mom_vol": 89.2, "PER": 24.8, "PBR": 5.4, "revenue_rate": 9.2, "oper_income_rate": 11.4, "net_income_rate": 10.2, "ROE": 24.5},
    {"scode": "MA", "sname": "Mastercard", "sector": "Financials", "marcap": 470000, "mom_price": 28.2, "mom_vol": 104.5, "PER": 35.4, "PBR": 68.0, "revenue_rate": 12.8, "oper_income_rate": 16.2, "net_income_rate": 15.4, "ROE": 182.0},
    {"scode": "COST", "sname": "Costco Wholesale", "sector": "Consumer Staples", "marcap": 410000, "mom_price": 48.6, "mom_vol": 119.5, "PER": 52.1, "PBR": 15.8, "revenue_rate": 8.9, "oper_income_rate": 12.8, "net_income_rate": 11.6, "ROE": 29.5},
    {"scode": "HD", "sname": "Home Depot", "sector": "Consumer Discretionary", "marcap": 390000, "mom_price": 22.4, "mom_vol": 98.4, "PER": 26.5, "PBR": 320.0, "revenue_rate": 4.2, "oper_income_rate": 6.8, "net_income_rate": 5.9, "ROE": 1150.0},
    {"scode": "PG", "sname": "Procter & Gamble", "sector": "Consumer Staples", "marcap": 395000, "mom_price": 12.1, "mom_vol": 88.5, "PER": 27.2, "PBR": 8.4, "revenue_rate": 3.5, "oper_income_rate": 5.8, "net_income_rate": 5.1, "ROE": 32.8},
    {"scode": "AMD", "sname": "Advanced Micro Devices", "sector": "Information Technology", "marcap": 230000, "mom_price": 15.4, "mom_vol": 135.0, "PER": 48.5, "PBR": 3.8, "revenue_rate": 18.2, "oper_income_rate": 45.0, "net_income_rate": 38.0, "ROE": 6.8},
    {"scode": "CRM", "sname": "Salesforce", "sector": "Information Technology", "marcap": 310000, "mom_price": 32.5, "mom_vol": 112.0, "PER": 38.2, "PBR": 4.9, "revenue_rate": 11.2, "oper_income_rate": 24.5, "net_income_rate": 22.0, "ROE": 12.8},
    {"scode": "MU", "sname": "Micron Technology", "sector": "Information Technology", "marcap": 125000, "mom_price": 62.4, "mom_vol": 155.0, "PER": 18.5, "PBR": 2.4, "revenue_rate": 82.5, "oper_income_rate": 210.0, "net_income_rate": 195.0, "ROE": 14.2},
    {"scode": "QCOM", "sname": "Qualcomm", "sector": "Information Technology", "marcap": 185000, "mom_price": 24.2, "mom_vol": 115.0, "PER": 17.5, "PBR": 6.8, "revenue_rate": 14.5, "oper_income_rate": 22.0, "net_income_rate": 19.5, "ROE": 42.0},
    {"scode": "TXN", "sname": "Texas Instruments", "sector": "Information Technology", "marcap": 175000, "mom_price": 18.5, "mom_vol": 96.0, "PER": 32.0, "PBR": 10.5, "revenue_rate": 2.5, "oper_income_rate": 4.8, "net_income_rate": 3.9, "ROE": 31.0},
    {"scode": "BAC", "sname": "Bank of America", "sector": "Financials", "marcap": 350000, "mom_price": 34.5, "mom_vol": 120.0, "PER": 14.2, "PBR": 1.35, "revenue_rate": 6.8, "oper_income_rate": 11.2, "net_income_rate": 10.1, "ROE": 10.5},
    {"scode": "CAT", "sname": "Caterpillar", "sector": "Industrials", "marcap": 195000, "mom_price": 41.2, "mom_vol": 118.0, "PER": 18.5, "PBR": 8.9, "revenue_rate": 4.8, "oper_income_rate": 14.5, "net_income_rate": 12.8, "ROE": 54.0},
]

_FIXTURE_CACHE = {}

def get_fixture_dataframe(market: str = "KR") -> pd.DataFrame:
    """테스트 및 플레이그라운드용 200개 종목 고속 표준 데이터셋 반환 (메모리 캐싱 지원)"""
    market_key = "KR" if market.upper() in ["KR", "KRX"] else "US"
    if market_key in _FIXTURE_CACHE:
        return _FIXTURE_CACHE[market_key].copy()

    file_name = f"data/{'kr' if market_key=='KR' else 'us'}_stocks_200.csv"
    try:
        df = pd.read_csv(file_name, dtype={'scode': str})
        df['scode'] = df['scode'].astype(str).str.zfill(6 if market_key == 'KR' else 1)
        _FIXTURE_CACHE[market_key] = df
        return df.copy()
    except Exception:
        data = KR_SAMPLE_STOCKS if market_key == "KR" else US_SAMPLE_STOCKS
        df = pd.DataFrame(data)
        _FIXTURE_CACHE[market_key] = df
        return df.copy()

def export_fixture_csvs(data_dir: str = "data"):
    """CSV 파일로 캐시 저장"""
    kr_df = pd.DataFrame(KR_SAMPLE_STOCKS)
    us_df = pd.DataFrame(US_SAMPLE_STOCKS)
    kr_df.to_csv(f"{data_dir}/kr_stocks_sample.csv", index=False, encoding="utf-8-sig")
    us_df.to_csv(f"{data_dir}/us_stocks_sample.csv", index=False, encoding="utf-8-sig")
