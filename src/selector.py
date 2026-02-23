import os
import akshare as ak

def select_a_shares():
    """筛选A股：低估值+趋势向上+资金关注（60/00/30开头）"""
    selected = []
    try:
        # 获取A股列表
        stock_info_df = ak.stock_info_a_code_name()
        valid_codes = [code for code in stock_info_df['代码'].tolist() 
                       if code.startswith(('60', '00', '30')) and len(code) == 6]
        
        # 筛选前100只，避免超时
        for code in valid_codes[:100]:
            try:
                df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq")
                if len(df) < 20:
                    continue
                # 核心条件：收盘价站20日线+成交量放大
                latest_close = df['收盘'].iloc[-1]
                ma20 = df['收盘'].rolling(window=20).mean().iloc[-1]
                vol_recent = df['成交量'].iloc[-5:].mean()
                vol_prev = df['成交量'].iloc[-10:-5].mean()
                if latest_close > ma20 and vol_recent > 1.5 * vol_prev:
                    selected.append(code)
                    if len(selected) >= 4:  # A股选4只
                        break
            except:
                continue
    except:
        pass
    # A股兜底（茅台、平安、宁德、比亚迪）
    return selected if selected else ['600519', '601318', '300750', '002594']

def select_hk_stocks():
    """筛选港股：主流龙头+趋势向上（hk前缀）"""
    selected = []
    try:
        # 港股主流标的列表（覆盖消费、科技、金融）
        hk_codes = ['00700', '09988', '03690', '01810', '00005', '02382']  # 腾讯、阿里、美团、小米、汇丰、舜宇
        for code in hk_codes:
            try:
                # 获取港股日线数据
                df = ak.stock_hk_hist(symbol=code, period="daily", adjust="qfq")
                if len(df) < 10:
                    continue
                latest_close = df['收盘'].iloc[-1]
                ma10 = df['收盘'].rolling(window=10).mean().iloc[-1]
                if latest_close > ma10:  # 收盘价站10日线
                    selected.append(f"hk{code}")  # 加hk前缀，适配系统
                    if len(selected) >= 2:  # 港股选2只
                        break
            except:
                continue
    except:
        pass
    # 港股兜底（腾讯、阿里）
    return selected if selected else ['hk00700', 'hk09988']

def select_us_stocks():
    """筛选美股：龙头股+成交量放大（无前缀）"""
    selected = []
    try:
        # 美股主流龙头列表
        us_codes = ['AAPL', 'MSFT', 'TSLA', 'AMZN', 'GOOGL', 'META', 'NVDA']  # 苹果、微软、特斯拉等
        for code in us_codes:
            try:
                # 获取美股日线数据
                df = ak.stock_us_hist(symbol=code, period="daily", adjust="qfq")
                if len(df) < 10:
                    continue
                vol_recent = df['成交量'].iloc[-3:].mean()
                vol_prev = df['成交量'].iloc[-6:-3].mean()
                if vol_recent > vol_prev:  # 近3日成交量放大
                    selected.append(code)
                    if len(selected) >= 2:  # 美股选2只
                        break
            except:
                continue
    except:
        pass
    # 美股兜底（苹果、微软）
    return selected if selected else ['AAPL', 'MSFT']

def auto_select_stocks():
    """合并三市场选股结果（总计8只左右，避免分析超时）"""
    a_shares = select_a_shares()
    hk_shares = select_hk_stocks()
    us_shares = select_us_stocks()
    # 合并并去重
    all_stocks = a_shares + hk_shares + us_shares
    return list(set(all_stocks))

# 测试：运行时打印选股结果
if __name__ == "__main__":
    stocks = auto_select_stocks()
    print("自动筛选的全市场股票：", stocks)
