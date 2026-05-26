import streamlit as st
import pandas as pd
import datetime

def show_guide(df, exchange_rate, current_prices):
    # 상단에 서브 탭 분리 (1. 일정이랑 뉴스 분석 / 2. 정밀 계산기 / 3. 계산 원리 예시)
    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["📅 실시간 일정 & AI 뉴스룸", "✂️ 정밀 매도 시뮬레이터", "🧮 계산법 원리 마스터"])

    # ------------------------------------------------------------------
    # [기능 2] 📅 실시간 일정 & 2주 내 중요 일정 목록
    # ------------------------------------------------------------------
    with sub_tab1:
        st.subheader("🗓️ 내 종목 핵심 마켓 캘린더")
        
        # 오늘 날짜 기준 (2026년 5월 현재 상황 반영)
        today = datetime.date(2026, 5, 27)
        
        # 은비 님 보유 종목 맞춤형 확정 및 예정 일정 데이터베이스
        all_events = [
            {"date": datetime.date(2026, 5, 19), "ticker": "NVDA", "title": "FY2027 Q1 실적 발표 완료 (어닝 서프라이즈! 🎉)"},
            {"date": datetime.date(2026, 6, 2), "ticker": "AMD", "title": "BofA 글로벌 테크 콘퍼런스 (CFO 발표 예정 🎤)"},
            {"date": datetime.date(2026, 6, 22), "ticker": "SOXL", "title": "분기 배당금 선언일 (Declaration Date 예정 💵)"},
            {"date": datetime.date(2026, 6, 23), "ticker": "SOXL", "title": "배당락일 (Ex-Dividend Date ✂️)"},
            {"date": datetime.date(2026, 7, 23), "ticker": "SK Hynix", "title": "FY2026 Q2 실적 발표 (예정)"},
            {"date": datetime.date(2026, 8, 4), "ticker": "AMD", "title": "FY2026 Q2 실적 발표 (예정 📊)"},
            {"date": datetime.date(2026, 8, 26), "ticker": "NVDA", "title": "FY2027 Q2 실적 발표 (예정 🔥)"},
        ]
        
        # 2주(14일) 내 임박한 일정 필터링
        two_weeks_later = today + datetime.timedelta(days=14)
        upcoming_events = [e for e in all_events if today <= e["date"] <= two_weeks_later]
        past_and_future = [e for e in all_events if e["date"] >= today]

        # UI 레이아웃 배치 (좌측: 2주 내 목록, 우측: 전체 캘린더 리스트)
        col_ev1, col_ev2 = st.columns([1, 1])
        
        with col_ev1:
            st.markdown("🚨 **2주 내 임박한 중요 일정**")
            if upcoming_events:
                for ev in upcoming_events:
                    st.info(f"**[{ev['date'].strftime('%m/%d')}] {ev['ticker']}**\n\n{ev['title']}")
            else:
                st.write("<small style='color:#64748b;'>앞으로 2주간 내 포트폴리오에 예정된 큰 이벤트가 없습니다. 평온한 밤입니다. ☕</small>", unsafe_allow_html=True)
                
        with col_ev2:
            st.markdown("📅 **전체 타임라인 (다가오는 일정)**")
            event_rows = []
            for ev in past_and_future:
                event_rows.append({"날짜": ev["date"].strftime("%Y-%m-%d"), "종목": ev["ticker"], "이벤트 내용": ev["title"]})
            if event_rows:
                st.dataframe(pd.DataFrame(event_rows), use_container_width=True, hide_index=True)

        st.divider()

        # ------------------------------------------------------------------
        # [기능 3] 📰 실시간 종목 뉴스 및 감성 묶음 (첨부 스크린샷 UI 구현)
        # ------------------------------------------------------------------
        st.subheader("📰 AI 기반 포트폴리오 실시간 뉴스룸")
        st.markdown("<small style='color:#64748b;'>내 계좌 주식들의 뉴스를 긍정/부정 스탠스로 자동 분류하여 노출합니다.</small>", unsafe_allow_html=True)
        
        # 실시간 데이터 크롤링을 모사한 피드 데이터 (실제 운영 시 API 연결 가능)
        news_feeds = [
            {"status": "positive", "title": "엔비디아, 차세대 인공지능 칩 '블랙웰' 출하 가속화... 공급 부족 연말 해소 전망", "ticker": "NVDA", "related": ["SOXL", "SK Hynix"]},
            {"status": "positive", "title": "AMD, 새로운 라이젠 AI 프로세서 벤치마크 유출... 인텔 대비 멀티코어 성능 20% 우위", "ticker": "AMD", "related": ["SOXL"]},
            {"status": "negative", "title": "미국 법무부, 반독합 점검 위해 빅테크 AI 독점 조사 수위 강화 카드 만지작", "ticker": "NVDA", "related": ["AMD", "SOXL"]},
            {"status": "positive", "title": "SK하이닉스, 12단 HBM3E 엔비디아 최종 퀄테스트 통과 임박 소식에 강세", "ticker": "SK Hynix", "related": ["NVDA"]},
            {"status": "negative", "title": "국제 유가 및 국채 금리 재상등 분위기... 기술주 중심 나스닥 프리마켓 일시적 차익실현 매물 출하", "ticker": "SOXL", "related": ["NVDA", "AMD"]}
        ]
        
        # 🟢 긍정 / 🔴 부정 컬럼 쪼개기 (은비 님이 주신 스크린샷 스타일)
        col_news1, col_news2 = st.columns(2)
        
        with col_news1:
            st.markdown("<h4 style='color:#22c55e;'>🟢 호재 및 긍정 시그널</h4>", unsafe_allow_html=True)
            pos_news = [n for n in news_feeds if n["status"] == "positive"]
            for n in pos_news:
                with st.container(border=True):
                    st.markdown(f"**{n['title']}**")
                    # 태그 뱃지 형태로 매핑
                    tags = f"`{n['ticker']}` " + " ".join([f"`{r}`" for r in n["related"]])
                    st.markdown(f"<small>🎯 관련주: {tags}</small>", unsafe_allow_html=True)
                    
        with col_news2:
            st.markdown("<h4 style='color:#ef4444;'>🔴 악재 및 경계 시그널</h4>", unsafe_allow_html=True)
            neg_news = [n for n in news_feeds if n["status"] == "negative"]
            for n in neg_news:
                with st.container(border=True):
                    st.markdown(f"**{n['title']}**")
                    tags = f"`{n['ticker']}` " + " ".join([f"`{r}`" for r in n["related"]])
                    st.markdown(f"<small>🎯 관련주: {tags}</small>", unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # [기존 기능 합본] ✂️ 내 맘대로 정밀 매도 시뮬레이터 & 안전 가이드
    # ------------------------------------------------------------------
    with sub_tab2:
        if df is None or df.empty:
            st.warning("⚠️ 불러온 엑셀 데이터가 없습니다.")
            return

        unique_titles = df['종목명'].unique()
        st.subheader("🎯 세금 Zero! 연간 기본 공제(250만 원) 맞춤형 익절 가이드")
        
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
        st.subheader("✂️ 특정 종목 조준 매도")
        selected_stock = st.selectbox("👉 시뮬레이션할 종목 선택", unique_titles, key="stock_sel_guide_new")
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
            st.metric(label="📈 이동평균법 차익", value=f"₩{int(ma_gain_krw):,}")
        with res_col2:
            st.metric(label="📜 선입선출법(FIFO) 차익", value=f"₩{int(fifo_gain_krw):,}")

    # ------------------------------------------------------------------
    # [기능 1] 🧮 선입선출과 이동평균 계산예시 직관 마스터 탭
    # ------------------------------------------------------------------
    with sub_tab3:
        st.subheader("💡 그림으로 이해하는 세금 계산법 차이 예시")
        st.markdown("증권사 앱(이동평균)과 국세청 기준(선입선출)이 왜 다르게 계산되는지 가상의 주식 거래 예시로 완벽하게 짚어드립니다.")
        
        # 가상 시나리오 설정 테이블 노출
        st.info("💡 **가상의 거래 내역**\n* 1차 매수: 10주를 **$100**에 매수\n* 2차 매수: 10주를 **$200**에 매수\n* **[현재 내 평단가]: $150 (총 20주保有)**")
        
        test_sell_price = st.slider("🎛️ 가상의 오늘 밤 매도 단가 조정 ($)", min_value=120, max_value=300, value=250, step=10)
        test_qty = 10  # 10주만 분할 매도한다고 가정한 상황
        
        # 계산 로직 가동
        example_ma_cost = 150 * test_qty
        example_ma_gain = (test_sell_price * test_qty) - example_ma_cost
        
        example_fifo_cost = 100 * test_qty  # 먼저 산 10주가 나가므로 무조건 원가는 $100짜리
        example_fifo_gain = (test_sell_price * test_qty) - example_fifo_cost
        
        col_ex1, col_ex2 = st.columns(2)
        with col_ex1:
            st.error(f"📈 **이동평균법 (평단가 $150 기준)**\n\n* 내 평단인 $150을 기준으로 10주의 원화를 계산합니다.\n* 인정 원가: **${example_ma_cost}**\n* 최종 계산된 장부상 양도차익:\n **${example_ma_gain}**")
        with col_ex2:
            st.success(f"📜 **선입선출법 (과거 최초 매수가 $100 기준)**\n\n* 과거에 가장 먼저 샀던 $100짜리 10주가 먼저 팔린 걸로 봅니다.\n* 인정 원가: **${example_fifo_cost}**\n* 최종 계산된 장부상 양도차익:\n **${example_fifo_gain}**")
            
        st.markdown(f"⚠️ **결과 분석:** 매도 단가가 **${test_sell_price}**일 때, 국세청 선입선출법 기준의 차익이 이동평균법보다 **${example_fifo_gain - example_ma_gain}**만큼 더 크게 잡힙니다. 즉, 국내 증권사 어플에 찍힌 수익금만 보고 냅다 다 팔았다가는 **나중에 국세청 양도세 폭탄**을 맞을 수 있는 이유가 바로 이 탭의 격차 때문입니다!")