import streamlit as st
import pandas as pd
import datetime
import plotly.express as px

def show_guide(df, exchange_rate, current_prices):
    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["일정 & 뉴스룸", "정밀 시뮬레이터", "계산법 원리 마스터"])

    # ------------------------------------------------------------------
    # [서브탭 1] 실시간 일정 & 뉴스룸
    # ------------------------------------------------------------------
    with sub_tab1:
        st.markdown("### 내 종목 핵심 마켓 캘린더")
        
        today = datetime.date(2026, 5, 27)
        all_events = [
            {"date": datetime.date(2026, 5, 19), "ticker": "NVDA", "title": "FY2027 Q1 실적 발표 완료"},
            {"date": datetime.date(2026, 6, 2), "ticker": "AMD", "title": "BofA 글로벌 테크 콘퍼런스 (CFO 발표 예정)"},
            {"date": datetime.date(2026, 6, 22), "ticker": "SOXL", "title": "분기 배당금 선언일 예정"},
            {"date": datetime.date(2026, 6, 23), "ticker": "SOXL", "title": "배당락일 (Ex-Dividend Date)"},
            {"date": datetime.date(2026, 7, 23), "ticker": "SK Hynix", "title": "FY2026 Q2 실적 발표 (예정)"},
        ]
        
        two_weeks_later = today + datetime.timedelta(days=14)
        upcoming_events = [e for e in all_events if today <= e["date"] <= two_weeks_later]
        past_and_future = [e for e in all_events if e["date"] >= today]

        col_ev1, col_ev2 = st.columns(2)
        with col_ev1:
            st.markdown("**2주 내 임박한 중요 일정**")
            if upcoming_events:
                for ev in upcoming_events:
                    st.info(f"**[{ev['date'].strftime('%m/%d')}] {ev['ticker']}**\n\n{ev['title']}")
            else:
                st.write("<small style='color:#64748b;'>2주간 예정된 주요 이벤트가 없습니다.</small>", unsafe_allow_html=True)
                
        with col_ev2:
            st.markdown("**전체 타임라인**")
            event_rows = []
            for ev in past_and_future:
                event_rows.append({"날짜": ev["date"].strftime("%Y-%m-%d"), "종목": ev["ticker"], "이벤트 내용": ev["title"]})
            if event_rows:
                st.dataframe(pd.DataFrame(event_rows), use_container_width=True, hide_index=True)

        st.divider()
        st.markdown("### AI 기반 포트폴리오 실시간 뉴스룸")
        
        news_feeds = [
            {"status": "positive", "title": "엔비디아, 차세대 인공지능 칩 '블랙웰' 출하 가속화... 공급 부족 연말 해소 전망", "ticker": "NVDA", "related": ["SOXL", "SK Hynix"]},
            {"status": "positive", "title": "AMD, 새로운 라이젠 AI 프로세서 벤치마크 유출... 인텔 대비 성능 우위", "ticker": "AMD", "related": ["SOXL"]},
            {"status": "negative", "title": "미국 법무부, 반독점 점검 위해 빅테크 AI 독점 조사 수위 강화 검토", "ticker": "NVDA", "related": ["AMD", "SOXL"]},
            {"status": "positive", "title": "SK하이닉스, 12단 HBM3E 엔비디아 최종 퀄테스트 통과 임박 소식에 강세", "ticker": "SK Hynix", "related": ["NVDA"]},
            {"status": "negative", "title": "국제 유가 및 국채 금리 재상승 분위기... 기술주 중심 차익실현 매물 출하", "ticker": "SOXL", "related": ["NVDA", "AMD"]}
        ]
        
        col_news1, col_news2 = st.columns(2)
        with col_news1:
            st.markdown("<h4 style='color:#22c55e;'>긍정 시그널</h4>", unsafe_allow_html=True)
            for n in [n for n in news_feeds if n["status"] == "positive"]:
                with st.container(border=True):
                    st.markdown(f"**{n['title']}**")
                    st.markdown(f"<small>관련주: `{n['ticker']}` " + " ".join([f"`{r}`" for r in n["related"]]) + "</small>", unsafe_allow_html=True)
                    
        with col_news2:
            st.markdown("<h4 style='color:#ef4444;'>경계 시그널</h4>", unsafe_allow_html=True)
            for n in [n for n in news_feeds if n["status"] == "negative"]:
                with st.container(border=True):
                    st.markdown(f"**{n['title']}**")
                    st.markdown(f"<small>관련주: `{n['ticker']}` " + " ".join([f"`{r}`" for r in n["related"]]) + "</small>", unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # [서브탭 2] 정밀 매도 시뮬레이터
    # ------------------------------------------------------------------
    with sub_tab2:
        if df is None or df.empty:
            st.warning("데이터가 없습니다.")
            return

        unique_titles = df['종목명'].unique()
        st.markdown("### 연간 기본 공제(250만 원) 안전 익절 가이드")
        
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
                    "종목명": name, "현재 주가 ($)": f"${live_price:,.2f}",
                    "안전 매도 가능 수량": f"{safe_qty:,.2f} 주", "예상 익절 금액 (원)": f"₩{int(safe_eval_krw):,}"
                })
        if zero_tax_rows:
            st.table(pd.DataFrame(zero_tax_rows))
        
        st.divider()
        st.markdown("### 특정 종목 조준 매도 시뮬레이션")
        selected_stock = st.selectbox("시뮬레이션할 종목 선택", unique_titles, key="stock_sel_guide_new")
        stock_df = df[df['종목명'] == selected_stock].sort_values('매수일자')
        ticker_code = stock_df.iloc[0]['코드']
        total_owned_qty = stock_df['매수수량'].sum()
        live_price = current_prices.get(ticker_code, 0.0)
        
        col_sim1, col_sim2 = st.columns(2)
        with col_sim1:
            sell_qty_input = st.number_input(f"매도할 수량 (보유: {total_owned_qty:,.2f}주)", min_value=0.0, max_value=float(total_owned_qty), value=float(total_owned_qty))
        with col_sim2:
            sell_price_input = st.number_input("예상 매도 가격 ($)", min_value=0.0, value=float(live_price))

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
            fifo_gain_krw += ((sell_price_input * exchange_rate) - row_cost_krw) * take_qty
            rem_qty -= take_qty

        res_col1, res_col2 = st.columns(2)
        with res_col1:
            st.metric(label="이동평균법 차익", value=f"₩{int(ma_gain_krw):,}")
        with res_col2:
            st.metric(label="선입선출법(FIFO) 차익", value=f"₩{int(fifo_gain_krw):,}")

    # ------------------------------------------------------------------
    # [서브탭 3] 계산법 원리 마스터
    # ------------------------------------------------------------------
    with sub_tab3:
        st.markdown("### 한눈에 비교하는 세금 계산법 차이 원리")
        
        with st.container(border=True):
            st.markdown("**시뮬레이션 가상 계좌 조건**\n"
                        "* 1차 매수: 10주를 $100에 매수 (원화 환산 원가: ₩1,400,000)\n"
                        "* 2차 매수: 10주를 $200에 매수 (원화 환산 원가: ₩2,800,000)\n"
                        "* 종합 평단가: $150 (총 20주 보유, 총 원가 ₩4,200,000)")
        
        st.write("")
        test_sell_price = st.slider("가상의 오늘 밤 매도 단가 설정 ($)", min_value=120, max_value=300, value=250, step=10, key="interactive_example_slider")
        test_qty = 10
        
        current_rate = 1400.0
        total_sell_amount_krw = test_sell_price * test_qty * current_rate
        ma_cost_krw = 150 * test_qty * current_rate
        ma_gain_krw = total_sell_amount_krw - ma_cost_krw
        fifo_cost_krw = 100 * test_qty * current_rate
        fifo_gain_krw = total_sell_amount_krw - fifo_cost_krw

        st.markdown("#### 연산 데이터 대조표 (10주 전량 매도 시)")
        compare_data = {
            "구분 항목": ["총 매도 대금 (원화)", "장부상 취득 원가 (국가 인정)", "최종 계산된 양도차익"],
            "이동평균법 (증권사 앱)": [f"₩{int(total_sell_amount_krw):,}", f"₩{int(ma_cost_krw):,}", f"₩{int(ma_gain_krw):,}"],
            "선입선출법 (국세청 기준)": [f"₩{int(total_sell_amount_krw):,}", f"₩{int(fifo_cost_krw):,}", f"₩{int(fifo_gain_krw):,}"]
        }
        st.table(pd.DataFrame(compare_data))

        st.markdown("#### 원가와 실제 차익 비중 비교")
        chart_rows = [
            {"방식": "이동평균법", "항목": "취득 원가", "금액(원)": ma_cost_krw},
            {"방식": "이동평균법", "항목": "양도차익", "금액(원)": ma_gain_krw},
            {"방식": "선입선출법", "항목": "취득 원가", "금액(원)": fifo_cost_krw},
            {"방식": "선입선출법", "항목": "양도차익", "금액(원)": fifo_gain_krw}
        ]
        df_chart = pd.DataFrame(chart_rows)
        fig_compare = px.bar(df_chart, x="방식", y="금액(원)", color="항목", 
                             color_discrete_map={"취득 원가": "#cbd5e1", "양도차익": "#3b82f6"})
        fig_compare.update_layout(height=350, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_compare, use_container_width=True)

        st.divider()
        st.markdown("#### 최종 리밸런싱 가이드라인 요약")
        gap = int(abs(fifo_gain_krw - ma_gain_krw))
        
        st.warning(f"현재 설정하신 가상 매도 단가 ${test_sell_price} 기준으로 연산 시, 국세청 선입선출법 방식의 장부상 차익이 증권사 이동평균법보다 ₩{gap:,}원 더 크게 잡힙니다.")
        st.markdown(f"""
            * **원인 분석:** 선입선출법은 과거에 저렴하게 샀던 $100짜리 물량부터 먼저 처리하므로 장부상 원가가 낮게 잡혀 수익(차익)이 튀게 됩니다.
            * **실전 꿀팁:** 증권사 계좌에 찍힌 평단가와 수익률만 보고 무턱대고 익절했다가는 나중에 국세청 양도세 신고 기간에 예상치 못한 세금 고지서를 받을 수 있습니다. 매도 버튼을 누르기 전에 반드시 이 대시보드로 격차를 체크하셔야 안전합니다!
        """)
        
        st.divider()
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
        st.download_button(label="국세청 신고용 시뮬레이션 데이터 다운로드 (CSV)", data=csv_data, file_name="국세청_해외주식_신고보조자료.csv", mime="text/csv")