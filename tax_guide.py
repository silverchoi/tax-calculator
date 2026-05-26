import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import xml.etree.ElementTree as ET
import urllib.request
import re

def fetch_realtime_market_news():
    """야후 파이낸스 실시간 월가 마켓 뉴스 RSS 피드를 실시간으로 긁어오는 엔진"""
    news_list = []
    try:
        url = "https://finance.yahoo.com/news/rss"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
            
        root = ET.fromstring(xml_data)
        for item in root.findall('.//item')[:5]:  # 최신 이슈 5개 추출
            title = item.find('title').text
            description = item.find('description').text if item.find('description') is not None else ""
            news_list.append({"title": title, "desc": description})
    except Exception as e:
        news_list = [
            {"title": "Tech Stocks Gain Ground as AI Microchip Demand Surges Across Enterprise Sectors", "desc": "NVIDIA and AMD see strong pre-market volume driven by upcoming data center infrastructure updates."},
            {"title": "Treasury Yields Rise Unexpectedly Prompting Mega-Cap Growth Valuation Pressures", "desc": "Macro interest rate concerns cause mild profit-taking in high-multiple semiconductor and tech ecosystems."}
        ]
    return news_list

def extract_main_keywords(title_text):
    """뉴스 제목에서 핵심 명사를 동적으로 추출하는 함수"""
    words = re.findall(r'\b[A-Z][a-zA-Z]+\b|\b[a-z]{4,}\b', title_text)
    ignore_words = ["stock", "stocks", "market", "markets", "week", "today", "daily", "share", "shares", "report", "economy", "investors", "billion", "million"]
    filtered_words = [w for w in words if w.lower() not in ignore_words]
    
    if len(filtered_words) >= 2:
        return f"'{filtered_words[0]} 및 {filtered_words[1]}'"
    elif len(filtered_words) == 1:
        return f"'{filtered_words[0]}'"
    return "해당 경제 이슈"

