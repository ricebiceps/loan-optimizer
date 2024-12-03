import os
import base64
import numpy as np
import pandas as pd
from dash import Input, Output, no_update, Dash, dcc
import dash_bootstrap_components as dbc
from backend.facility_creation import create_facilities_from_config
from backend.optimization import run_optimization_process
from backend.models import Loan
import plotly.graph_objects as go


# Path for saving uploaded files
UPLOAD_DIRECTORY = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../uploads")

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

CALLBACKS_REGISTERED = False

def save_file(name, content):
    """Decode and store a file uploaded via Dash."""
    data = content.split(",")[1]
    decoded = base64.b64decode(data)
    save_path = os.path.join(UPLOAD_DIRECTORY, name)
    with open(save_path, "wb") as f:
        f.write(decoded)

    return save_path
def generate_visualizations(facility_metrics):
    # Data preparation
    facilities = facility_metrics['Facility']
    new_loans = facility_metrics['Value Filled (New)']
    total_loans = facility_metrics['Total Loans']
    total_value = facility_metrics['Total Value']
    facility_sizes = facility_metrics['Facility Size']

    # Deduce existing values and loans
    existing_loans = [total - new for total, new in zip(total_loans, new_loans)]
    existing_values = [total - new for total, new in zip(total_value, new_loans)]

    # Calculate unused capacity
    unused_capacity = [size - total for size, total in zip(facility_sizes, total_value)]

    # Calculate percentages for stacked bar chart (Utilization)
    total_budget = [exist + new + unused for exist, new, unused in zip(existing_values, new_loans, unused_capacity)]
    existing_percentage = [exist / total * 100 for exist, total in zip(existing_values, total_budget)]
    new_percentage = [new / total * 100 for new, total in zip(new_loans, total_budget)]
    unused_percentage = [unused / total * 100 for unused, total in zip(unused_capacity, total_budget)]

    # Traditional Stacked Bar Chart
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(name='Existing Loans', x=facilities, y=existing_values, marker=dict(color='gray')))
    fig1.add_trace(go.Bar(name='New Loans', x=facilities, y=new_loans, marker=dict(color='blue')))
    fig1.add_trace(go.Bar(name='Unused Capacity', x=facilities, y=unused_capacity, marker=dict(color='green')))
    fig1.update_layout(
        barmode='stack',
        title="Facility Budget Utilization by Loan Value",
        xaxis_title="Facility",
        yaxis_title="Dollar Value ($)",
        template="plotly_dark",
    )

    # Utilization Stacked Bar Chart
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(name='Existing Loans (%)', x=facilities, y=existing_percentage, marker=dict(color='gray')))
    fig2.add_trace(go.Bar(name='New Loans (%)', x=facilities, y=new_percentage, marker=dict(color='blue')))
    fig2.add_trace(go.Bar(name='Unused Capacity (%)', x=facilities, y=unused_percentage, marker=dict(color='green')))
    fig2.update_layout(
        barmode='stack',
        title="Facility Budget Utilization by Loan Type",
        xaxis_title="Facility",
        yaxis_title="Percentage of Facility Budget (%)",
        template="plotly_dark",
    )

    return fig1, fig2

