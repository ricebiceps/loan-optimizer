from dash import Dash, Input, Output, dcc, html, State
import dash_bootstrap_components as dbc
from authentication import login_page
from dashboard import dashboard_page
from frontend.callback import register_callbacks

# Initialize the Dash app
app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.DARKLY])
app.title = "Loan Allocation Optimizer"

register_callbacks(app)

# Initial route: login page
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="page-content")
])

# Callbacks for navigation
@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def display_page(pathname):
    if pathname == "/dashboard":
        return dashboard_page()
    else:  # Default to login
        return login_page()

@app.callback(
    [Output("url", "pathname"),  # To navigate to the dashboard
     Output("login-alert", "is_open")],  # To show/hide the login error
    [Input("login-button", "n_clicks")],  # Login button click
    [State("username", "value"),  # Username input value
     State("password", "value")],  # Password input value
    prevent_initial_call=True
)
def login(n_clicks, username, password):
    # Define valid credentials
    VALID_CREDENTIALS = {"admin": "admin", "user": "password"}

    # Only proceed if the username and password are not empty
    if username and password:
        if username in VALID_CREDENTIALS and VALID_CREDENTIALS[username] == password:
            return "/dashboard", False  # Redirect to dashboard and hide the alert
    return "/", True  # Stay on login page and show the alert

if __name__ == "__main__":
    app.run_server(debug=True)
