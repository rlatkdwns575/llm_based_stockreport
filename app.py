import streamlit as st
import yfinance as yf
import json
import time

from dotenv import load_dotenv
load_dotenv()

# 다른 파일에서 도구와 보고서 함수 가져오기
from tools_stock import get_stock_info, get_financials
from reporting_service import generate_markdown_report, generate_structured_report

# ===== 페이지 기본 설정 =====
st.set_page_config(page_title="AI 투자보고서", page_icon="📊", layout="wide")
st.title("📊 AI 투자보고서 생성 서비스")

# ===== 사이드바: 회사 검색 + 심볼 선택 =====
with st.sidebar:
    st.header("회사 검색")
    query = st.text_input("회사명을 입력하세요", "Apple")

    # [검색] 버튼 → yf.Search로 Yahoo Finance 검색 → 결과를 session_state에 저장
    if st.button("🔍 검색", use_container_width=True):
        with st.spinner("검색 중..."):
            try:
                results = yf.Search(query, max_results=10).quotes  # Yahoo 자동완성 API
                # 검색 결과에서 심볼과 회사명만 추출하여 저장
                st.session_state.search_results = [
                    {"symbol": r.get("symbol", ""), "name": r.get("longname") or r.get("shortname", "")}
                    for r in results if r.get("symbol")
                ]
            except Exception as e:
                st.error(f"검색 실패: {e}")
                st.session_state.search_results = []

    # 검색 결과가 있으면 → selectbox(드롭다운)로 선택
    # 검색 결과가 없으면 → 심볼 직접 입력 (한국 종목 등)
    search_results = st.session_state.get("search_results", [])
    if search_results:
        options = [f"{r['symbol']}: {r['name']}" for r in search_results]
        selected = st.selectbox("검색 결과에서 선택하세요", options)
        selected_symbol = selected.split(":")[0].strip() if selected else ""
    else:
        selected_symbol = st.text_input("심볼을 직접 입력하세요", "AAPL")

    st.markdown(f"**선택된 심볼:** `{selected_symbol}`")

    # [보고서 생성] 버튼 → 메인 영역에서 처리
    if st.button("📊 보고서 생성", use_container_width=True, disabled=not selected_symbol):
        st.session_state.target_symbol = selected_symbol
        st.session_state.generate = True     # 메인 영역의 if문을 트리거

# ===== 메인 영역: 보고서 생성 =====
if st.session_state.get("generate"):
    symbol = st.session_state.target_symbol
    st.session_state.generate = False        # 한 번만 실행되도록 리셋

    col1, col2 = st.columns([1, 1])         # 왼쪽: 마크다운, 오른쪽: JSON

    # ---- 데이터 수집 (tools_stock.py의 도구 직접 호출) ----
    with st.status("데이터 수집 중...", expanded=True) as status:
        st.write(f"🔧 {symbol} 기본 정보 조회...")
        stock_info = get_stock_info.invoke({"symbol": symbol})    # 도구 직접 호출

        st.write(f"🔧 {symbol} 재무제표 조회...")
        financials = get_financials.invoke({"symbol": symbol})    # 도구 직접 호출

        status.update(label="데이터 수집 완료!", state="complete", expanded=False)

    # ---- 왼쪽: 마크다운 보고서 ----
    with col1:
        st.header("📝 투자 보고서")
        start = time.time()
        with st.spinner("보고서 생성 중..."):
            md_report = generate_markdown_report(
                company=symbol, symbol=symbol,
                stock_info=str(stock_info), financials=str(financials),
            )
        st.caption(f"⏱️ {time.time() - start:.2f}초")
        st.markdown(md_report)               # 마크다운 렌더링

    # ---- 오른쪽: 구조화 보고서 (JSON) ----
    with col2:
        st.header("📋 구조화 분석 (JSON)")
        start = time.time()
        with st.spinner("구조화 보고서 생성 중..."):
            try:
                structured = generate_structured_report(
                    company=symbol, symbol=symbol,
                    stock_info=str(stock_info), financials=str(financials),
                )
                st.caption(f"⏱️ {time.time() - start:.2f}초")

                # 추천 등급을 색상으로 표시 (매수=초록, 보유=주황, 매도=빨강)
                rec_color = {"매수": "green", "보유": "orange", "매도": "red"}
                st.markdown(f"### 추천: :{rec_color.get(structured.recommendation, 'gray')}[{structured.recommendation}]")
                st.markdown(f"**리스크:** {structured.risk_level}")
                st.markdown(f"**요약:** {structured.summary}")

                st.subheader("핵심 강점")
                for s in structured.key_strengths:
                    st.markdown(f"- ✅ {s}")

                st.subheader("핵심 리스크")
                for r in structured.key_risks:
                    st.markdown(f"- ⚠️ {r}")

                st.markdown(f"**결론:** {structured.conclusion}")

                # JSON 원본을 접을 수 있는 패널로 표시
                with st.expander("원본 JSON 보기"):
                    st.json(structured.model_dump())    # Pydantic → dict → JSON 표시
            except Exception as e:
                st.error(f"구조화 보고서 생성 실패: {e}")

    # ---- 하단: 수집된 원본 데이터 (디버깅용) ----
    with st.expander("📄 수집된 원본 데이터"):
        st.subheader("기본 정보")
        st.text(stock_info)
        st.subheader("재무제표")
        st.text(financials)
