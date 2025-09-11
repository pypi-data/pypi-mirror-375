"""
花朵可视化页面
"""

import pandas as pd
import plotly.graph_objects as go
from dash import html, dcc, callback, Input, Output, State
import numpy as np


def layout():
    """花朵可视化页面布局"""
    return html.Div(
        [
            # 页面标题
            html.Div(
                [
                    html.H2("CPR花朵图分析", style={"margin": "0", "color": "#2c3e50"}),
                    html.P(
                        "通过花朵图可视化CPR质量",
                        style={"color": "#7f8c8d", "marginTop": "5px"},
                    ),
                ],
                style={
                    "marginBottom": "20px",
                    "borderBottom": "1px solid #ecf0f1",
                    "paddingBottom": "10px",
                },
            ),
            # 控制面板
            html.Div(
                [
                    html.Div(
                        [
                            html.Label(
                                "选择数据文件",
                                style={"fontWeight": "bold", "marginBottom": "5px"},
                            ),
                            dcc.Dropdown(
                                id="flower-file-dropdown",
                                placeholder="选择CSV文件",
                                style={"width": "100%"},
                            ),
                        ],
                        style={"flex": "1", "marginRight": "10px"},
                    ),
                    html.Div(
                        [
                            html.Label(
                                "选择时间段",
                                style={"fontWeight": "bold", "marginBottom": "5px"},
                            ),
                            dcc.RangeSlider(
                                id="flower-time-range-slider",
                                min=0,
                                max=100,
                                step=1,
                                value=[0, 100],
                                marks=None,
                                tooltip={"placement": "bottom", "always_visible": True},
                            ),
                        ],
                        style={"flex": "2"},
                    ),
                ],
                style={"display": "flex", "marginBottom": "20px"},
            ),
            # 花朵图表
            html.Div(
                [
                    dcc.Graph(
                        id="flower-graph", figure=go.Figure(), style={"height": "500px"}
                    )
                ],
                style={
                    "backgroundColor": "#ffffff",
                    "padding": "15px",
                    "borderRadius": "8px",
                    "boxShadow": "0 2px 5px rgba(0,0,0,0.05)",
                },
            ),
            # 花朵分析结果
            html.Div(
                [
                    html.H3("花朵分析", style={"marginTop": "20px"}),
                    html.Div(id="flower-analysis-results", style={"marginTop": "10px"}),
                ]
            ),
            # 隐藏的数据存储
            dcc.Store(id="flower-data-store"),
        ],
        style={"padding": "20px"},
    )


@callback(Output("flower-file-dropdown", "options"), Input("file-data-store", "data"))
def update_file_dropdown(file_data):
    """更新文件下拉列表"""
    if not file_data:
        return []

    options = [{"label": file["name"], "value": file["path"]} for file in file_data]
    return options


@callback(
    [
        Output("flower-data-store", "data"),
        Output("flower-time-range-slider", "min"),
        Output("flower-time-range-slider", "max"),
        Output("flower-time-range-slider", "value"),
        Output("flower-time-range-slider", "marks"),
    ],
    Input("flower-file-dropdown", "value"),
    prevent_initial_call=True,
)
def load_flower_data(file_path):
    """加载花朵数据"""
    if not file_path:
        raise PreventUpdate

    try:
        # 加载CSV文件
        df = pd.read_csv(file_path)

        # 确保数据包含必要的列
        required_cols = ["time", "depth"]
        if not all(col in df.columns for col in required_cols):
            return None, 0, 100, [0, 100], {}

        # 准备时间范围滑块
        time_min = df["time"].min()
        time_max = df["time"].max()

        # 创建标记点
        marks = {i: f"{i:.1f}s" for i in np.linspace(time_min, time_max, 5)}

        # 返回数据和滑块设置
        return df.to_dict("records"), time_min, time_max, [time_min, time_max], marks

    except Exception as e:
        print(f"加载花朵数据错误: {e}")
        return None, 0, 100, [0, 100], {}


@callback(
    [Output("flower-graph", "figure"), Output("flower-analysis-results", "children")],
    [Input("flower-data-store", "data"), Input("flower-time-range-slider", "value")],
    prevent_initial_call=True,
)
def update_flower_graph(data, time_range):
    """更新花朵图表"""
    if not data or not time_range:
        raise PreventUpdate

    try:
        # 转换为DataFrame
        df = pd.DataFrame(data)

        # 过滤时间范围
        filtered_df = df[(df["time"] >= time_range[0]) & (df["time"] <= time_range[1])]

        # 创建花朵图
        fig = create_flower_plot(filtered_df)

        # 分析花朵数据
        analysis_results = analyze_flower_data(filtered_df)

        return fig, analysis_results

    except Exception as e:
        print(f"更新花朵图表错误: {e}")
        return go.Figure(), html.Div("数据处理错误，请检查文件格式")


