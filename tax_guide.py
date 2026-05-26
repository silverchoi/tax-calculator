import streamlit as st
import pandas as pd
import yfinance as yf

def show_guide(df, exchange_rate, current_prices):
    st.header("🖲️ 해외주식 절세 마스터 확장 패키지")
    st.markdown("기존 대시보드 로직 위에 실전 매매 전략 수립을 위한 초강력 시뮬레이션 엔진을 구동합니다.")

    if df is None or df.empty:
        st.warning("⚠️ 불러온 엑셀 데이터가 없어 시뮬레이션을 진행할 수 없습니다.")
        return

    unique_titles = df['종목명'].unique()
    
    # ------------------------------------------------------------------
    # ✨ 디테일 3: [세금 0원] 기본 공제 250만 원 맞춤형 안전 익절 가이드
    # ------------------------------------------------------------------
    st.markdown("---")
    st.subheader("🎯 세금 Zero! 연간 기본 공제(250만 원) 맞춤형 익절 가이드")
    st.markdown("올해 실현한 손익이 전혀 없다고 가정할 때, 세금을 단 1원도 내지 않고 **오늘 밤 최대치로 익절할 수 있는 종목별 안전 수량**입니다.")
    
    zero_tax_rows = []
    for name, group in df.groupby('종목명'):
        group_sorted = group.sort_values('매수일자')
        ticker_code = group_sorted.iloc[0]['코드']
        total_owned_qty = group_sorted['매수수량'].sum()
        live_price = current_prices.get(ticker_code, 0.0)
        
        total_cost_usd = (group_sorted['매수가'] * group_sorted['매수수량']).sum()
        avg_cost_usd = total_cost_usd / total_owned_qty if total_owned_qty > 0 else 0
        per_share_gain_krw = (live_price - avg_cost_usd) * exchange_rate
        
        if per_share_gain_krw > 0:
            safe_qty = 2500000 / per_share_gain_krw
            safe_qty = min(safe_qty, float(total_owned_qty))
            safe_eval_krw = safe_qty * live_price * exchange_rate
            zero_tax_rows.append({
                "종목명": name,
                "현재 주가 ($)": f"${live_price:,.2f}",
                "평균 단가 ($)": f"${avg_cost_usd:,.2f}",
                "안전 매도 가능 수량": f"{safe_qty:,.2f} 주",
                "예상 익절 금액 (원)": f"₩{int(safe_eval_krw):,}"
            })
            
    if zero_tax_rows:
        st.table(pd.DataFrame(zero_tax_rows))
        st.caption("💡 위 종목 중 **딱 하나의 종목만** 골라서 해당 수량만큼 팔면 양도세가 0원에 수렴합니다. (여러 개를 동시에 팔면 합산되어 세금이 나옵니다!)")
    else:
        st.info("💡 현재 포트폴리오에 수익 구간인 종목이 없어 안전 익절 가이드라인이 비어 있습니다.")

    # ------------------------------------------------------------------
    # ✨ 디테일 2 & 개별 매도: 내 맘대로 정밀 매도 시뮬레이터
    # ------------------------------------------------------------------
    st.markdown("---")
    st.subheader("✂️ 내 맘대로 매도 시뮬레이터 (종목별 정밀 타격)")
    st.markdown("전체 일괄 매도가 아니라, 내가 원하는 특정 종목만 원하는 단가와 수량으로 팔았을 때의 정밀 영수증을 끊어봅니다.")
    
    selected_stock = st.selectbox("👉 시뮬레이션할 종목 선택", unique_titles, key="stock_selector_guide")
    stock_df = df[df['종목명'] == selected_stock].sort_values('매수일자')
    ticker_code = stock_df.iloc[0]['코드']
    total_owned_qty = stock_df['매수수량'].sum()
    live_price = current_prices.get(ticker_code, 0.0)
    
    col_sim1, col_sim2 = st.columns(2)
    with col_sim1:
        sell_qty_input = st.number_input(f"매도할 수량 (보유: {total_owned_qty:,.2f}주)", min_value=0.0, max_value=float(total_owned_qty), value=float(total_owned_qty), step=1.0)
    with col_sim2:
        sell_price_input = st.number_input("예상 매도 가격 ($)", min_value=0.0, value=float(live_price), step=0.1)

    total_cost_usd = (stock_df['매수가'] * stock_df['매수수량']).sum()
    avg_cost_usd = total_cost_usd / total_owned_qty if total_owned_qty > 0 else 0
    ma_gain_krw = (sell_price_input - avg_cost_usd) * sell_qty_input * exchange_rate
    
    fifo_gain_krw = 0
    rem_qty = sell_qty_input
    for _, row in stock_df.iterrows():
        if rem_qty <= 0:
            break
        row_qty = row['매수수량']
        take_qty = min(rem_qty, row_qty)
        row_cost_krw = row['매수금액(원)'] / row_qty if row_qty > 0 else 0
        row_sell_krw = sell_price_input * exchange_rate
        fifo_gain_krw += (row_sell_krw - row_cost_krw) * take_qty
        rem_qty -= take_qty

    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.metric(label="📈 이동평균법 적용 시 차익", value=f"₩{int(ma_gain_krw):,}")
    with res_col2:
        st.metric(label="📜 선입선출법(FIFO) 적용 시 차익", value=f"₩{int(fifo_gain_krw):,}")

    # ------------------------------------------------------------------
    # ✨ 디테일 4: 환율 변동 스트레스 테스트 시뮬레이터 (오타 완전 수정! 🛠️)
    # ------------------------------------------------------------------
    st.markdown("---")
    st.subheader("💵 환율 급변동 스트레스 테스트 (Stress Test)")
    st.markdown("환율이 폭등하거나 급락할 때, 내 계좌 전체의 원화 차익이 어떻게 춤추는지 가상 시나리오를 돌려봅니다.")
    
    stress_rate = st.slider("⚡ 가상 시나리오 환율 설정 (원/$)", min_value=1200.0, max_value=1600.0, value=float(exchange_rate), step=5.0)
    
    st.write(f"💡 환율이 **₩{stress_rate}**원으로 변할 경우:")
    stress_ma_total = 0
    stress_fifo_total = 0
    
    for name, group in df.groupby('종목명'):
        g_sorted = group.sort_values('매수일자') # 👈 원래대로 '매수일자'로 오타 완벽 복구!
        t_code = g_sorted.iloc[0]['코드']
        t_qty = g_sorted['매수수량'].sum()
        c_price = current_prices.get(t_code, 0.0)
        
        t_cost_usd = (g_sorted['매수가'] * g_sorted['매수수량']).sum()
        t_cost_krw = g_sorted['매수금액(원)'].sum()
        
        stress_ma_total += ((c_price * t_qty) - t_cost_usd) * stress_rate
        stress_fifo_total += (c_price * t_qty * stress_rate) - t_cost_krw
        
    st.info(f"계좌 총 차익 변화량 ➔  이동평균법 기준: **₩{int(stress_ma_total):,}** |  선입선출법 기준: **₩{int(stress_fifo_total):,}**")

    # ------------------------------------------------------------------
    # 국세청 제출용 CSV 다운로드 기능
    # ------------------------------------------------------------------
    st.markdown("---")
    st.subheader("📄 국세청 제출용 양도소득세 신고 자료 추출")
    
    report_rows = []
    for name, group in df.groupby('종목명'):
        group_sorted = group.sort_values('매수일자')
        ticker_code = group_sorted.iloc[0]['코드']
        live_price = current_prices.get(ticker_code, 0.0)
        for _, row in group_sorted.iterrows():
            qty = row['매수수량']
            cost_krw = row['매수금액(원)']
            sell_krw = qty * live_price * exchange_rate
            gain_krw = sell_krw - cost_krw
            report_rows.append({
                "종목명": name, "주식코드": ticker_code, "수량": qty,
                "매수일자": row['매수일자'], "원화취득가액": int(cost_krw),
                "원화양도가액(예정)": int(sell_krw), "양도차익(원)": int(gain_krw)
            })
    
    report_df = pd.DataFrame(report_rows)
    csv_data = report_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(label="📥 국세청 신고용 시뮬레이션 데이터 다운로드 (CSV)", data=csv_data, file_name="국세청_해외주식_신고보조자료.csv", mime="text/csv")