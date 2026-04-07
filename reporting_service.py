from dotenv import load_dotenv
load_dotenv()                                          # .env에서 OPENAI_API_KEY 로드

from langchain_openai import ChatOpenAI                # OpenAI LLM
from langchain_core.prompts import ChatPromptTemplate  # 프롬프트 템플릿 (4장)
from langchain_core.output_parsers import StrOutputParser  # 텍스트 출력 파서 (5장)
from langchain_core.globals import set_llm_cache       # 전역 캐시 설정 (8장)
from langchain_community.cache import SQLiteCache      # SQLite 파일 캐시 (8장)

from report_schema import InvestmentReport             # 위에서 정의한 JSON 스키마

# ===== [8장] 캐싱 설정 =====
# 같은 회사를 다시 분석하면 LLM을 호출하지 않고 캐시에서 즉시 반환
# report_cache.db 파일이 프로젝트 폴더에 자동 생성됩니다
set_llm_cache(SQLiteCache(database_path="report_cache.db"))

# ===== [2장] LLM 초기화 =====
# temperature=0.2: 사실 기반 분석이므로 낮은 창의성
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

# ===== [4장] 프롬프트 =====
# {company}, {symbol}, {stock_info}, {financials} — 4개의 변수를 받는 템플릿
# system: LLM의 역할 설정 (금융 분석가)
# human: 사용자 요청 + 도구가 수집한 데이터를 변수로 전달
report_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "당신은 경험이 풍부한 금융 분석가입니다.\n"
     "제공된 기업 기본 정보와 재무제표를 바탕으로 투자 보고서를 작성합니다.\n"
     "데이터에 기반한 객관적인 분석을 하고, 근거 없는 추측은 하지 마세요.\n"
     "한국어로 작성합니다."),
    ("human",
     "{company} ({symbol}) 주식에 대한 투자 보고서를 작성해주세요.\n\n"
     "기본 정보:\n{stock_info}\n\n"
     "재무제표:\n{financials}"),
])

# ===== [3장] LCEL 체인 2개 =====

# 체인 A: 마크다운 보고서 — 프롬프트 → LLM → 텍스트 출력
# 사람이 읽기 좋은 형태 (Streamlit 왼쪽에 표시)
markdown_chain = report_prompt | llm | StrOutputParser()

# 체인 B: 구조화(JSON) 보고서 — 프롬프트 → LLM(스키마 강제) → Pydantic 객체
# 프로그램이 처리하기 좋은 형태 (Streamlit 오른쪽에 표시)
structured_chain = report_prompt | llm.with_structured_output(InvestmentReport)


# ===== 외부에서 호출할 함수 2개 =====

def generate_markdown_report(company: str, symbol: str, stock_info: str, financials: str) -> str:
    """마크다운 형식의 투자 보고서를 생성합니다."""
    return markdown_chain.invoke({
        "company": company,        # 회사명 (예: "Microsoft")
        "symbol": symbol,          # 심볼 (예: "MSFT")
        "stock_info": stock_info,  # get_stock_info 도구의 결과 문자열
        "financials": financials,  # get_financials 도구의 결과 문자열
    })


def generate_structured_report(company: str, symbol: str, stock_info: str, financials: str) -> InvestmentReport:
    """구조화된(JSON) 투자 보고서를 생성합니다. InvestmentReport 객체 반환."""
    return structured_chain.invoke({
        "company": company,
        "symbol": symbol,
        "stock_info": stock_info,
        "financials": financials,
    })
