from dash import dcc, html
import dash_bootstrap_components as dbc

def login_page():
    return dbc.Container([
        dbc.Row(
            dbc.Col(html.H1("Login", className="text-center mt-4 mb-4")),
            justify="center"
        ),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Enter your credentials")),
                    dbc.CardBody([
                        dbc.Input(id="username", placeholder="Username", type="text", className="mb-3"),
                        dbc.Input(id="password", placeholder="Password", type="password", className="mb-3"),
                        dbc.Button("Login", id="login-button", color="primary", className="mt-2", n_clicks=0),
                        dbc.Alert("Please enter the correct credentials.", id="login-alert", is_open=False, color="warning", className="mt-2")
                    ]),
                ], className="mt-4"),
            ], width=4)
        ], justify="center"),
    ], fluid=True)
