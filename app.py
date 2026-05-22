import streamlit as pd
import streamlit as st
import pandas as pd
import os

# 엑셀 파일 이름
FILE_NAME = "14매수일자별잔고.xls.xlsx"

# 페이지 기본 설정
st.set_page_config(page_title="해외주식 절세 시뮬레이터", page_icon="📈", layout="wide")

st.title("📈 해외주식 선입선출 vs 이동평균 절세 시뮬레이터")
st.markdown("키움증권 매수일자별 잔고 데이터를 기반으로 실시간 절세 효과를 계산합니다.")
st.sidebar.header("⚙️ 데이터 및 설정")

# 데이터 불러오기 함수
@st.cache_data
def load_data():
    if not os.path.exists(FILE_NAME):
        return None
    try:
        df = pd.read_csv(FILE_NAME, skiprows=3) if FILE_NAME.endswith('.csv') else pd.read_excel(FILE_NAME, skiprows=3)
        df['종목명'] = df['종목명'].str.strip()
        df['매수수량'] = pd.to_numeric(df['매수수량'], errors='coerce')
        df['매수가'] = pd.to_numeric(df['매수가'], errors='coerce')
        df['매수금액(원)'] = pd.to_numeric(df['매수금액(원)'], errors='coerce')
        df = df.dropna(subset=['종목명', '매수수량', '매수가'])
        return df
    except:
        return None

df = load_data()

if df is None:
    st.error(f"❌ 폴더 내에 '{FILE_NAME}' 파일이 존재하지 않습니다. 파일을 매칭해 주세요.")
else:
    # 1. 보유 주식 포트폴리오 요약
    st.subheader("📊 최은비 님의 실시간 보유 잔고 현황")
    
    summary_list = []
    for name, group in df.groupby('종목명'):
        total_qty = group['매수수량'].sum()
        total_cost_krw = group['매수금액(원)' ].sum()
        avg_price_krw = total_cost_krw / total_qty if total_qty > 0 else 0
        
        group_sorted = group.sort_values('매수일자')
        oldest_price = group_sorted.iloc[0]['매수가']
        oldest_date = group_sorted.iloc[0]['매수일자']
        
        summary_list.append({
            "종목명": name,
            "보유 수량 (주)": int(total_qty),
            "이동평균단가 (원)": int(avg_price_krw),
            "FIFO 기준 최초 매수단가 ($)": round(oldest_price, 2),
            "FIFO 기준 최초 매수일": oldest_date
        })
    
    df_summary = pd.DataFrame(summary_list)
    # 웹 화면에 이쁜 표로 보여주기
    st.dataframe(df_summary, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # 2. 시뮬레이터 섹션
    st.subheader("🔮 매도 시뮬레이션 및 절세 비교")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        target_stock = st.selectbox("시뮬레이션할 종목을 선택하세요", df['종목명'].unique())
        
    stock_group = df[df['종목명'] == target_stock].sort_values('매수일자')
    total_owned = int(stock_group['매수수량'].sum())
    
    with col2:
        sell_qty = st.number_input(f"매도 수량 입력 (보유: {total_owned}주)", min_value=1, max_value=total_owned, value=min(10, total_owned))
        
    with col3:
        sell_price = st.number_input("예상 매도 단가 입력 ($)", min_value=0.1, value=float(stock_group['매수가'].max()))

    # 계산 로직
    # [이동평균법]
    total_cost_usd = (stock_group['매수가'] * stock_group['매수수량']).sum()
    avg_price_usd = total_cost_usd / total_owned
    ma_cost_basis = avg_price_usd * sell_qty
    ma_gain = (sell_price * sell_qty) - ma_cost_basis
    
    # [선입선출법]
    fifo_cost_basis = 0
    temp_sell_qty = sell_qty
    for _, row in stock_group.iterrows():
        lot_qty = row['매수수량']
        lot_price = row['매수가']
        if temp_sell_qty <= lot_qty:
            fifo_cost_basis += temp_sell_qty * lot_price
            temp_sell_qty = 0
            break
        else:
            fifo_cost_basis += lot_qty * lot_price
            temp_sell_qty -= lot_qty
    fifo_gain = (sell_price * sell_qty) - fifo_cost_basis

    # 결과 대시보드 시각화
    res_col1, res_col2 = st.columns(2)
    
    with res_col1:
        st.metric(label="📊 이동평균법 적용 시 양도차익", value=f"${ma_gain:,.2f}", delta=f"평균원가: ${avg_price_usd:,.2f}", delta_color="off")
        
    with res_col2:
        st.metric(label="📜 선입선출법(FIFO) 적용 시 양도차익", value=f"${fifo_gain:,.2f}", delta="과거 매수 건부터 차감", delta_color="off")
        
    # 절세 진단 결과 알림창
    st.markdown("### 💡 제미나이의 절세 진단 리포트")
    if ma_gain < fifo_gain:
        diff = fifo_gain - ma_gain
        st.success(f"현재 조건에서는 **[이동평균법]**이 유리합니다! 선입선출법보다 양도차익이 **${diff:,.2f}** 만큼 더 적게 잡히므로, 당장 올해 내야 할 세금을 크게 아낄 수 있습니다.")
    elif ma_gain > fifo_gain:
        diff = ma_gain - fifo_gain
        st.info(f"현재 조건에서는 **[선입선출법]**이 유리합니다! 이동평균법보다 양도차익이 **${diff:,.2f}** 만큼 더 적게 잡히므로, 과세 대상 소득을 줄이기에 유리합니다.")
    else:
        st.warning("두 방식의 양도차익이 완전히 일치합니다. 어떤 방식을 선택하셔도 무방합니다.")