def register_callbacks(app: Dash):
    global combined_df
    global CALLBACKS_REGISTERED  # Use the global flag
    if CALLBACKS_REGISTERED:
        return  # Skip registration if already registered
    
    @app.callback(
        [Output("data-table", "data"),
         Output("data-table", "columns"),
         Output("upload-alert", "children"),
         Output("upload-alert", "is_open"),
         Output("upload-alert", "color"),
         Output("processing-spinner", "children"),
         Output("total-loans", "children"),
         Output("total-facilities", "children"),
         Output("total-value-assigned", "children"),
         Output("total-new-loans", "children"),
         Output("average-credit-score", "children"),
         Output("visualization-1", "figure"),
         Output("visualization-2", "figure")
         ],
        [Input("upload-loan", "contents"),
         Input("upload-loan", "filename"),
         Input("upload-facility", "contents"),
         Input("upload-facility", "filename"),
         Input("upload-order", "contents"),
         Input("upload-order", "filename"),
         Input("upload-existing-loans", "contents"),
         Input("upload-existing-loans", "filename")],
        prevent_initial_call=True
    )
    def handle_upload(loan_content, loan_name, facility_content, facility_name, order_content, order_name, existing_loan_content, existing_loan_name):
        # If not all files are uploaded, return empty DataTable
        if not loan_content or not facility_content or not order_content or not existing_loan_content:
            return no_update, no_update, "Please upload all four files.", True, "warning", "", "", "", "", "", "", go.Figure(), go.Figure()
        spinner = dbc.Spinner(size="lg", color="primary")

        try:
            # Save uploaded files
            loan_path = save_file(loan_name, loan_content)
            facility_path = save_file(facility_name, facility_content)
            order_path = save_file(order_name, order_content)
            existing_loan_path = save_file(existing_loan_name, existing_loan_content)

            # Preprocess loan file as an example
            preprocessed_df = pd.read_csv(loan_path)
            pre_facility_df = pd.read_csv(facility_path)
            order_df = pd.read_csv(order_path)
            existing_loan_df = pd.read_csv(existing_loan_path)

            loans_to_assign = [Loan(**preprocessed_df.iloc[row]) for row in range(len(preprocessed_df))]

            facilities1 = create_facilities_from_config(pre_facility_df, existing_loan_df, preprocessed_df)

            facilities = []  # Initialize an empty list

            # Iterate through the dictionary's values and add them to the facilities list
            for key, value in facilities1.items():
                facilities.append(value)  # Append the value (facility) to the list

            # Matrix of loans x facilities compatibility
            asset_acc_matrix = np.zeros((len(loans_to_assign), len(facilities)))
           

            for i, loan in enumerate(loans_to_assign):
                for j, facility in enumerate(facilities):
                #existing_loans = pd.DataFrame([loan.__dict__ for loan in facility.existing_loans])
                    if facility.asset_check(loan):
                        asset_acc_matrix[i][j] = 1
            
            global combined_df
            results, facilities, combined_df = run_optimization_process(
                preprocessed_df, asset_acc_matrix,
                facilities,
                existing_loan_df,order_df
            )

            # Create facility-specific metrics
            final_assignments = results['assignments']

            # Calculate total loan value and average credit score
            assigned_loans = []
            for facility in facilities:
                assigned_loans.extend(facility.existing_loans)

            # Get total newly assigned loans and their metrics
            all_assigned_loans = []
            for facility in facilities:
                all_assigned_loans.extend(facility.existing_loans)

            # Create facility-specific metrics
            facility_data = []
            for i, facility in enumerate(facilities):
                # Count new assignments for this facility from the current run
                new_assignments = len([a for a in final_assignments if a[1] == i])
                new_value = sum(loans_to_assign[a[0]].orig_amt for a in final_assignments if a[1] == i)
    
                # Get total loans and values including historical assignments
                total_loans = len(facility.existing_loans)
                total_value = sum(loan.orig_amt for loan in facility.existing_loans)
    
                # Calculate average credit score
                facility_avg_score = (
                    sum(loan.CSCORE_B for loan in facility.existing_loans) / len(facility.existing_loans)
                    if facility.existing_loans else 0
                )

                facility_size = facility.facility_size
                facility_data.append({
                    'Facility ID': i,
                    'Facility': f'Facility {i+1}',
                    'Loans Assigned (New)': new_assignments,
                    'Value Filled (New)': new_value,
                    'Total Loans': total_loans,  # This includes historical + new
                    'Total Value': total_value,
                    'Average Credit Score': facility_avg_score,
                    'Facility Size': facility_size
                })

            # Create DataFrame
            facility_df = pd.DataFrame(facility_data)
            table_data = facility_df.to_dict("records")
            table_columns = [{"name": col, "id": col} for col in facility_df.columns]

            total_loans = len(all_assigned_loans)
            total_facilities = len(facilities)
            total_value_assigned = sum([facility['Total Value'] for facility in facility_data])
            total_new_loans = len(final_assignments)
            average_credit_score = sum([facility['Average Credit Score'] for facility in facility_data]) / len(facility_data)

            facility_metrics = pd.DataFrame(facility_data)  # Replace with actual facility data generation logic
            fig1, fig2 = generate_visualizations(facility_metrics)

            return table_data, table_columns, "Files processed successfully!", True, "success", "", total_loans, total_facilities, f"${total_value_assigned}", total_new_loans, f"{average_credit_score:.2f}", fig1, fig2

        except Exception as e:
            # Log the error and return an empty table
            print(f"An error occurred: {e}")
            return no_update, no_update, f"An error occurred: {str(e)}", True, "danger", "","", "", "$0", "", "", go.Figure(), go.Figure()
    @app.callback(
        Output("download-csv", "data"),
        Input("download-button", "n_clicks"),
        prevent_initial_call=True
    )
    def download_csv(n_clicks):
        return dcc.send_data_frame(combined_df.to_csv, "combined_data.csv", index=False)

    CALLBACKS_REGISTERED = True