def create_flower_plot(df):
    """创建花朵图"""
    try:
        # 提取深度和速度数据
        if "depth" not in df.columns:
            return go.Figure()

        # 计算速度（如果不存在）
        if "velocity" not in df.columns and len(df) > 1:
            df["velocity"] = df["depth"].diff() / df["time"].diff()

        # 找到按压周期
        cycles = []
        in_compression = False
        cycle_start = 0

        for i in range(len(df)):
            if not in_compression and df["depth"].iloc[i] > 5:  # 开始按压
                in_compression = True
                cycle_start = i
            elif in_compression and df["depth"].iloc[i] < 5:  # 结束按压
                in_compression = False
                if i - cycle_start > 3:  # 确保周期有足够的点
                    cycles.append(df.iloc[cycle_start:i])

        # 创建花朵图
        fig = go.Figure()

        # 为每个周期创建一个轨迹
        for i, cycle in enumerate(cycles):
            if len(cycle) < 4:  # 跳过太短的周期
                continue

            # 如果有速度数据，使用深度-速度图
            if "velocity" in cycle.columns:
                fig.add_trace(
                    go.Scatter(
                        x=cycle["depth"],
                        y=cycle["velocity"],
                        mode="lines",
                        name=f"周期 {i+1}",
                        line=dict(
                            width=1,
                            color=f"rgba(31, 119, 180, {0.3 + 0.7*i/len(cycles)})",
                        ),
                    )
                )
            # 否则使用深度-时间图
            else:
                relative_time = cycle["time"] - cycle["time"].iloc[0]
                fig.add_trace(
                    go.Scatter(
                        x=cycle["depth"],
                        y=relative_time,
                        mode="lines",
                        name=f"周期 {i+1}",
                        line=dict(
                            width=1,
                            color=f"rgba(31, 119, 180, {0.3 + 0.7*i/len(cycles)})",
                        ),
                    )
                )

        # 添加理想区域
        if "velocity" in df.columns:
            # 深度-速度图的理想区域
            ideal_depth = [50, 60, 60, 50, 50]
            ideal_velocity = [-400, -400, 400, 400, -400]

            fig.add_trace(
                go.Scatter(
                    x=ideal_depth,
                    y=ideal_velocity,
                    fill="toself",
                    mode="lines",
                    name="理想区域",
                    line=dict(color="rgba(0, 200, 0, 0.2)"),
                    fillcolor="rgba(0, 200, 0, 0.1)",
                )
            )

            # 更新布局
            fig.update_layout(
                title="CPR花朵图 (深度-速度)",
                xaxis_title="深度 (mm)",
                yaxis_title="速度 (mm/s)",
            )
        else:
            # 深度-时间图没有明确的理想区域
            fig.update_layout(
                title="CPR花朵图 (深度-时间)",
                xaxis_title="深度 (mm)",
                yaxis_title="相对时间 (s)",
            )

        # 更新布局
        fig.update_layout(
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
            margin=dict(l=40, r=40, t=40, b=40),
            hovermode="closest",
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family="Arial", size=12, color="#2c3e50"),
        )

        # 添加网格线
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="#ecf0f1")
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="#ecf0f1")

        return fig

    except Exception as e:
        print(f"创建花朵图错误: {e}")
        return go.Figure()


