import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 1. 페이지 설정
st.set_page_config(page_title="농산물 품질/가격 모니터링", layout="wide")
st.title("🥬 농산물 가격 예측 및 Cpk 조기 경보 시스템")

# 2. 데이터 로드
@st.cache_data
def load_data():
    file_path = '20260416_data.csv'  # 저장소에 있는 파일명과 정확히 일치해야 함
    try:
        df = pd.read_csv(file_path, encoding='cp949')
    except:
        df = pd.read_csv(file_path, encoding='utf-8')
    return df

df = load_data()

# 3. Cpk 산출 로직
def calculate_cpk(current_price, normal_price):
    usl = normal_price * 1.2
    lsl = normal_price * 0.8
    mean = current_price
    sigma = current_price * 0.05
    if sigma == 0: return 0
    cpu = (usl - mean) / (3 * sigma)
    cpl = (mean - lsl) / (3 * sigma)
    return min(cpu, cpl)

# 4. 사이드바 - 품목 선택
items = df['PDLT_NM'].unique()
selected_item = st.sidebar.selectbox("📈 분석할 품목을 선택하세요", items)
item_df = df[df['PDLT_NM'] == selected_item].iloc[-1]

# 5. 메인 지표 표시
col1, col2, col3 = st.columns(3)
current_prc = item_df['WHSL_DAIL_PRCE']
normal_prc = item_df['WHSL_NMYR_TDP']
cpk_val = calculate_cpk(current_prc, normal_prc)

with col1:
    st.metric("현재 도매가", f"{current_prc:,.0f} 원", f"{item_df['BFRT_RATE']}%")
with col2:
    st.metric("평년가 대비", f"{normal_prc:,.0f} 원", f"{item_df['NMYR_RATE']}%")
with col3:
    status = "✅ 정상" if cpk_val >= 1.33 else "⚠️ 주의" if cpk_val >= 1.0 else "🚨 이상"
    st.metric("품질 지수 (Cpk)", f"{cpk_val:.2f}", status)

# 6. 시각화 (에러가 났던 부분 - 한 줄로 작성)
st.subheader(f"📊 {selected_item} 가격 변동 추이")
fig = px.line(df[df['PDLT_NM'] == selected_item], x='INQ_YMD', y='WHSL_DAIL_PRCE', markers=True)
st.plotly_chart(fig, use_container_width=True)

# 7. 경보 시스템
if cpk_val < 1.0:
    st.error(f"❗ 알림: {selected_item}의 가격 변동성이 공정 범위를 벗어났습니다.")
else:
    st.success(f"✔️ {selected_item}은 안정적인 범위를 유지하고 있습니다.")
