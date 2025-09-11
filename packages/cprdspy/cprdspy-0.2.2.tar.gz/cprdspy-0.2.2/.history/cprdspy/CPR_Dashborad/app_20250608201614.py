# app.py
from dash import Dash
from dash_router import Router

app = Dash(__name__)
router = Router(app)

router.add_route("/waves", app_waves.layout)
router.add_route("/flowers", app_flowers.layout)
