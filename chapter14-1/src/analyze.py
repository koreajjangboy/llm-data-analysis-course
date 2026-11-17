import matplotlib.pyplot as plt
import pandas as pd

# 💡 1. 한글 폰트 설정 (Windows: Malgun Gothic)
plt.rc("font", family="Malgun Gothic")
plt.rc("axes", unicode_minus=False)

df = pd.read_csv("data/processed/naver_trend.csv")

df["period"] = pd.to_datetime(df["period"])

for keyword, group in df.groupby("keyword"):
  group = group.sort_values("period")

  plt.plot(
      group["period"],
      group["ratio"],
      marker="o",
      label=keyword,
  )

plt.title("NAVER 검색 관심도 추이")
plt.xlabel("기간")
plt.ylabel("상대 관심도")
plt.legend()
plt.tight_layout()
plt.savefig("reports/naver_trend.png", dpi=150)
plt.close()

print("[PASS] 네이버 트렌드 그래프 시각화 완료 (한글 적용)")