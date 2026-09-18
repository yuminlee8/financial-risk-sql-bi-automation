import streamlit as st
import pandas as pd

st.set_page_config(page_title="여신 리스크 조회", layout="centered")

df = pd.read_csv('segment_lookup.csv')

st.title("💵 여신 리스크 조회")
st.caption("Lending Club 2007-2018 실적 기반. 과거 유사 세그먼트의 부실률을 조회합니다.")

col1, col2 = st.columns(2)
with col1:
    grade = st.selectbox("신용등급", sorted(df['grade'].unique()))
with col2:
    purpose = st.selectbox("대출 목적", sorted(df['purpose'].unique()))

row = df[(df['grade'] == grade) & (df['purpose'] == purpose)]

if row.empty:
    st.warning("해당 조합은 표본이 100건 미만이라 조회할 수 없습니다.")
else:
    r = row.iloc[0]
    
    c1, c2, c3 = st.columns(3)
    c1.metric("부실률", f"{r['bad_rate']:.2f}%")
    c2.metric("등급 평균 대비", f"{r['ratio']:.2f}배")
    c3.metric("표본 수", f"{int(r['total_cnt']):,}건")

    if r['ratio'] >= 1.5:
        st.error(f"주의 — {grade}등급 평균({r['grade_avg_rate']:.2f}%)의 {r['ratio']:.2f}배 수준입니다.")
    elif r['ratio'] >= 1.2:
        st.warning(f"관찰 — {grade}등급 평균({r['grade_avg_rate']:.2f}%)을 다소 상회합니다.")
    else:
        st.success(f"정상 — {grade}등급 평균({r['grade_avg_rate']:.2f}%) 범위 내입니다.")

    if r['total_cnt'] < 300:
        st.info(f"표본이 {int(r['total_cnt']):,}건으로 적어 해석에 주의가 필요합니다.")

    st.divider()
    st.write(f"평균 DTI **{r['avg_dti']:.1f}%** · 평균 대출금액 **${r['avg_amnt']:,.0f}**")