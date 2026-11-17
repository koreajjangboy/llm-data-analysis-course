import json
import os
from datetime import datetime
from pathlib import Path
import requests
from dotenv import load_dotenv
import urllib.parse

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
CONFIG_PATH = BASE_DIR / "config" / "tourism_params.json"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# .env 파일 명시적 로드
load_dotenv(BASE_DIR / ".env")

service_key = os.getenv("TOURISM_SERVICE_KEY")
stay_url = os.getenv("TOURISM_STAY_URL")
consumption_url = os.getenv("TOURISM_CONSUMPTION_URL")

print("--- [디버그 정보] ---")
print(f"로드된 서비스키 존재 여부: {bool(service_key)}")
print(f"체류 URL: {stay_url}")
print("--------------------")

if not service_key:
    raise RuntimeError("TOURISM_SERVICE_KEY가 .env 파일에 없습니다.")
if not stay_url or not consumption_url:
    raise RuntimeError("관광 API URL이 설정되지 않았습니다.")

with CONFIG_PATH.open("r", encoding="utf-8") as f:
    config = json.load(f)
    
def call_api(name, url, params):
    params = params.copy()
    
    # 💡 인증키를 명시적으로 unquote 한 뒤 params에 확실히 강제 주입
    decoded_key = urllib.parse.unquote(service_key)
    params["serviceKey"] = decoded_key
    
    print(f"[{name}] 전송될 최종 파라미터 키 개수: {len(params)}")

    response = requests.get(url, params=params, timeout=30)
    print(f"[{name}] 최종 요청 URL: {response.url}")

    if response.status_code != 200:
        raise RuntimeError(
            f"{name} API 실패: HTTP {response.status_code} {response.text[:300]}"
        )
    return response.json()

stay_data = call_api(
    "stay",
    stay_url,
    config["stay"]["params"],
)

consumption_data = call_api(
    "consumption",
    consumption_url,
    config["consumption"]["params"],
)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
stay_path = RAW_DIR / f"tourism_stay_{timestamp}.json"
consumption_path = RAW_DIR / f"tourism_consumption_{timestamp}.json"

with stay_path.open("w", encoding="utf-8") as f:
    json.dump(stay_data, f, ensure_ascii=False, indent=2)

with consumption_path.open("w", encoding="utf-8") as f:
    json.dump(consumption_data, f, ensure_ascii=False, indent=2)

print("[PASS] Tourism API")
print("stay saved:", stay_path)
print("consumption saved:", consumption_path)