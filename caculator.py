import pandas as pd
import os

# 1. 파일 이름 설정
FILE_NAME = "14매수일자별잔고.xls.xlsx"

def run_tax_simulator():
    if not os.path.exists(FILE_NAME):
        print(f"❌ 에러: 폴더 안에 '{FILE_NAME}' 파일이 없습니다!")
        return

    try:
        # 상단 서식 3줄을 건너뛰고 진짜 데이터를 읽어옵니다.
        df = pd.read_csv(FILE_NAME, skiprows=3) if FILE_NAME.endswith('.csv') else pd.read_excel(FILE_NAME, skiprows=3)
        
        # 데이터 공백 제거 및 숫자 변환
        df['종목명'] = df['종목명'].str.strip()
        df['매수수량'] = pd.to_numeric(df['매수수량'], errors='coerce')
        df['매수가'] = pd.to_numeric(df['매수가'], errors='coerce')
        df['매수금액(원)'] = pd.to_numeric(df['매수금액(원)'], errors='coerce')
        df = df.dropna(subset=['종목명', '매수수량', '매수가'])
        
    except Exception as e:
        print(f"❌ 파일을 읽는 중 오류가 발생했습니다: {e}")
        return

    print("\n" + "="*60)
    print("       🎉 최은비 님의 실시간 보유주식 포트폴리오 분석 결과 🎉")
    print("="*60)
    
    # 종목별 요약 정보 계산 및 출력
    summary_data = []
    for name, group in df.groupby('종목명'):
        total_qty = group['매수수량'].sum()
        total_cost_krw = group['매수금액(원)'].sum()
        
        # 이동평균 단가 (원화 기준)
        avg_price_krw = total_cost_krw / total_qty if total_qty > 0 else 0
        
        # 선입선출 기준 (가장 오래된 물량의 단가)
        group_sorted = group.sort_values('매수일자')
        oldest_price = group_sorted.iloc[0]['매수가']
        oldest_date = group_sorted.iloc[0]['매수일자']
        
        summary_data.append({
            "종목명": name,
            "보유수량": int(total_qty),
            "이동평균단가(원)": f"{int(avg_price_krw):,}",
            "FIFO_최고령단가($)": f"${oldest_price:,.2f}",
            "FIFO_최고령매수일": oldest_date
        })
        
    print(pd.DataFrame(summary_data).to_string(index=False))
    print("="*60)
    
    # 2. 절세 시뮬레이터 인터페이스
    print("\n🔮 [절세 시뮬레이션 대화창]")
    print("현재 계좌에서 주식을 매도한다고 가정할 때, 어떤 방식이 유리한지 비교해 드립니다.")
    
    target_stock = input("➔ 시뮬레이션할 종목명을 정확히 입력하세요 (예: 애플, 엔비디아): ").strip()
    
    if target_stock not in df['종목명'].unique():
        print("❌ 해당 종목은 현재 보유 잔고에 없습니다. 종목명을 다시 확인해 주세요.")
        return
        
    stock_group = df[df['종목명'] == target_stock].sort_values('매수일자')
    total_owned = stock_group['매수수량'].sum()
    
    print(f"현재 [{target_stock}] 주식을 총 {int(total_owned)}주 보유 중이십니다.")
    sell_qty = int(input(f"➔ 몇 주를 매도할 예정이신가요? (1 ~ {int(total_owned)}): "))
    
    if sell_qty > total_owned or sell_qty <= 0:
        print("❌ 보유 수량을 초과했거나 잘못된 수량입니다.")
        return
        
    sell_price = float(input("➔ 예상 매도 단가($)를 입력하세요 (숫자만): "))
    
    # [이동평균법 계산]
    total_cost_usd = (stock_group['매수가'] * stock_group['매수수량']).sum()
    avg_price_usd = total_cost_usd / total_owned
    ma_cost_basis = avg_price_usd * sell_qty
    ma_revenue = sell_price * sell_qty
    ma_gain = ma_revenue - ma_cost_basis
    
    # [선입선출법 계산]
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
            
    fifo_revenue = sell_price * sell_qty
    fifo_gain = fifo_revenue - fifo_cost_basis
    
    print("\n" + "-"*50)
    print(f"📊 [{target_stock}] {sell_qty}주 매도 시 양도차익(이익) 비교 결과")
    print("-"*50)
    print(f"▶ 이동평균법 적용 시 이익: ${ma_gain:,.2f} (원가 적용 단가: ${avg_price_usd:,.2f})")
    print(f"▶ 선입선출법 적용 시 이익: ${fifo_gain:,.2f} (과거 매수 물량부터 차감)")
    print("-"*50)
    
    if ma_gain < fifo_gain:
        tax_diff = fifo_gain - ma_gain
        print(f"💡 [절세 매매 팁] '이동평균법'이 이익이 ${tax_diff:,.2f} 만큼 더 적게 잡힙니다!")
        print("   따라서 지금 당장 세금을 줄이고 싶다면 이동평균법이 유리할 수 있습니다.")
    elif ma_gain > fifo_gain:
        tax_diff = ma_gain - fifo_gain
        print(f"💡 [절세 매매 팁] '선입선출법'이 이익이 ${tax_diff:,.2f} 만큼 더 적게 잡힙니다!")
        print("   따라서 지금 당장 세금을 줄이고 싶다면 선입선출법이 유리할 수 있습니다.")
    else:
        print("두 방식의 계산 결과가 동일합니다.")
    print("="*60)

if __name__ == "__main__":
    run_tax_simulator()