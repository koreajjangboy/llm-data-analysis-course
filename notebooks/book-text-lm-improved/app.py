import streamlit as st
import pandas as pd
from kiwipiepy import Kiwi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics.pairwise import cosine_similarity

# 페이지 기본 설정
st.set_page_config(
    page_title="도서 분야 예측 및 추천 시스템",
    page_icon="📚",
    layout="wide"
)

# 1. Kiwi 객체 안전 로드
@st.cache_resource
def get_kiwi():
    return Kiwi()

kiwi = get_kiwi()
ALLOWED_TAGS = {"NNG", "NNP", "SL"}
STOPWORDS = {"에디션"}

def preprocess_text(text):
    if not isinstance(text, str):
        return ""
    tokens = kiwi.tokenize(text)
    cleaned = [
        t.form for t in tokens 
        if t.tag in ALLOWED_TAGS 
        and t.form not in STOPWORDS 
        and not t.form.isdigit() 
        and len(t.form) >= 2
    ]
    return " ".join(cleaned)

# 2. 데이터 및 모델 학습 로드
@st.cache_data
def load_data_and_model():
    df = pd.read_csv("books_improved.csv", encoding="utf-8-sig")
    df["상품명_정제"] = df["상품명"].apply(preprocess_text)
    
    vectorizer = TfidfVectorizer()
    X_train_vec = vectorizer.fit_transform(df["상품명_정제"])
    
    model = MultinomialNB()
    model.fit(X_train_vec, df["분야"])
    
    return df, vectorizer, model

# 데이터 로드
try:
    df, vectorizer, model = load_data_and_model()
except Exception as e:
    st.error(f"데이터를 로드하는 중 오류가 발생했습니다: {e}")
    st.stop()

# ---------------------------------------------------------
# 사이드바 메뉴 및 메인 로직
# ---------------------------------------------------------
st.sidebar.title("📚 도서 AI 서비스")
menu = st.sidebar.radio("메뉴 선택", ["1. 도서 분야 예측", "2. 비슷한 도서 추천"])

if menu == "1. 도서 분야 예측":
    st.header("🎯 도서 제목 기반 분야 예측")
    input_title = st.text_input("도서 제목을 입력하세요:", placeholder="예: 처음 배우는 파이썬 데이터 분석")
    
    if st.button("분야 예측하기", type="primary"):
        if input_title.strip() == "":
            st.warning("도서 제목을 입력해 주세요.")
        else:
            cleaned_title = preprocess_text(input_title)
            title_vec = vectorizer.transform([cleaned_title])
            predicted_category = model.predict(title_vec)[0]
            
            st.success(f"예측된 도서 분야: **[{predicted_category}]**")
            with st.expander("🔍 상세 정보"):
                st.write(f"- 원문: {input_title}")
                st.write(f"- 정제 텍스트: `{cleaned_title}`")

elif menu == "2. 비슷한 도서 추천":
    st.header("📖 연관 도서 추천")
    selected_title = st.selectbox("기준 도서 선택:", df["상품명"].unique())
    
    if st.button("추천 도서 찾기", type="primary"):
        selected_idx = df[df["상품명"] == selected_title].index[0]
        selected_category = df.loc[selected_idx, "분야"]
        selected_clean_text = df.loc[selected_idx, "상품명_정제"]
        
        st.info(f"선택한 도서 분야: **[{selected_category}]**")
        
        candidate_df = df[(df["분야"] == selected_category) & (df.index != selected_idx)].copy().reset_index(drop=True)
        
        if candidate_df.empty:
            st.warning("⚠️ 추천할 후보 도서가 없습니다.")
        else:
            rec_vectorizer = TfidfVectorizer()
            all_texts = [selected_clean_text] + candidate_df["상품명_정제"].tolist()
            tfidf_matrix = rec_vectorizer.fit_transform(all_texts)
            
            sim_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
            candidate_df["similarity"] = sim_scores
            
            filtered_df = candidate_df[candidate_df["similarity"] > 0].sort_values(by="similarity", ascending=False)
            
            if filtered_df.empty:
                st.warning("⚠️ 현재 기준으로 유사도가 있는 추천 도서를 찾지 못했습니다.")
            else:
                top_results = filtered_df.head(5)
                st.subheader(f"🎯 추천 도서 Top {len(top_results)}")
                for idx, row in top_results.reset_index().iterrows():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{idx + 1}. [{row['분야']}] {row['상품명']}**")
                    with col2:
                        st.metric(label="유사도", value=f"{row['similarity']:.4f}")
                    st.divider()