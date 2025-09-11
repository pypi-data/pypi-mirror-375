# run_app.py
from app import app

if __name__ == "__main__":
    print("启动CPR可视化工具...")
    print("请在浏览器中访问: http://127.0.0.1:8050/")
    app.run_server(debug=True)
