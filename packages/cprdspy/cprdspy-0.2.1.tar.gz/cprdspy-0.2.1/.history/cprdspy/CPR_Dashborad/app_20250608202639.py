# app.py
from dash import Dash, html, dcc
from werkzeug.exceptions import NotFound
from dash_router import Router
import app_waves
import app_flowers

# 创建Dash应用
app = Dash(__name__)
router = Router(app)


# 主页布局
def home_layout():
    return html.Div(
        [
            html.H1("CPR可视化工具", style={"textAlign": "center"}),
            html.Div(
                [
                    dcc.Link(
                        html.Button("波形可视化", className="nav-button"),
                        href="/waves",
                        style={"margin": "10px"},
                    ),
                    dcc.Link(
                        html.Button("花朵可视化", className="nav-button"),
                        href="/flowers",
                        style={"margin": "10px"},
                    ),
                ],
                style={"display": "flex", "justifyContent": "center", "margin": "20px"},
            ),
        ]
    )


# 添加路由
router.add_route("/", home_layout)  # 主页路由
router.add_route("/waves", app_waves.layout)  # 波形页面
router.add_route("/flowers", app_flowers.layout)  # 花朵页面

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
            .nav-button {
                padding: 10px 20px;
                font-size: 16px;
                cursor: pointer;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                transition: background-color 0.3s;
            }
            .nav-button:hover {
                background-color: #45a049;
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
    app.run_server(debug=True)
