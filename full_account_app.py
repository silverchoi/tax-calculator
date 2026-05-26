import streamlit as st
import pandas as pd
import yfinance as yf
import os
import plotly.express as px
import tax_guide

# 엑셀 파일 이름 지정
FILE_NAME = "14매수일자별잔고.xls.xlsx"

# ✨ [UI 개선 1] layout을 "centered"로 변경하여 넙데데함을 잡고 정갈하게 중앙 집중화합니다.
st.set_page_config(page_title="해외주식 실시간 통합 절세 대시보드 Pro", page_icon="💰", layout="centered")

# 카카오톡이나 핀테크 앱 느낌의 깔끔한 폰트 및 스타일 부여
st.markdown("""
    <style>
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        h1 { font-weight: 800; font-size: 1.8rem !important; color: #1e293b; }
        h3 { font-weight: 700; font-size: 1.2rem !important; color: #334155; }
        .stMetric { background-color: #f8fafc; padding: 15px; border-radius: 12px; border: 1px solid #e2e8f0; }
        div[data-testid="metric-container"] label { font-size: 0.85rem !important; font-weight: 600; color: #64748b; }
        div[data-testid="metric-container"] [data-testid="stMetricValue"] { font-size: 1.4rem !important; font-weight: 700; color: #0f172a; }
    </style>
""", unsafe_allow_html=True)

st.title("💰 해외주식 절세 대시보드 Pro")
st.markdown("<small style='color:#64748b;'>실시간 시세·환율 반영 및 분할 매도 시뮬레이터</small>", unsafe_allow_html=True)

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

# 프리마켓 대응 실시간 주가 추출 엔진
def get_current_prices(tickers):
    prices = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            todays_data = stock.history(period='1d', prepost=True)
            fast_info_price = stock.fast_info.get('last_price', None)
            if fast_info_price is not None and fast_info_price > 0:
                prices[ticker] = fast_info_price
            elif not todays_data.empty:
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
    with st.spinner('🔄 실시간 마켓 데이터 동기화 중...'):
        current_prices = get_current_prices(unique_tickers)
        auto_exchange_rate = get_realtime_exchange_rate()
    
    # ✨ [UI 개선 2] 사이드바 설정창 가시성 확보 및 정돈
    st.sidebar.header("⚙️ 시뮬레이션 설정")
    st.sidebar.markdown("<small style='color:#94a3b8;'>왼쪽 위의 화살표( > ) 버튼으로 창을 접거나 열 수 있습니다.</small>", unsafe_allow_html=True)
    
    exchange_rate = st.sidebar.number_input(
        f"💵 적용 환율 (원/$)", 
        min_value=1000.0, max_value=2000.0, value=auto_exchange_rate, step=1.0
    )
    sell_percent = st.sidebar.slider("✂️ 매도 비율 선택 (%)", min_value=1, max_value=100, value=100, step=5)
    sell_factor = sell_percent / 100.0
    already_gain = st.sidebar.number_input("🎯 올해 이미 실현한 타 종목 손익 (원)", value=0, step=100000)

    # 상단 탭 스위처 생성
    tab1, tab2 = st.tabs(["📊 절세 대시보드", "🔍 확장 시뮬레이터"])

    total_dashboard = []
    portfolio_pie_data = []
    ma_total_gain_krw = 0
    fifo_total_gain_krw = 0

    for name, group in df.groupby('종목명'):
        group_sorted = group.sort_values('매수일자')
        ticker_code = group_sorted.iloc[0]['코드']
        total_qty = group_sorted['매수수량'].sum()
        
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
            f"이동평균 차익 ({sell_percent}%)": int(ma_gain_krw),
            f"선입선출 차익 ({sell_percent}%)": int(fifo_gain_krw),
            "추천 방식": best_method,
            "절세 금액": int(abs(tax_diff_krw))
        })
        
        ma_total_gain_krw += ma_gain_krw
        fifo_total_gain_krw += fifo_gain_krw

    ma_tax = max(0, ((ma_total_gain_krw + already_gain) - 2500000) * 0.22)
    fifo_tax = max(0, ((fifo_total_gain_krw + already_gain) - 2500000) * 0.22)

    with tab1:
        st.subheader(f"🏁 [{sell_percent}% 매도 기준] 예상 세금 비교")
        
        # ✨ [UI 개선 3] 모바일에서 3칸 쪼개지면 글씨가 깨지므로 columns 구조를 세로 레이아웃 형태로 변환 감싸기 유도
        st.metric(
            label="📈 이동평균법 (국내 증권사 기본 기준)", 
            value=f"₩{int(ma_total_gain_krw):,}", 
            delta=f"예상 세금: ₩{int(ma_tax):,}",
            delta_color="inverse"
        )
        st.write("")
        st.metric(
            label="📜 선입선출법 (FIFO 국세청 신고 기준)", 
            value=f"₩{int(fifo_total_gain_krw):,}", 
            delta=f"예상 세금: ₩{int(fifo_tax):,}",
            delta_color="inverse"
        )
        st.write("")
        
        tax_saved = abs(fifo_tax - ma_tax)
        final_recommend = "이동평균법" if ma_tax < fifo_tax else ("선입선출법" if ma_tax > fifo_tax else "세금 동일")
        st.metric(
            label="💡 최종 선택 시 절세 가능한 세금", 
            value=f"₩{int(tax_saved):,}", 
            delta=f"추천 방식: {final_recommend} 선택",
            delta_color="normal"
        )

        st.divider()
        st.subheader("📊 내 계좌 자산 비중")
        df_pie = pd.DataFrame(portfolio_pie_data)
        fig = px.pie(df_pie, values='평가금액', names='종목명', hole=0.5, color_discrete_sequence=px.colors.sequential.Plotly3)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.subheader("🔍 실시간 종목별 상세 분석")
        df_dashboard = pd.DataFrame(total_dashboard)
        
        def color_roi(val):
            color = '#ef4444' if val > 0 else ('#3b82f6' if val < 0 else '#64748b')
            return f'color: {color}; font-weight: bold;'

        styled_df = df_dashboard.style\
            .format({
                "현재가($)": "${:,.2f}",
                "수익률(%)": "{:+.2f}%",
                f"이동평균 차익 ({sell_percent}%)": "{:,}원",
                f"선입선출 차익 ({sell_percent}%)": "{:,}원",
                "절세 금액": "{:,}원"
            })\
            .map(color_roi, subset=["수익률(%)"])
        
        # 모바일 가독성을 위해 넓은 테이블 뷰 지원
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

    with tab2:
        # 분리된 파일 호출
        tax_guide.show_guide(df, exchange_rate, current_prices)