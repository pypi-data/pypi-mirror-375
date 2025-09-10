import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import plotly.graph_objects as go
import plotly.io as pio # 导入 io 模块

# --- 均线生成函数 (保持不变) ---
def create_moving_average_trace(df, date_col, price_col, ma_periods, ma_colors=None):
    traces = []
    if ma_colors is None:
        ma_colors = ['blue', 'purple', 'orange', 'grey', 'brown']

    for i, period in enumerate(ma_periods):
        if price_col not in df.columns:
            print(f"警告: DataFrame中没有'{price_col}'列，跳过均线计算。")
            continue

        df[price_col] = pd.to_numeric(df[price_col], errors='coerce')
        ma_data = df[price_col].rolling(window=period).mean()
        color = ma_colors[i % len(ma_colors)] 

        traces.append(
            go.Scatter(
                x=df[date_col],
                y=ma_data,
                mode='lines',
                name=f'{period}日均线 ({price_col})',
                line=dict(color=color, width=2),
                xaxis='x' # 均线在主图（x轴）上
            )
        )
    return traces

# --- 封装净卡路里柱状图生成函数 (主要修改这里) ---
def create_net_calorie_volume_trace(df, date_col, intake_col, burn_col):
    """
    生成 Plotly 净卡路里柱状图轨迹。
    柱子颜色表示净盈余 (绿色) 或净亏空 (红色)。

    参数:
    df (pd.DataFrame): 包含日期和卡路里数据的DataFrame。
    date_col (str): 日期列的名称。
    intake_col (str): 摄入卡路里列的名称。
    burn_col (str): 消耗卡路里列的名称。

    返回:
    go.Bar: 净卡路里柱状图轨迹对象。
    """
    # 确保卡路里数据是数值类型
    df[intake_col] = pd.to_numeric(df[intake_col], errors='coerce')
    df[burn_col] = pd.to_numeric(df[burn_col], errors='coerce')

    # 计算净卡路里：摄入 - 消耗
    net_calories = df[intake_col] - df[burn_col]

    # 根据净卡路里值设置柱子的颜色
    bar_colors = ['green' if val >= 0 else 'red' for val in net_calories]

    return go.Bar(
        x=df[date_col],
        y=net_calories,
        name='净卡路里',
        marker_color=bar_colors, # 根据每个柱子的值动态设置颜色
        xaxis='x' # 将这个 Bar 轨迹的 x 轴关联到主图的共享 x 轴
    )


