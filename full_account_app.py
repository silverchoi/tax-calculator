import streamlit as st
import pandas as pd
import yfinance as yf
import os
import plotly.express as px
import tax_guide  # 👈 새로 만든 세금 가이드 파일을 여기서 알아서 불러옵니다!

# 엑셀 파일 이름 지정
FILE_NAME = "14매수일자별잔고.xls.xlsx"

# 웹페이지 기본 설정
st.set_page_config(page_title="해외주식 실시간 통합 절세 대시보드 Pro", page_icon="💰", layout="wide")

st.title("💰 해외주식 실시간 통합 절세 대시보드 Pro")
st.markdown("실시간 시세와 환율을 반영하여, **분할 매도 비율** 및 **올해 기실현 손익**에 따른 이동평균법 vs 선입선출법(FIFO) 세금을 비교합니다.")

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

# 실시간 주가 추출 함수
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

# 실시간 원/달러 환율 가져오기 함수
@st.cache_data(ttl=3600)
def get_realtime_exchange_rate():
    try:
        usd_krw = yf.Ticker("KRW=X")
        rate = usd_krw.history(period="1d")['Close'].iloc[-1]
        return round(rate, 2)
    except:
        return 1400.0

df = load_data()

if df is None:
    st.error(f"❌ 폴더 내에 '{FILE_NAME}' 파일이 존재하지 않습니다. 파일을 동일한 폴더에 넣어주세요.")
else:
    unique_tickers = df['코드'].unique()
    with st.spinner('🔄 야후 파이낸스에서 실시간 마켓 시세 및 환율을 동기화하는 중...'):
        current_prices = get_current_prices(unique_tickers)
        auto_exchange_rate = get_realtime_exchange_rate()
    
    st.sidebar.header("⚙️ 시뮬레이션 설정")
    exchange_rate = st.sidebar.number_input(
        f"💵 적용 환율 (원/$) [현재 실시간: ₩{auto_exchange_rate}]", 
        min_value=1000.0, max_value=2000.0, value=auto_exchange_rate, step=1.0
    )
    
    sell_percent = st.sidebar.slider("✂️ 매도 비율 선택 (%)", min_value=1, max_value=100, value=100, step=5)
    sell_factor = sell_percent / 100.0
    already_gain = st.sidebar.number_input("🎯 올해 이미 실현한 타 종목 수익/손실 (원)", value=0, step=100000)

    # ✨ [조립 완료 1] 여기서 화면에 상단 탭 2개를 만들어 줍니다.
    tab1, tab2 = st.tabs(["📊 실시간 절세 대시보드", "🔍 세금 연산 로직 가이드"])

    total_dashboard = []
    portfolio_pie_data = []
    ma_total_gain_krw = 0
    fifo_total_gain_krw = 0

    for name, group in df.groupby('종목명'):
        group_sorted = group.sort_values('매수일자')
        ticker_code = group_sorted.iloc[0]['코드']
        total_qty = group_sorted['매수수량'].sum()
        
        sim_qty = total