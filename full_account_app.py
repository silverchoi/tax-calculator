import streamlit as st
import pandas as pd
import yfinance as yf
import os
import plotly.express as px
import tax_guide  # 새로 만든 세금 가이드 파일을 불러옵니다

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

    # 상단 탭 2개 생성
    tab1, tab2 = st.tabs(["📊 실시간 절세 대시보드", "🔍 세금 연산 로직 가이드"])

    total_dashboard = []
    portfolio_pie_data = []
    ma_total_gain_krw = 0
    fifo_total_gain_krw = 0

    for name, group in df.groupby('종목명'):
        group_sorted = group.sort_values('매수일자')
        ticker_code = group_sorted.iloc[0]['코드']
        total_qty = group_sorted['매수수량'].sum()
        
        # 🚨 에러가 났던 문제의 93번째 줄 파트 (정상 복구 완료)
        sim_qty = total_qty * sell_factor
        total_cost_krw = group_sorted['매수금액(원)'].sum()
        total_cost_usd = (group_sorted['매수가'] * group_sorted['매수수량']).sum()
        
        sim_cost_krw = total_cost_krw * sell_factor
        sim_cost_usd = total_cost_usd * sell_factor
        
        now_price_usd = current_prices.get(ticker_code, 0.0)
        if now_price_usd == 0.0:
            now_price_usd = group_sorted.iloc[-1]['매수가'] 
            
        total_eval_krw = total_qty * now_price_usd * exchange_rate
        portfolio_pie_data.append({"종목명": name, "평가금액": total_eval_krw})
            
        ma_gain_usd = (now_price_usd * sim_qty) - sim_cost_usd
        ma_gain_krw = ma_gain_usd * exchange_rate
        fifo_gain_krw = (now_price_usd * sim_qty * exchange_rate) - sim_cost_krw

        roi = ((now_price_usd * total_qty) - total_cost_usd) / total_cost_usd * 100 if total_cost_usd > 0 else 0
        tax_diff_krw = fifo_gain_krw - ma_gain_krw
        
        if ma_gain_krw < fifo_gain_krw:
            best_method = "이동평균법 유리"
        elif ma_gain_krw > fifo_gain_krw:
            best_method = "선입선출법 유리"
        else:
            best_method = "동일"
        
        total_dashboard.append({
            "종목명": name,
            "현재가($)": now_price_usd,
            "수익률(%)": roi,
            f"이동평균 차익 ({sell_percent}% 매도)": int(ma_gain_krw),
            f"선입선출 차익 ({sell_percent}% 매도)": int(fifo_gain_krw),
            "추천 방식": best_method,
            "절세 가능 금액(원)": int(abs(tax_diff_krw))
        })
        
        ma_total_gain_krw += ma_gain_krw
        fifo_total_gain_krw += fifo_gain_krw

    ma_tax = max(0, ((ma_total_gain_krw + already_gain) - 2500000) * 0.22)
    fifo_tax = max(0, ((fifo_total_gain_krw + already_gain) - 2500000) * 0.22)

    # 1번 탭 구역 내용물
    with tab1:
        st.subheader(f"🏁 [{sell_percent}% 분할 매도 기준] 예상 세금(양도세) 비교")
        sum_col1, sum_col2, sum_col3 = st.columns(3)
        
        with sum_col1:
            st.metric(label="📈 이동평균법 적용 시", value=f"선택 차익: ₩{int(ma_total_gain_krw):,}", delta=f"최종 양도세: ₩{int(ma_tax):,}", delta_color="inverse")
        with sum_col2:
            st.metric(label="📜 선입선출법(FIFO) 적용 시", value=f"선택 차익: ₩{int(fifo_total_gain_krw):,}", delta=f"최종 양도세: ₩{int(fifo_tax):,}", delta_color="inverse")
        with sum_col3:
            tax_saved = abs(fifo_tax - ma_tax)
            final_recommend = "이동평균법" if ma_tax < fifo_tax else ("선입선출법" if ma_tax > fifo_tax else "세금 동일")
            st.metric(label="💡 최종 선택 시 절세 가능한 세금", value=f"₩{int(tax_saved):,}", delta=f"추천: {final_recommend}")

        st.divider()
        st.subheader("📊 내 계좌 자산 비중 (Portfolio Allocation)")
        df_pie = pd.DataFrame(portfolio_pie_data)
        fig = px.pie(df_pie, values='평가금액', names='종목명', hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.subheader(f"🔍 실시간 종목별 상세 분석 ({sell_percent}% 매도 시뮬레이션)")
        df_dashboard = pd.DataFrame(total_dashboard)
        
        def color_roi(val):
            color = '#ef4444' if val > 0 else ('#3b82f6' if val < 0 else '#ffffff')
            return f'color: {color}; font-weight: bold;'

        styled_df = df_dashboard.style\
            .format({
                "현재가($)": "${:,.2f}",
                "수익률(%)": "{:+.2f}%",
                f"이동평균 차익 ({sell_percent}% 매도)": "{:,}원",
                f"선입선출 차익 ({sell_percent}% 매도)": "{:,}원",
                "절세 가능 금액(원)": "{:,}원"
            })\
            .map(color_roi, subset=["수익률(%)"])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

    # 2번 탭 구역 내용물
    with tab2:
        tax_guide.show_guide()