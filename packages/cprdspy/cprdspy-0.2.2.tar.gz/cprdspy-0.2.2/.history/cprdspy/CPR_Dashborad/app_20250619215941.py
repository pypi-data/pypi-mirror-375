"""
CPR可视化工具主应用

此模块提供了应用的主要入口点和路由控制。
支持通过命令行参数配置端口和数据目录。
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from dash import Dash, html, dcc, Input, Output, State
from dash.exceptions import PreventUpdate
from pages import waves, flowers

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("dash_app.log")],
)
logger = logging.getLogger(__name__)

# 解析命令行参数
parser = argparse.ArgumentParser(description="CPR可视化工具")
parser.add_argument("--port", type=int, default=8050, help="服务器端口号")
parser.add_argument("--data-dir", type=str, default="data", help="数据目录路径")
args = parser.parse_args()

# 确保数据目录存在
data_dir = Path(args.data_dir)
data_dir.mkdir(parents=True, exist_ok=True)
logger.info(f"数据目录: {data_dir}")

# 创建Dash应用
app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    update_title="更新中...",
    title="CPR可视化工具",
)

# 配置应用
app.config.suppress_callback_exceptions = True


# 文件列表组件
def file_list_component():
    files = []
    try:
        for file_path in data_dir.glob("*.csv"):
            files.append(
                {
                    "name": file_path.name,
                    "path": str(file_path),
                    "size": file_path.stat().st_size,
                    "date": file_path.stat().st_mtime,
                }
            )
    except Exception as e:
        logger.error(f"读取文件列表错误: {e}")

    return html.Div(
        [
            html.H3("数据文件", style={"marginBottom": "15px"}),
            html.Div(
                [
                    html.Button(
                        "刷新列表",
                        id="refresh-file-list",
                        style={
                            "marginRight": "10px",
                            "padding": "5px 10px",
                            "backgroundColor": "#607D8B",
                            "color": "white",
                            "border": "none",
                            "borderRadius": "4px",
                        },
                    ),
                    dcc.Upload(
                        id="upload-data",
                        children=html.Button(
                            "上传文件",
                            style={
                                "padding": "5px 10px",
                                "backgroundColor": "#FF9800",
                                "color": "white",
                                "border": "none",
                                "borderRadius": "4px",
                            },
                        ),
                        multiple=True,
                    ),
                ],
                style={"marginBottom": "15px", "display": "flex"},
            ),
            html.Div(
                id="file-list-container",
                children=[
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span(
                                        file["name"], style={"fontWeight": "bold"}
                                    ),
                                    html.Span(
                                        f" ({round(file['size']/1024, 1)} KB)",
                                        style={"color": "#757575", "fontSize": "0.9em"},
                                    ),
                                ],
                                style={"flex": "1"},
                            ),
                            html.Div(
                                [
                                    html.Button(
                                        "加载",
                                        id={"type": "load-file", "index": i},
                                        style={
                                            "marginRight": "5px",
                                            "padding": "3px 8px",
                                            "backgroundColor": "#4CAF50",
                                            "color": "white",
                                            "border": "none",
                                            "borderRadius": "3px",
                                            "fontSize": "0.9em",
                                        },
                                    ),
                                    html.Button(
                                        "删除",
                                        id={"type": "delete-file", "index": i},
                                        style={
                                            "padding": "3px 8px",
                                            "backgroundColor": "#F44336",
                                            "color": "white",
                                            "border": "none",
                                            "borderRadius": "3px",
                                            "fontSize": "0.9em",
                                        },
                                    ),
                                ]
                            ),
                        ],
                        style={
                            "display": "flex",
                            "justifyContent": "space-between",
                            "alignItems": "center",
                            "padding": "10px",
                            "margin": "5px 0",
                            "backgroundColor": "#f5f5f5",
                            "borderRadius": "5px",
                            "boxShadow": "0 1px 3px rgba(0,0,0,0.1)",
                        },
                        id={"type": "file-item", "index": i},
                    )
                    for i, file in enumerate(files)
                ],
                style={"maxHeight": "300px", "overflowY": "auto"},
            ),
            # 存储文件数据
            dcc.Store(
                id="file-data-store",
                data=[{"path": file["path"], "name": file["name"]} for file in files],
            ),
            # 通知区域
            html.Div(
                id="notification-area", style={"marginTop": "10px", "color": "#FF5722"}
            ),
        ],
        style={
            "padding": "15px",
            "backgroundColor": "white",
            "borderRadius": "8px",
            "boxShadow": "0 2px 5px rgba(0,0,0,0.1)",
        },
    )


# 主页布局
def home_layout():
    return html.Div(
        [
            html.Div(
                [
                    html.H1(
                        "CPR波形可视化工具",
                        style={"textAlign": "center", "marginBottom": "30px"},
                    ),
                    # 文件管理区域
                    html.Div([file_list_component()], style={"marginBottom": "30px"}),
                    # 功能导航区域
                    html.Div(
                        [
                            dcc.Link(
                                html.Button(
                                    [
                                        html.I(
                                            className="fas fa-wave-square",
                                            style={"marginRight": "10px"},
                                        ),
                                        "波形可视化",
                                    ],
                                    className="nav-button",
                                    style={
                                        "fontSize": "16px",
                                        "padding": "12px 25px",
                                        "margin": "10px",
                                        "backgroundColor": "#4CAF50",
                                        "color": "white",
                                        "border": "none",
                                        "borderRadius": "5px",
                                        "cursor": "pointer",
                                        "transition": "all 0.3s",
                                        "display": "flex",
                                        "alignItems": "center",
                                        "justifyContent": "center",
                                        "width": "180px",
                                    },
                                ),
                                href="/waves",
                            ),
                            dcc.Link(
                                html.Button(
                                    [
                                        html.I(
                                            className="fas fa-spa",
                                            style={"marginRight": "10px"},
                                        ),
                                        "花朵可视化",
                                    ],
                                    className="nav-button",
                                    style={
                                        "fontSize": "16px",
                                        "padding": "12px 25px",
                                        "margin": "10px",
                                        "backgroundColor": "#2196F3",
                                        "color": "white",
                                        "border": "none",
                                        "borderRadius": "5px",
                                        "cursor": "pointer",
                                        "transition": "all 0.3s",
                                        "display": "flex",
                                        "alignItems": "center",
                                        "justifyContent": "center",
                                        "width": "180px",
                                    },
                                ),
                                href="/flowers",
                            ),
                        ],
                        style={
                            "display": "flex",
                            "justifyContent": "center",
                            "alignItems": "center",
                            "marginBottom": "30px",
                        },
                    ),
                    # 功能说明区域
                    html.Div(
                        [
                            html.H2(
                                "功能说明",
                                style={"textAlign": "center", "marginBottom": "20px"},
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H3(
                                                "波形可视化", style={"color": "#4CAF50"}
                                            ),
                                            html.P(
                                                "生成和可视化各种类型的波形，包括："
                                            ),
                                            html.Ul(
                                                [
                                                    html.Li("等差圆形波"),
                                                    html.Li("等比圆形波"),
                                                    html.Li(
                                                        "可调节振幅、频率、周期等参数"
                                                    ),
                                                ]
                                            ),
                                        ],
                                        style={
                                            "flex": "1",
                                            "margin": "10px",
                                            "padding": "15px",
                                            "backgroundColor": "#f5f5f5",
                                            "borderRadius": "8px",
                                            "boxShadow": "0 2px 4px rgba(0,0,0,0.05)",
                                        },
                                    ),
                                    html.Div(
                                        [
                                            html.H3(
                                                "花朵可视化", style={"color": "#2196F3"}
                                            ),
                                            html.P(
                                                "创建和可视化各种类型的花朵图案，包括："
                                            ),
                                            html.Ul(
                                                [
                                                    html.Li("基本花瓣和花弧"),
                                                    html.Li("单层和多层花朵"),
                                                    html.Li(
                                                        "可调节花瓣形状、数量、大小等参数"
                                                    ),
                                                ]
                                            ),
                                        ],
                                        style={
                                            "flex": "1",
                                            "margin": "10px",
                                            "padding": "15px",
                                            "backgroundColor": "#f5f5f5",
                                            "borderRadius": "8px",
                                            "boxShadow": "0 2px 4px rgba(0,0,0,0.05)",
                                        },
                                    ),
                                ],
                                style={
                                    "display": "flex",
                                    "justifyContent": "center",
                                    "maxWidth": "1000px",
                                    "margin": "0 auto",
                                },
                            ),
                        ]
                    ),
                ],
                style={"maxWidth": "1200px", "margin": "0 auto", "padding": "20px"},
            ),
            # 隐藏的元素，用于存储状态
            dcc.Store(id="current-file", data=None),
            dcc.Store(id="app-state", data={"theme": "light"}),
        ]
    )


# 应用布局
app.layout = html.Div(
    [
        # 导航栏
        html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src="/assets/logo.png",
                            height="30px",
                            style={"marginRight": "10px"},
                        ),
                        html.Span(
                            "CPR波形可视化",
                            style={"fontSize": "18px", "fontWeight": "bold"},
                        ),
                    ],
                    style={"display": "flex", "alignItems": "center"},
                ),
                html.Div(
                    [
                        dcc.Link(
                            html.Button("首页", className="nav-link"),
                            href="/",
                            style={"marginRight": "15px"},
                        ),
                        dcc.Link(
                            html.Button("波形", className="nav-link"),
                            href="/waves",
                            style={"marginRight": "15px"},
                        ),
                        dcc.Link(
                            html.Button("花朵", className="nav-link"),
                            href="/flowers",
                            style={"marginRight": "15px"},
                        ),
                    ],
                    style={"display": "flex", "alignItems": "center"},
                ),
            ],
            style={
                "display": "flex",
                "justifyContent": "space-between",
                "padding": "10px 20px",
                "backgroundColor": "#f8f9fa",
                "borderBottom": "1px solid #e9ecef",
                "marginBottom": "20px",
            },
        ),
        # 主内容区域
        dcc.Location(id="url", refresh=False),
        html.Div(id="page-content"),
    ],
    style={"fontFamily": "Arial, sans-serif"},
)


# 页面路由回调
@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    if pathname == "/waves":
        return waves.layout
    elif pathname == "/flowers":
        return flowers.layout
    else:
        return home_layout()


# 添加CSS样式
app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>CPR可视化工具</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #ffffff;
            }
            .nav-button:hover {
                opacity: 0.9;
                transform: scale(1.05);
            }
            ul {
                padding-left: 20px;
            }
            li {
                margin: 10px 0;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)
