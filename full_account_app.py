import streamlit as st
import pandas as pd
import yfinance as yf
import os

# 엑셀 파일 이름 지정
FILE_NAME = "14매수일자별잔고.xls.xlsx"

# 웹페이지 기본 설정
st.set_page_config(page_title="해외주식 실시간 통합 절세 대시보드", page_icon="💰", layout="wide")

st.title("💰 해외주식 실시간 통합 절세 대시보드")
st.markdown("현재 시장 시세를 실시간으로 반영하여, 전량 매도 시 **이동평균법**과 **선입선출법(FIFO)**의 세금을 비교합니다.")

# 데이터 불러오기 함수
@st.cache_data
def load_data():
    if not os.path.exists(FILE_NAME):
        return None
    try:
        df = pd.read_csv(FILE_NAME, skiprows=3) if FILE_NAME.endswith('.csv') else pd.read_excel(FILE_NAME, skiprows=3)
        df['종목명'] = df['종목명'].str.strip()
        df['코드'] = df['코드'].str.strip()
        df['매수수량'] = pd.to_numeric(df['매수수량'], errors='coerce')
        df['매수가'] = pd.to_numeric(df['매수가'], errors='coerce')
        df['매수금액'] = pd.to_numeric(df['매수금액'], errors='coerce')
        df['매수금액(원)'] = pd.to_numeric(df['매수금액(원)'], errors='coerce')
        df = df.dropna(subset=['종목명', '매수수량', '매수가', '코드'])
        return df
    except:
        return None

def get_current_prices(tickers):
    prices = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            todays_data = stock.history(period='1d', prepost=True)
            if not todays_data.empty:
                prices[ticker] = todays_data['Close'].iloc[-1]
            else:
                prices[ticker] = stock.info.get('previousClose', 0.0)
        except:
            prices[ticker] = 0.0
    return prices

df = load_data()

if df is None:
    st.error(f"❌ 폴더 내에 '{FILE_NAME}' 파일이 존재하지 않습니다. 파일을 동일한 폴더에 넣어주세요.")
else:
    unique_tickers = df['코드'].unique()
    with st.spinner('🔄 야후 파이낸스에서 실시간 미국 시장 시세를 끌어오는 중입니다...'):
        current_prices = get_current_prices(unique_tickers)
    
    st.sidebar.header("⚙️ 시뮬레이션 설정")
    exchange_rate = st.sidebar.number_input("💵 적용 환율 (원/$)", min_value=1000.0, max_value=2000.0, value=1400.0, step=10.0)

    total_dashboard = []
    ma_total_gain_krw = 0
    fifo_total_gain_krw = 0

    for name, group in df.groupby('종목명'):
        group_sorted = group.sort_values('매수일자')
        ticker_code = group_sorted.iloc[0]['코드']
        total_qty = group_sorted['매수수량'].sum()
        
        total_cost_krw = group_sorted['매수금액(원)'].sum()
        total_cost_usd = (group_sorted['매수가'] * group_sorted['매수수량']).sum()
        
        now_price_usd = current_prices.get(ticker_code, 0.0)
        if now_price_usd == 0.0:
            now_price_usd = group_sorted.iloc[-1]['매수가'] 
            
        ma_gain_usd = (now_price_usd * total_qty) - total_cost_usd
        ma_gain_krw = ma_gain_usd * exchange_rate
        fifo_gain_krw = (now_price_usd * total_qty * exchange_rate) - total_cost_krw

        roi = ((now_price_usd * total_qty) - total_cost_usd) / total_cost_usd * 100 if total_cost_usd > 0 else 0
        tax_diff_krw = fifo_gain_krw - ma_gain_krw
        best_method = "이동평균법 유리" if ma_gain_krw < fifo_gain_krw else ("선입선출법 유리" if ma_gain_krw > fifo_gain_krw else "동일")
        
        total_dashboard.append({
            "종목명": name,
            "현재가($)": now_price_usd,
            "수익률(%)": roi,
            "이동평균 차익(원)": int(ma_gain_krw),
            "선입선출 차익(원)": int(fifo_gain_krw),
            "추천 방식": best_method,
            "절세 가능 금액(원)": int(abs(tax_diff_krw))
        })
        
        ma_total_gain_krw += max(0, ma_gain_krw)
        fifo_total_gain_krw += max(0, fifo_gain_krw)

    ma_tax = max(0, (ma_total_gain_krw - 2500000) * 0.22)
    fifo_tax = max(0, (fifo_total_gain_krw - 2500000) * 0.22)

    st.subheader("🏁 실시간 기준 예상 세금(양도세) 비교 리포트")
    sum_col1, sum_col2, sum_col3 = st.columns(3)
    
    with sum_col1:
        st.metric(label="📈 이동평균법 적용 시", value=f"총 이익: ₩{int(ma_total_gain_krw):,}", delta=f"예상 세금: ₩{int(ma_tax):,}", delta_color="inverse")
    with sum_col2:
        st.metric(label="📜 선입선출법(FIFO) 적용 시", value=f"총 이익: ₩{int(fifo_total_gain_krw):,}", delta=f"예상 세금: ₩{int(fifo_tax):,}", delta_color="inverse")
    with sum_col3:
        tax_saved = abs(fifo_tax - ma_tax)
        final_recommend = "이동평균법" if ma_tax < fifo_tax else "선입선출법"
        st.metric(label="💡 최종 선택 시 절세 가능한 세금", value=f"₩{int(tax_saved):,}", delta=f"추천 방식: {final_recommend}")

    st.divider()

    # 🎨 여기서부터 테이블 스타일 꾸미기 파트!
    st.subheader("🔍 실시간 종목별 상세 수익 및 절세 분석")
    df_dashboard = pd.DataFrame(total_dashboard)
    
    # 스타일 함수 정의 (수익률 양수면 빨강, 음수면 파랑)
    def color_roi(val):
        color = '#ef4444' if val > 0 else ('#3b82f6' if val < 0 else '#ffffff')
        return f'color: {color}; font-weight: bold;'

    # 판다스 스타일 적용 엔진
    styled_df = df_dashboard.style\
        .format({
            "현재가($)": "${:,.2f}",
            "수익률(%)": "{:+.2f}%",
            "이동평균 차익(원)": "{:,}원",
            "선입선출 차익(원)": "{:,}원",
            "절세 가능 금액(원)": "{:,}원"
        })\
        .applymap(color_roi, subset=["수익률(%)"])\
        .highlight_max(subset=["절세 가능 금액(원)"], color="#2e3d30") # 가장 돈 많이 아끼는 행 하이라이트

    # 화면에 이쁘게 뿌려주기
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

    st.markdown("""
    ---
    ### 📜 대한민국 해외주식 세법 상식 가이드
    * **기본 공제:** 1인당 연간 해외주식 양도차익 총합에서 **250만 원**이 공제됩니다.
    * **세율:** 공제 후 남은 순이익의 **22%(양도소득세 20% + 지방소득세 2%)**가 세금으로 부과됩니다.
    """)