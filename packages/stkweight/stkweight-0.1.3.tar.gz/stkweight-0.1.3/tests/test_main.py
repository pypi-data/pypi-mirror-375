import pandas as pd
from stkweight.core import plot_weight_candlestick_daily_full_range_with_volume


def test_plot_weight_candlestick_daily_full_range_with_volume():
    df = pd.read_csv('tests/resources/weight.csv',index_col=0)

    df.columns = [i.strip() for i in df.columns]

    # --- 调用绘图函数 ---
    print("\n--- 每日全范围波动蜡烛图 (带净卡路里成交量) 示例 ---")
    ma_config_daily = [
        {'period': 5, 'price_col': 'EveningWeight', 'color': 'blue'},
        {'period': 10, 'price_col': 'MorningWeight', 'color': 'purple'}
    ]
    plot_weight_candlestick_daily_full_range_with_volume(df, ma_configs=ma_config_daily, show_calorie_volume=True,show = False)
