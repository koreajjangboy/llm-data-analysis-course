import json
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
REPORTS_DIR = BASE_DIR / "reports"
load_dotenv(BASE_DIR / ".env")

def build_prompt(summary):
    return f"""
당신은 데이터 분석 보고서 작성 보조자입니다.

아래 값은 Python에서 계산하고 사람이 기본 검증을 완료한 결과입니다.

{json.dumps(summary, ensure_ascii=False, indent=2)}

다음 형식으로 한국어 보고서를 작성하세요.

1. 분석 기준일
2. 검색 관심도 주요 변화
3. 지역 관광 수요 주요 특징
4. 관찰 가능한 패턴
5. 현재 데이터로 말할 수 없는 것
6. 추가 확인이 필요한 사항

중요:
- 검색 관심도는 실제 검색 건수가 아닌 상대지수라고 명시하세요.
- 상관관계나 동시 변화만으로 인과관계를 단정하지 마세요.
- 입력에 없는 사실을 새로 만들지 마세요.
"""

def call_openai(prompt):
    from openai import OpenAI
    
    api_key = os.getenv("LLM_API_KEY")
    model = os.getenv("LLM_MODEL", "gpt-4o") # 설정이 없으면 기본값으로 gpt-4o 사용

    if not api_key:
        raise RuntimeError("OpenAI API Key가 설정되지 않았습니다.")

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def generate_report(summary):
    provider = os.getenv("LLM_PROVIDER", "").lower()
    prompt = build_prompt(summary)

    if provider == "openai":
        text = call_openai(prompt)
    elif provider == "gemini":
        # 혹시 나중에 Gemini를 다시 쓸 경우를 대비해 남겨둘 수 있습니다.
        from google import genai
        api_key = os.getenv("LLM_API_KEY")
        model = os.getenv("LLM_MODEL")
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(model=model, contents=prompt)
        text = response.text
    else:
        raise RuntimeError(
            f"지원하지 않거나 설정되지 않은 LLM_PROVIDER입니다: '{provider}'. "
            "'.env' 파일에서 LLM_PROVIDER를 'openai'로 설정해주세요."
        )

    output_path = REPORTS_DIR / "llm_summary.md"
    output_path.write_text(text, encoding="utf-8")

    return text

# --- 파일 가장 아래에 아래 코드를 추가해보세요 ---
if __name__ == "__main__":
  # 테스트용 요약 데이터
  sample_summary = {
      "analysis_date": "2026-10-15",
      "description": (
          "네이버 검색 트렌드 및 관광공사 체류/소비 데이터 분석 결과"
      ),
  }

  print("🚀 LLM 리포트 생성 시작...")
  result_text = generate_report(sample_summary)
  print("✅ 리포트 생성 완료!")
  print("생성된 내용 미리보기:")
  print(result_text[:200] + "...")