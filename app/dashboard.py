from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc

def dashboard_page():
    return dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("Loan Allocation Dashboard", className="text-center mt-4 mb-4"))
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Upload Loan File")),
                    dbc.CardBody([
                        dcc.Upload(
                            id="upload-loan",
                            children=dbc.Button("Select Loan File", color="primary", className="mt-2"),
                            style={"width": "100%"},
                        ),
                        dbc.Alert("Loan file uploaded successfully!", id="loan-upload-alert", is_open=False, color="success", className="mt-2")
                    ]),
                ], className="mb-4"),
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Upload Facility File")),
                    dbc.CardBody([
                        dcc.Upload(
                            id="upload-facility",
                            children=dbc.Button("Select Facility File", color="primary", className="mt-2"),
                            style={"width": "100%"},
                        ),
                        dbc.Alert("Facility file uploaded successfully!", id="facility-upload-alert", is_open=False, color="success", className="mt-2")
                    ]),
                ], className="mb-4"),
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Upload Order File")),
                    dbc.CardBody([
                        dcc.Upload(
                            id="upload-order",
                            children=dbc.Button("Select Order File", color="primary", className="mt-2"),
                            style={"width": "100%"},
                        ),
                        dbc.Alert("Order file uploaded successfully!", id="order-upload-alert", is_open=False, color="success", className="mt-2")
                    ]),
                ], className="mb-4"),
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Upload Existing Loans File")),
                    dbc.CardBody([
                        dcc.Upload(
                            id="upload-existing-loans",
                            children=dbc.Button("Select Existing Loans File", color="primary", className="mt-2"),
                            style={"width": "100%"},
                        ),
                        dbc.Alert("Existing loans file uploaded successfully!", id="existing-loans-upload-alert", is_open=False, color="success", className="mt-2")
                    ]),
                ], className="mb-4"),
            ], width=3),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.H5("Total Loans", className="card-title text-center"),
                        html.H3(id="total-loans", className="card-text text-center text-primary"),
                    ]),
                )
            ], width=2),
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.H5("Total Facilities", className="card-title text-center"),
                        html.H3(id="total-facilities", className="card-text text-center text-primary"),
                    ]),
                )
            ], width=2),
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.H5("Total Value Assigned", className="card-title text-center"),
                        html.H3(id="total-value-assigned", className="card-text text-center text-success"),
                    ]),
                )
            ], width=3),
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.H5("Average Credit Score", className="card-title text-center"),
                        html.H3(id="average-credit-score", className="card-text text-center text-warning"),
                    ]),
                )
            ], width=3),
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.H5("Total New Loans Assigned", className="card-title text-center"),
                        html.H3(id="total-new-loans", className="card-text text-center text-info"),
                    ]),
                )
            ], width=2),
        ], className="mb-4"),
        dbc.Row([
            dbc.Col([
                dbc.Alert(id="upload-alert", is_open=False, duration=4000),
                dbc.Spinner(html.Div(id="processing-spinner"), size="lg", color="primary"),
                html.H2("Facility-Specific Metrics", className="text-center mt-4", style={"color": "white"}),
                html.Div(
                    dash_table.DataTable(
                        id="data-table",
                        data=[],  # Initially, no data
                        columns=[],  # Columns will be dynamically updated
                        style_header={
                            "backgroundColor": "#333",  # Dark header background
                            "fontWeight": "bold",
                            "color": "#EAEAEA",  # Header text color
                            "textAlign": "center",
                            "maxHeight": "60px", "minHeight": "60px", "height": "60px",
                        },
                        style_cell={
                            "textAlign": "center",
                            "color": "#EAEAEA",  # Table text color
                            "backgroundColor": "#222",  # Cell background
                            "padding": "10px",
                            "border": "1px solid #444",
                            "whiteSpace": "normal",  # Ensure text wraps
                        },
                        fixed_rows={"headers": True},
                        style_data_conditional=[
                            {"if": {"row_index": "odd"}, "backgroundColor": "#2A2A2A"},
                        ],
                    ),
                    style={"height": "600px","overflowY": "scroll", 'padding': '10px 10px 10px 20px',},  # Restrict container height
                ),
            ], width=12),
        ]),
        dbc.Row([
            dbc.Col([
            dcc.Graph(id="visualization-1")  # Placeholder for traditional stacked bar chart
        ], width=6),
        dbc.Col([
        dcc.Graph(id="visualization-2")  # Placeholder for utilization stacked bar chart
        ], width=6),
    ]),
    dbc.Row(
            dbc.Col(
                html.Div(style={"height": "100px"}),  # Dummy element to extend page height
            )
        ),
        dbc.Row([
            dbc.Col([
                dbc.Button("Download Allocation Data", id="download-button", color="primary", className="mt-4"),
                dcc.Download(id="download-csv")  # Component to handle file download
            ], width=12, className="text-center"),
        ]),

        dbc.Row(
            dbc.Col(
                html.Div(style={"height": "100px"}),  # Dummy element to extend page height
            )
        ),

    ], fluid=True, style={"overflowY": "auto", "height": "100vh", "paddingBottom": "100px"})  # Allow full-page scrolling
