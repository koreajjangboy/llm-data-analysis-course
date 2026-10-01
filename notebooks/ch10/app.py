import streamlit as st
import pandas as pd
import numpy as np
import joblib

# ==============================================================================
# 1. 페이지 기본 설정 & 모델 로드
# ==============================================================================
st.set_page_config(
    page_title="주문 취소 위험 예측 대시보드",
    page_icon="📦",
    layout="wide"
)

@st.cache_resource
def load_model():
    """저장된 파이프라인 모델 및 임계값을 로드합니다."""
    try:
        artifacts = joblib.load('cancellation_model.pkl')
        return artifacts['pipeline'], artifacts['threshold']
    except Exception as e:
        st.error(f"모델 파일을 불러오는데 실패했습니다: {e}")
        return None, 0.10

pipeline, threshold = load_model()

# ==============================================================================
# 2. 대시보드 헤더 영역
# ==============================================================================
st.title("📦 주문 취소 위험 사전 탐지 대시보드")
st.markdown("""
이 시스템은 실시간으로 입력된 신규 주문 데이터를 분석하여 **주문 취소 가능성(Probability)**을 계산하고, 
사전에 이탈 방지 조치가 필요한 주문인지 판별합니다.
""")
st.divider()

if pipeline is None:
    st.stop()

# ==============================================================================
# 3. 사이드바 - 운영 파라미터 및 정보
# ==============================================================================
with st.sidebar:
    st.header("⚙️ 모델 운영 설정")
    st.info(f"**현재 설정된 임계값(Threshold)**: `{threshold:.2f}`")
    st.caption("Validation 최적화를 통해 고정된 탐지 민감도 기준선입니다.")
    
    st.divider()
    st.markdown("### 📊 모델 성능 요약")
    st.markdown("- **알고리즘**: Logistic Regression")
    st.markdown("- **주요 목표**: Recall(탐지율) 극대화")
    st.markdown("- **Final Test Recall**: `76.92%`")

# ==============================================================================
# 4. 메인 입력 폼 (주문 정보 입력)
# ==============================================================================
st.subheader("📝 신규 주문 정보 입력")

col1, col2, col3 = st.columns(3)

with col1:
    total_quantity = st.number_input("총 구매 수량 (total_quantity)", min_value=1, max_value=100, value=2)
    total_price = st.number_input("총 결제 금액 (total_price, 원)", min_value=1000, max_value=5000000, value=45000, step=1000)

with col2:
    item_count = st.number_input("구매 품목 종류 수 (item_count)", min_value=1, max_value=20, value=1)
    age = st.number_input("고객 연령 (age)", min_value=10, max_value=100, value=30)

with col3:
    gender = st.selectbox("성별 (gender)", options=['M', 'F'])
    city = st.selectbox("배송 지역 도시 (city)", options=['Seoul', 'Busan', 'Incheon', 'Daegu', 'Daejeon', 'Gwangju'])

# ==============================================================================
# 5. 예측 수행 및 결과 시각화
# ==============================================================================
st.divider()

if st.button("🔮 주문 취소 위험도 예측 실행", type="primary", use_container_width=True):
    # 입력된 데이터로 Raw DataFrame 구성 (학습시 사용된 컬럼명과 정확히 일치해야 함)
    input_df = pd.DataFrame([{
        'total_quantity': total_quantity,
        'total_price': total_price,
        'item_count': item_count,
        'age': age,
        'gender': gender,
        'city': city
    }])
    
    # 확률 추론 및 위험 여부 판단
    cancel_prob = pipeline.predict_proba(input_df)[0, 1]
    is_risk = cancel_prob >= threshold

    # 결과 표출 영역
    st.subheader("🎯 예측 분석 결과")
    
    res_col1, res_col2 = st.columns([1, 2])
    
    with res_col1:
        st.metric(
            label="예측된 취소 확률 (Cancel Probability)", 
            value=f"{cancel_prob * 100:.2f}%",
            delta=f"기준 임계값 {threshold * 100:.1f}% 대비",
            delta_color="inverse" if is_risk else "normal"
        )
        
    with res_col2:
        if is_risk:
            st.error("🚨 **[위험 상태] 주문 취소 가능성이 높은 주문입니다!**")
            st.warning("""
            **권장 액션 플랜:**
            - 이탈 방지용 감사 할인 쿠폰/알림톡 즉시 발송
            - 물류팀에 우선 출고/배송 배치 요청
            - CS팀 사전 모니터링 리스트에 추가
            """)
        else:
            st.success("✅ **[정상 상태] 주문이 안정적으로 완료될 것으로 예상됩니다.**")
            st.info("별도의 이탈 방지 조치가 필요하지 않은 일반 주문입니다.")

    # 입력 데이터 요약 표시
    with st.expander("🔍 입력된 Raw 데이터 확인"):
        st.dataframe(input_df)