# --- 绘图函数 (概念一：每日全范围波动 + 净卡路里) ---
def plot_weight_candlestick_daily_full_range_with_volume(data, ma_configs=None, show_calorie_volume=True,show = True,
                                                        file_path = "tests/resources/interactive_bar_chart.html"):
    """
    使用 Plotly 绘制体重数据的蜡烛图，包含每日最高/最低体重，均线，以及可选的净卡路里量。
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError("输入数据必须是 pandas DataFrame。")
    required_cols = ['Date', 'MorningWeight', 'EveningWeight', 'DailyHighestWeight', 'DailyLowestWeight']
    if not all(col in data.columns for col in required_cols):
        raise ValueError(f"DataFrame 必须包含 {required_cols} 列。")
    
    if show_calorie_volume:
        calorie_cols = ['CalorieIntake', 'CalorieBurn']
        if not all(col in data.columns for col in calorie_cols):
            print("警告: 缺少卡路里数据列，将不显示净卡路里成交量。")
            show_calorie_volume = False

    data['Date'] = pd.to_datetime(data['Date'])
    data = data.sort_values('Date')

    # 创建子图布局
    # rows: 主图一行，净卡路里一行
    specs = [[{"secondary_y": False}], [{"secondary_y": False}]] if show_calorie_volume else [[{"secondary_y": False}]]
    fig = make_subplots(rows=2 if show_calorie_volume else 1, 
                        cols=1, 
                        shared_xaxes=True, # 共享X轴，实现缩放平移同步
                        vertical_spacing=0.05,
                        row_heights=[0.7, 0.3] if show_calorie_volume else [1.0])

    # 1. 添加蜡烛图 (到第一个子图)
    fig.add_trace(go.Candlestick(
        x=data['Date'],
        open=data['MorningWeight'],
        high=data['DailyHighestWeight'],
        low=data['DailyLowestWeight'],
        close=data['EveningWeight'],
        increasing_line_color='green',
        decreasing_line_color='red',
        name='每日体重波动'
    ), row=1, col=1)

    # 2. 添加均线 (到第一个子图)
    if ma_configs:
        for config in ma_configs:
            period = config.get('period')
            price_col = config.get('price_col')
            color = config.get('color')
            if period and price_col:
                ma_traces = create_moving_average_trace(data, 'Date', price_col, [period], [color])
                for trace in ma_traces:
                    fig.add_trace(trace, row=1, col=1)

    # 3. 添加净卡路里柱状图 (到第二个子图)
    if show_calorie_volume:
        net_calorie_trace = create_net_calorie_volume_trace(data, 'Date', 'CalorieIntake', 'CalorieBurn')
        fig.add_trace(net_calorie_trace, row=2, col=1)

        # 更新第二行的Y轴标题
        fig.update_yaxes(title_text='净卡路里 (千卡)', row=2, col=1, title_font=dict(size=10))
        # 隐藏第二行Y轴刻度标签
        # fig.update_yaxes(showticklabels=False, row=2, col=1) # 净卡路里有正负，刻度显示可能更清晰
        # 调整净卡路里Y轴的范围，使其居中
        max_abs_cal = max(abs(net_calorie_trace.y.min()), abs(net_calorie_trace.y.max()))
        fig.update_yaxes(range=[-max_abs_cal * 1.1, max_abs_cal * 1.1], row=2, col=1) # 留出一点边距
        fig.update_xaxes(row=2, col=1, title_text='日期')


    # 更新布局
    ma_titles = []
    if ma_configs:
        for config in ma_configs:
            if 'period' in config and 'price_col' in config:
                ma_titles.append(f"{config['period']}日({config['price_col']})")
    title_suffix = f"及 {', '.join(ma_titles)}均线" if ma_titles else ""
    
    fig.update_layout(
        title=f'每日体重波动蜡烛图 (含全天最高最低) {title_suffix}',
        yaxis_title='体重 (斤)',
        xaxis_title='日期',
        xaxis_rangeslider_visible=False, # 移除了主图的范围选择器，由底部的子图提供
        hovermode="x unified",
        height=700, # 调整图表高度
        xaxis=dict(rangeslider=dict(visible=False)), # 确保主图x轴不显示rangeslider
        xaxis2=dict(rangeslider=dict(visible=True), type="date") if show_calorie_volume else None # 净卡路里子图的x轴显示rangeslider
    )

    # 隐藏主图X轴的日期标签，只在底部子图显示
    fig.update_xaxes(showticklabels=False, row=1, col=1)

    if show:
        fig.show()
    else:
        # print("图表已保存为 scatter_plot.png (使用 pio.write_image)")
        # fig.write_image(
        #     "tests/resources/scatter_plot2.png",
        #     format="png",          # 可以显式指定格式，默认为根据文件名后缀判断
        #     width=1800,             # 设置图片宽度（像素）
        #     height=1600,            # 设置图片高度（像素）
        #     scale=2                # 放大倍数，用于提高分辨率，例如 2 倍分辨率
        #     )
        fig.write_html(
            file_path,
            include_plotlyjs="cdn",  # 将 Plotly.js 库通过 CDN 引入
            full_html=True,          # 生成完整的 HTML 文件 (包含 <head>, <body> 等)
            default_width="80%",     # 设置默认宽度
            default_height=500       # 设置默认高度
        )
# output.svg