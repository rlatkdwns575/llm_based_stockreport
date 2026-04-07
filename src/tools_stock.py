import yfinance as yf                    # Yahoo Finance 데이터 라이브러리
import pandas as pd                      # 데이터 처리 (to_markdown 변환에 필요)
from langchain_core.tools import tool    # @tool 데코레이터 — 함수를 LLM 도구로 등록

# ========== 도구 1: 회사명 → 심볼 검색 ==========
# "Apple" 같은 회사명을 입력하면 "AAPL" 같은 주식 심볼을 찾아줍니다.
# LLM이 사용자 질문에서 회사명을 추출 → 이 도구를 호출하여 심볼 획득

@tool
def search_company(query: str) -> str:
    """회사명으로 주식 심볼(ticker)을 검색합니다. 예: 'Apple' → 'AAPL'"""
    try:
        # yf.Search: Yahoo Finance의 자동완성 검색 API
        results = yf.Search(query, max_results=5).quotes
        if not results:
            return f"'{query}'에 대한 검색 결과가 없습니다."
        lines = []
        for r in results:
            symbol = r.get("symbol", "")            # 심볼 (예: AAPL)
            name = r.get("longname") or r.get("shortname", "")  # 회사명
            exchange = r.get("exchange", "")         # 거래소 (예: NMS)
            lines.append(f"- {symbol}: {name} ({exchange})")
        return "검색 결과:\n" + "\n".join(lines)
    except Exception as e:
        return f"검색 실패: {e}"

# ========== 도구 2: 심볼 → 기본 정보 조회 ==========
# 시가총액, P/E, 현재가 등 회사의 핵심 지표를 가져옵니다.

@tool
def get_stock_info(symbol: str) -> str:
    """주식 심볼로 회사 기본 정보(시가총액, P/E, 업종 등)를 조회합니다."""
    try:
        info = yf.Ticker(symbol).info    # Yahoo Finance에서 회사 정보 딕셔너리 가져오기
        if not info or len(info) < 5:    # 데이터가 너무 적으면 실패 처리
            return f"'{symbol}'의 정보를 가져올 수 없습니다."
        # .get(key, default)로 안전하게 접근 — Yahoo가 키를 제거해도 에러 안 남
        return (
            f"회사명: {info.get('longName', 'N/A')}\n"
            f"업종: {info.get('industry', 'N/A')}\n"
            f"부문: {info.get('sector', 'N/A')}\n"
            f"시가총액: ${info.get('marketCap', 0):,.0f}\n"        # :,.0f → 쉼표 포함 정수
            f"현재가: ${info.get('currentPrice', 0):,.2f}\n"       # :,.2f → 소수점 2자리
            f"P/E (trailing): {info.get('trailingPE', 'N/A')}\n"   # 주가수익비율
            f"P/B: {info.get('priceToBook', 'N/A')}\n"             # 주가순자산비율
            f"EPS: {info.get('trailingEps', 'N/A')}\n"             # 주당순이익
            f"52주 최고: ${info.get('fiftyTwoWeekHigh', 0):,.2f}\n"
            f"52주 최저: ${info.get('fiftyTwoWeekLow', 0):,.2f}"
        )
    except Exception as e:
        return f"정보 조회 실패: {e}"

# ========== 도구 3: 심볼 → 재무제표 조회 ==========
# 분기별 손익계산서, 대차대조표, 현금흐름표를 마크다운 표로 반환합니다.

@tool
def get_financials(symbol: str) -> str:
    """주식 심볼로 분기별 재무제표(손익계산서, 대차대조표, 현금흐름표)를 조회합니다."""
    try:
        ticker = yf.Ticker(symbol)
        parts = []    # 각 재무제표를 문자열로 모아둘 리스트

        # --- 손익계산서 ---
        income = ticker.quarterly_income_stmt       # 분기별 손익계산서 DataFrame
        if not income.empty:
            rows = ["Total Revenue", "Gross Profit", "Operating Income", "Net Income"]
            available = [r for r in rows if r in income.index]   # 실제 존재하는 항목만
            if available:
                parts.append("### 분기별 손익계산서\n" + income.loc[available].to_markdown())

        # --- 대차대조표 ---
        balance = ticker.quarterly_balance_sheet
        if not balance.empty:
            rows = ["Total Assets", "Total Liabilities Net Minority Interest", "Stockholders Equity"]
            available = [r for r in rows if r in balance.index]
            if available:
                parts.append("### 분기별 대차대조표\n" + balance.loc[available].to_markdown())

        # --- 현금흐름표 ---
        cashflow = ticker.quarterly_cash_flow
        if not cashflow.empty:
            rows = ["Operating Cash Flow", "Investing Cash Flow", "Financing Cash Flow"]
            available = [r for r in rows if r in cashflow.index]
            if available:
                parts.append("### 분기별 현금흐름표\n" + cashflow.loc[available].to_markdown())

        # 모든 재무제표를 합쳐서 반환
        return "\n\n".join(parts) if parts else f"'{symbol}'의 재무제표를 가져올 수 없습니다."
    except Exception as e:
        return f"재무제표 조회 실패: {e}"

# 도구 리스트 — 다른 파일에서 import하여 사용
tools = [search_company, get_stock_info, get_financials]
