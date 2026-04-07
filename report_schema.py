from pydantic import BaseModel, Field    # Pydantic — JSON 스키마를 Python 클래스로 정의
from typing import Literal               # Literal — 허용 값을 제한 ("매수"/"보유"/"매도" 중 하나만)

# LLM의 응답을 이 구조에 맞춰 JSON으로 반환하게 합니다 (5장 with_structured_output)
# 각 Field의 description은 LLM이 "이 필드에 뭘 넣어야 하는지" 판단하는 데 사용됩니다

class InvestmentReport(BaseModel):
    """구조화된 투자 분석 보고서"""
    symbol: str = Field(description="주식 심볼 (예: AAPL)")
    company_name: str = Field(description="회사명")
    recommendation: Literal["매수", "보유", "매도"] = Field(
        description="투자 추천 의견"
    )
    risk_level: Literal["낮음", "보통", "높음"] = Field(
        description="리스크 수준"
    )
    current_price: str = Field(description="현재 주가")
    pe_ratio: str = Field(description="P/E 비율")
    summary: str = Field(description="2~3문장의 투자 요약")
    key_strengths: list[str] = Field(description="핵심 강점 3가지")
    key_risks: list[str] = Field(description="핵심 리스크 3가지")
    conclusion: str = Field(description="최종 결론 한 문장")