def analyze_flower_data(df):
    """分析花朵数据"""
    try:
        # 计算基本统计数据
        avg_depth = df["depth"].mean()
        max_depth = df["depth"].max()

        # 计算按压频率
        if len(df) > 1:
            time_diff = df["time"].iloc[-1] - df["time"].iloc[0]
            if time_diff > 0:
                # 找到波峰数量（简单方法：寻找局部最大值）
                peaks = 0
                for i in range(1, len(df) - 1):
                    if (
                        df["depth"].iloc[i] > df["depth"].iloc[i - 1]
                        and df["depth"].iloc[i] > df["depth"].iloc[i + 1]
                    ):
                        peaks += 1

                # 计算频率（每分钟按压次数）
                frequency = (peaks / time_diff) * 60
            else:
                frequency = 0
        else:
            frequency = 0

        # 计算完全释放百分比
        if len(df) > 0:
            release_points = df[df["depth"] < 5]
            release_percentage = (len(release_points) / len(df)) * 100
        else:
            release_percentage = 0

        # 创建分析结果显示
        return html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.H4("花朵一致性"),
                                html.P(
                                    calculate_consistency_score(df),
                                    style={
                                        "fontSize": "24px",
                                        "fontWeight": "bold",
                                        "color": "#3498db",
                                    },
                                ),
                            ],
                            className="feature-card",
                            style={
                                "flex": "1",
                                "padding": "15px",
                                "backgroundColor": "#f8f9fa",
                                "borderRadius": "8px",
                                "margin": "5px",
                                "textAlign": "center",
                            },
                        ),
                        html.Div(
                            [
                                html.H4("完全释放率"),
                                html.P(
                                    f"{release_percentage:.1f}%",
                                    style={
                                        "fontSize": "24px",
                                        "fontWeight": "bold",
                                        "color": "#2ecc71",
                                    },
                                ),
                            ],
                            className="feature-card",
                            style={
                                "flex": "1",
                                "padding": "15px",
                                "backgroundColor": "#f8f9fa",
                                "borderRadius": "8px",
                                "margin": "5px",
                                "textAlign": "center",
                            },
                        ),
                        html.Div(
                            [
                                html.H4("按压频率"),
                                html.P(
                                    f"{frequency:.1f} 次/分钟",
                                    style={
                                        "fontSize": "24px",
                                        "fontWeight": "bold",
                                        "color": "#e74c3c",
                                    },
                                ),
                            ],
                            className="feature-card",
                            style={
                                "flex": "1",
                                "padding": "15px",
                                "backgroundColor": "#f8f9fa",
                                "borderRadius": "8px",
                                "margin": "5px",
                                "textAlign": "center",
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "justifyContent": "space-between",
                        "marginBottom": "15px",
                    },
                ),
                html.Div(
                    [
                        html.H4("质量评估"),
                        html.P(
                            [
                                "花朵图显示了CPR按压的质量和一致性。理想的花朵图应该有规则的形状，表明按压深度和速度的一致性。",
                                html.Br(),
                                html.Br(),
                                "当前数据分析结果：",
                                html.Br(),
                                html.Span("• 按压深度: ", style={"fontWeight": "bold"}),
                                f"{avg_depth:.1f} mm ",
                                html.Span(
                                    "(理想: 50-60 mm)",
                                    style={
                                        "color": (
                                            "green"
                                            if 50 <= avg_depth <= 60
                                            else "orange"
                                        )
                                    },
                                ),
                                html.Br(),
                                html.Span("• 按压频率: ", style={"fontWeight": "bold"}),
                                f"{frequency:.1f} 次/分钟 ",
                                html.Span(
                                    "(理想: 100-120 次/分钟)",
                                    style={
                                        "color": (
                                            "green"
                                            if 100 <= frequency <= 120
                                            else "orange"
                                        )
                                    },
                                ),
                                html.Br(),
                                html.Span("• 完全释放: ", style={"fontWeight": "bold"}),
                                f"{release_percentage:.1f}% ",
                                html.Span(
                                    "(理想: >90%)",
                                    style={
                                        "color": (
                                            "green"
                                            if release_percentage > 90
                                            else "orange"
                                        )
                                    },
                                ),
                            ]
                        ),
                    ],
                    style={
                        "padding": "15px",
                        "backgroundColor": "#f8f9fa",
                        "borderRadius": "8px",
                    },
                ),
            ]
        )

    except Exception as e:
        print(f"分析花朵数据错误: {e}")
        return html.Div("无法分析数据")


def calculate_consistency_score(df):
    """计算按压一致性得分"""
    try:
        if len(df) < 10:
            return "数据不足"

        # 计算深度的标准差
        depth_std = df["depth"].std()

        # 计算频率的一致性
        # 找到所有按压周期
        cycles = []
        in_compression = False
        cycle_start = 0

        for i in range(len(df)):
            if not in_compression and df["depth"].iloc[i] > 5:  # 开始按压
                in_compression = True
                cycle_start = i
            elif in_compression and df["depth"].iloc[i] < 5:  # 结束按压
                in_compression = False
                if i - cycle_start > 3:  # 确保周期有足够的点
                    cycles.append((cycle_start, i))

        # 计算周期时间的标准差
        if len(cycles) > 1:
            cycle_times = []
            for i in range(len(cycles) - 1):
                start_time = df["time"].iloc[cycles[i][0]]
                next_start_time = df["time"].iloc[cycles[i + 1][0]]
                cycle_times.append(next_start_time - start_time)

            cycle_time_std = np.std(cycle_times) if cycle_times else 0

            # 计算一致性得分 (0-100)
            depth_score = max(0, 100 - depth_std * 10)  # 深度标准差越小越好
            time_score = max(0, 100 - cycle_time_std * 100)  # 周期时间标准差越小越好

            # 综合得分
            consistency_score = int((depth_score + time_score) / 2)

            return f"{consistency_score}/100"
        else:
            return "数据不足"

    except Exception as e:
        print(f"计算一致性得分错误: {e}")
        return "计算错误"