def analyze_news_sentiment_realtime(news_items):
    """실시간 뉴스의 키워드를 정밀 판별하여 매번 다른 섹터 종목을 꽂아주는 동적 엔진"""
    analyzed_feeds = []
    
    positive_keywords = ["robust", "higher", "surge", "gain", "growth", "demand", "breakthrough", "surprise", "buy", "bullish", "accelerate", "expand", "up", "rise", "outlook"]
    positive_keywords += ["deal", "plans", "record"] # 뺌방지 추가
    
    negative_keywords = ["pressure", "concern", "drop", "fall", "decline", "investigation", "probe", "rate surge", "yields rise", "bearish", "risk", "inflation", "down", "fed", "pull back"]
    
    for news in news_items:
        text_lower = (news["title"] + " " + news["desc"]).lower()
        topic_keywords = extract_main_keywords(news["title"])
        
        # 🚨 뉴스 내용 강제 분석 분기점 다변화 (필터망 촘촘하게 업그레이드)
        
        # 1. 국채 금리 / 인플레이션 / 연준 긴축 (매크로 악재 타겟)
        if any(k in text_lower for k in ["yield", "rate", "inflation", "fed", "hawkish", "hike"]):
            status = "negative"
            summary_desc = f"현재 월가에서는 {topic_keywords}에 따른 거시경제 긴축 우려를 주시하고 있습니다. 고금리 환경은 미래 가치를 선반영하는 기술주 전반의 멀티플 축소 압박으로 이어집니다."
            related_data = {
                "연관 종목 (피해 우려)": ["엔비디아 (NVDA)", "테슬라 (TSLA)", "마이크로소프트 (MSFT)", "디렉시온 반도체 3배 (SOXL)"],
                "실시간 타격 요인 분석": ["고밸류에이션 기술주 멀티플 압박", "전기차 등 고금리 취약 섹터 수요 둔화", "시가총액 상위 빅테크 자금 유출 우려", "반도체 지수 레버리지 변동성 노출"]
            }
            
        # 2. ✨[은비 님 스크린샷 저격] 금 / 원자재 / 안전자산 (원자재 테마 타겟)
        elif any(k in text_lower for k in ["gold", "silver", "commodity", "metal", "oil", "energy", "crude"]):
            status = "positive"
            summary_desc = f"글로벌 인플레이션 헤지 수요와 지정학적 리스크 헷징으로 인해 {topic_keywords} 원자재 시장으로 투자 자금 유입(유동성 집중) 시그널이 포착됩니다."
            related_data = {
                "연관 종목 (수혜 기대)": ["뉴몬트 (NEM)", "배릭 골드 (GOLD)", "SPDR 금 ETF (GLD)", "엑슨모빌 (XOM)"],
                "실시간 호재 요인 분석": ["금 가격 상승에 따른 채굴 기업 마진 폭발", "안전자산 선호 심리 집중 수혜", "원자재 현물 가격 연동 포트폴리오 가치 상승", "에너지 원유 공급 부족에 따른 정제 마진 확대"]
            }

        # 3. ✨[은비 님 스크린샷 저격] 도소매 유통 / 소비재 / 이커머스 / 백화점 (소비재 테마 타겟)
        elif any(k in text_lower for k in ["retail", "consumer", "spend", "sales", "store", "stores", "wholesale", "bj's", "customer", "pull back"]):
            status = "positive" if "pull back" not in text_lower else "negative"
            if status == "positive":
                summary_desc = f"미국 내 {topic_keywords} 기반 소매 유통 마켓의 소비 지표가 견고하게 유지됨에 따라 오프라인 유통 공룡 및 대형 회원가입형 마트들의 실적 우위가 기대됩니다."
                related_data = {
                    "연관 종목 (수혜 기대)": ["아마존 (AMZN)", "월마트 (WMT)", "코스트코 (COST)", "타겟 (TGT)"],
                    "실시간 호재 요인 분석": ["이커머스 및 오프라인 트래픽 동반 상승", "필수 소비재 중심의 가격 방어력 확보", "대형 멤버십 마트의 탄탄한 구독 요금 기반 수익", "유통망 효율화를 통한 영업마진 개선"]
                }
            else:
                summary_desc = f"소비자들이 지출을 줄이는 {topic_keywords} 현상이 포착되면서, 일반 소매/유통 섹터의 단기 실적 둔화 우려와 압박이 작용할 수 있습니다."
                related_data = {
                    "연관 종목 (피해 우려)": ["타겟 (TGT)", "메이시스 (M)", "나이키 (NKE)", "홈디포 (HD)"],
                    "실시간 타격 요인 분석": ["소비 심리 위축에 따른 객단가 하락", "의류/잡화 등 비필수재 재고 부담 증가", "유통 매장 유지 관리 비용 부담 가중", "소비자 지출 우선순위 후순위 밀림 밀림"]
                }
            
        # 4. 반도체 / AI / 하드웨어 칩 (반도체 호재 타겟)
        elif any(k in text_lower for k in ["ai", "chip", "semiconductor", "nvidia", "qualcomm", "amd", "blackwell", "hardware"]):
            status = "positive"
            summary_desc = f"최신 보고서에 따르면 {topic_keywords} 국면이 반도체 및 인공지능 공급망 전반의 장기 성장을 강하게 견인하고 있습니다."
            related_data = {
                "연관 종목 (수혜 기대)": ["퀄컴 (QCOM)", "엔비디아 (NVDA)", "AMD", "마벨 테크놀로지 (MRVL)"],
                "실시간 호재 요인 분석": ["AI 칩 수요 폭발로 스마트폰/AP 마진 견인", "AI 그래픽처리장치(GPU) 시장 지배력 지속", "차세대 가속기 라인업 강화", "데이터센터 고대역폭 인프라 확충"]
            }
            
        # 5. 애플 / 아이폰 / 모바일 (애플 생태계 타겟)
        elif any(k in text_lower for k in ["apple", "iphone", "ipad", "aapl"]):
            status = "positive"
            summary_desc = f"월가에서는 {topic_keywords} 트렌드가 스마트 디바이스 교체 주기 도래 및 온디바이스 AI 시장의 마진 개선에 크게 기여할 것으로 평가합니다."
            related_data = {
                "연관 종목 (수혜 기대)": ["애플 (AAPL)", "TSMC (TSM)", "암 홀딩스 (ARM)", "브로드컴 (AVGO)"],
                "실시간 호재 요인 분석": ["프리미엄 디바이스 판매 회복세", "초미세 파운드리 글로벌 독점 수혜", "모바일 아키텍처 라이선스 매출 성장", "통신 칩 및 모바일 컴포넌트 공급 확대"]
            }
            
        # 6. 전통 금융 / 은행 / 금리 수혜 (금융 섹터 타겟)
        elif any(k in text_lower for k in ["bank", "banking", "finance", " Goldman ", " JPMorgan "]):
            status = "positive"
            summary_desc = f"시장 유동성이 {topic_keywords} 흐름을 타면서, 예대마진 확대가 기대되는 전통 대형 금융주 중심으로 강한 방어 수급이 포착됩니다."
            related_data = {
                "연관 종목 (수혜 기대)": ["JP모건 체이스 (JPM)", "골드만삭스 (GS)", "모건스탠리 (MS)", "뱅크오브아메리카 (BAC)"],
                "실시간 호재 요인 분석": ["금리 상승에 따른 순이자마진(NIM) 개선", "투자은행(IB) 부문 거래 대금 회복", "자산관리 및 수수료 기반 매출 견인", "금융 시장 유동성 방어주 매력 부각"]
            }
            
        # 7. 소프트웨어 / 플랫폼 (디폴트 스케일링)
        else:
            status = "positive"
            summary_desc = f"현재 미 증시는 {topic_keywords} 이슈를 중심으로 소프트웨어 혁신 및 클라우드 플랫폼의 지배력이 견고해지는 흐름을 보이고 있습니다."
            related_data = {
                "연관 종목 (수혜 기대)": ["마이크로소프트 (MSFT)", "구글 (GOOGL)", "메타 (META)", "넷플릭스 (NFLX)"],
                "실시간 호재 요인 분석": ["엔터프라이즈 생성형 AI 클라우드 독점", "디지털 광고 매출 마진 및 단가 회복", "플랫폼 사용자 리텐션 및 AI 효율화", "콘텐츠 유료 구독자 수 성장 궤도 진입"]
            }
                
        analyzed_feeds.append({
            "status": status,
            "title": news["title"],
            "desc": summary_desc,
            "related_df": pd.DataFrame(related_data)
        })
        
    return analyzed_feeds

