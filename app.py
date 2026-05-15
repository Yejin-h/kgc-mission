import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="농산물 품질 및 가격 모니터링", layout="wide")
st.title("🥬 농산물 가격 예측 및 Cpk 조기 경보 시스템")

# 2. 데이터 로드 (파일 이름을 정확히 맞춰야 합니다)
@st.cache_data
def load_data():
    try:
        # GitHub에 올린 데이터 파일명과 일치해야 함
        df = pd.read_csv('20260416_data.csv', encoding='cp949')
    except:
        df = pd.read_csv('20260416_data.csv', encoding='utf-8')
    return df

df = load_data()

# 3. Cpk 산출 로직 (품질 관리팀 업무 지식 반영)
def calculate_cpk(current_price, normal_price):
    # 평년가 대비 변동성을 공정 능력으로 간주 (USL/LSL 임의 설정)
    usl = normal_price * 1.2
    lsl = normal_price * 0.8
    mean = current_price
    sigma = current_price * 0.05 # 변동계수 5% 가정
    
    cpu = (usl - mean) / (3 * sigma) if sigma != 0 else 0
    cpl = (mean - lsl) / (3 * sigma) if sigma != 0 else 0
    return min(cpu, cpl)

# 4. 사이드바 - 품목 선택
items = df['PDLT_NM'].unique()
selected_item = st.sidebar.selectbox("📈 분석할 품목을 선택하세요", items)

# 선택된 품목 데이터 필터링
item_df = df[df['PDLT_NM'] == selected_item].iloc[-1] # 가장 최근 데이터

# 5. 메인 대시보드 구성
col1, col2, col3 = st.columns(3)

# 가격 정보 표시
current_prc = item_df['WHSL_DAIL_PRCE']
normal_prc = item_df['WHSL_NMYR_TDP']
cpk_val = calculate_cpk(current_prc, normal_prc)

with col1:
    st.metric("현재 도매가", f"{current_prc:,.0f} 원", f"{item_df['BFRT_RATE']}%")

with col2:
    st.metric("평년가 대비", f"{normal_prc:,.0f} 원", f"{item_df['NMYR_RATE']}%")

with col3:
    # Cpk 값에 따른 상태 표시
    status = "✅ 정상" if cpk_val >= 1.33 else "⚠️ 주의" if cpk_val >= 1.0 else "🚨 이상 발생"
    st.metric("품질 지수 (Cpk)", f"{cpk_val:.2f}", status)

# 6. 시각화 차트
st.subheader(f"📊 {selected_item} 가격
