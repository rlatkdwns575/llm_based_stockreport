# AI 기반 주식 투자 보고서 생성기

LangChain, OpenAI, Yahoo Finance, Streamlit을 활용하여 만든 **주식 투자 보고서 생성 웹 서비스**입니다.  
사용자가 회사명 또는 주식 심볼을 입력하면, 기업 기본 정보와 분기 재무제표를 수집한 뒤 이를 바탕으로 **마크다운 투자 보고서**와 **구조화된 JSON 분석 결과**를 함께 생성합니다.

---

## 1. 프로젝트 개요

이 프로젝트는 단순한 주가 조회가 아니라,  
**실제 기업 데이터 기반으로 투자 판단에 참고할 수 있는 보고서를 자동 생성**하는 데 목적이 있습니다.

전체 흐름은 다음과 같습니다.

1. 사용자가 회사명 또는 심볼 입력
2. Yahoo Finance에서 기업 정보 및 재무제표 조회
3. LangChain 체인으로 LLM 분석 수행
4. 사람이 읽기 좋은 마크다운 보고서 생성
5. 프로그램이 처리하기 쉬운 JSON 구조 보고서 생성

---

## 2. 주요 기능

- 회사명 검색 및 주식 심볼 선택
- Yahoo Finance 기반 기업 기본 정보 조회
- 분기 손익계산서 / 대차대조표 / 현금흐름표 조회
- LLM 기반 투자 보고서 생성
- 구조화된 JSON 투자 분석 결과 생성
- 동일 요청에 대한 SQLite 캐시 지원
- Streamlit 웹 UI 제공

---

## 3. 기술 스택

- **Python 3.12+**
- **Streamlit**
- **LangChain**
- **OpenAI API**
- **Yahoo Finance (`yfinance`)**
- **Pydantic**
- **SQLite Cache**
- **python-dotenv**

---

## 4. 프로젝트 구조

```bash
llm_based_stockreport/
├─ src/
│  ├─ app.py
│  ├─ report_schema.py
│  ├─ reporting_service.py
│  └─ tools_stock.py
├─ requirements.txt
├─ pyproject.toml
├─ report_cache.db
└─ README.md