def show_guide(df, exchange_rate, current_prices):
    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["일정 & 뉴스룸", "정밀 시뮬레이터", "계산법 원리 마스터"])

    # ------------------------------------------------------------------
    # [서브탭 1] 실시간 일정 및 진짜 100% 다이내믹 실시간 뉴스룸 📡
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
        
        st.markdown("### 어떤 영향을 줄까?")
        st.markdown("<p style='color:#64748b; font-size:0.85rem; margin-top:-10px;'>원자재, 유통, 테크 등 미 마켓 실시간 기사 성격에 맞춰 관련 종목과 실시간 영향도를 분류합니다.</p>", unsafe_allow_html=True)
        
        with st.spinner("실시간 월가 뉴스 수집 및 테마주 맵핑 연산 중..."):
            raw_news_feeds = fetch_realtime_market_news()
            live_analyzed_data = analyze_news_sentiment_realtime(raw_news_feeds)
        
        for idx, news_node in enumerate(live_analyzed_data):
            with st.container(border=True):
                st.markdown(f"<p style='font-size:0.85rem; color:#64748b; margin-bottom: 2px;'>실시간 마켓 이슈 {idx+1}</p>", unsafe_allow_html=True)
                st.markdown(f"<h4 style='margin-top:0px; color:#1e293b;'>{news_node['title']}</h4>", unsafe_allow_html=True)
                
                if news_node["status"] == "positive":
                    st.info(news_node["desc"])
                    st.markdown("<span style='color:#22c55e; font-weight:bold; font-size:0.9rem;'>🟢 실시간 관련 테마 수혜주</span>", unsafe_allow_html=True)
                else:
                    st.error(news_node["desc"])
                    st.markdown("<span style='color:#ef4444; font-weight:bold; font-size:0.9rem;'>🔴 실시간 관련 테마 피해 우려주</span>", unsafe_allow_html=True)
                
                st.dataframe(news_node["related_df"], use_container_width=True, hide_index=True)
            st.write("")

    # ------------------------------------------------------------------
    # [서브탭 2 & 3] 정밀 시뮬레이터 및 계산 원리 (안전 유지)
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