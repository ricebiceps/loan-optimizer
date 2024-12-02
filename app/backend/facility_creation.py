from typing import List, Dict, Any
import pandas as pd
from backend.models import Facility, AssetCovenant, PoolCovenant

def clean_string(s):
    """Clean quoted strings from CSV."""
    if pd.isna(s):
        return None
    if isinstance(s, str):
        # Remove extra quotes and spaces
        s = s.strip().strip('"""').strip("'''")
    return s

def evaluate_expression(expr, random_df):
    """Safely evaluate expressions that may contain DataFrame operations."""
    if pd.isna(expr):
        return None
    try:
        # For any expression containing random_df
        if isinstance(expr, str):
            return eval(expr, {'random_df': random_df})
        # For numeric values
        if isinstance(expr, (int, float)):
            return expr
        return expr
    except Exception as e:
        print(f"Error evaluating expression: {expr}")
        print(f"Error details: {str(e)}")
        return None

def create_facilities_from_config(config_df, existing_loans_df, random_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Creates facilities from a configuration file with support for various expression types.
    """
    # Read the configuration file
    existing_loans_df = existing_loans_df.dropna(subset=[existing_loans_df.columns[0]])

    # Initialize dictionary to store facilities
    facilities = {}

    # Process each row in the configuration
    for _, row in config_df.iterrows():
        command = row['Command']
        cost = row['Cost']
        facility_num = row['Number']
        facility_name = f"facility{facility_num}"
        facility_size = row["facility_space"]
        
        if pd.isna(facility_size):
            facility_size = config_df[config_df['Number'] == facility_num]["facility_space"].max(skipna=True)
            if pd.isna(facility_size):  # If facility_size is still NaN, assign a default value (e.g., 0)
                facility_size = 0

        # Create facility if it doesn't exist
        if facility_name not in facilities:
            facilities[facility_name] = Facility(facility_id=facility_num, facility_cost=cost, facility_size = facility_size)
        else:
            facilities[facility_name].facility_size = max(facilities[facility_name].facility_size, facility_size)
        if 'add_asset_covenants' in command:
            # Clean and validate asset covenant parameters
            constr_prop = clean_string(row['constr_prop'])
            constr_op = clean_string(row['constr_op'])
            constr_val = row['constr_val']

            if pd.notna(constr_prop) and pd.notna(constr_op) and pd.notna(constr_val):
                # Handle critical properties if they exist
                crit_prop = [] if pd.isna(row['crit_prop']) else row['crit_prop'].split(',')
                crit_op = [] if pd.isna(row['crit_op']) else row['crit_op'].split(',')
                crit_val = [] if pd.isna(row['crit_val']) else [float(x) for x in row['crit_val'].split(',')]

                covenant = AssetCovenant(
                    constr_prop=constr_prop,
                    constr_op=constr_op,
                    constr_val=float(constr_val),
                    crit_prop=crit_prop,
                    crit_op=crit_op,
                    crit_val=crit_val
                )
                facilities[facility_name].add_asset_covenants(covenant)

        elif 'add_pool_covenants' in command:
            # Check if we have the necessary parameters
            if pd.notna(row['a']) and pd.notna(row['b']) and pd.notna(row['c']):
                # Directly evaluate whatever expressions are in the a and b columns
                a_param = evaluate_expression(row['a'], random_df)
                b_param = evaluate_expression(row['b'], random_df)

                if a_param is not None and b_param is not None:
                    # Handle NaN values for constr_type and constr_op
                    constr_type = 0 if pd.isna(row['constr_type']) else int(row['constr_type'])
                    constr_op = 0 if pd.isna(row['constr_op.1']) else int(row['constr_op.1'])

                    covenant = PoolCovenant(
                        a=a_param,
                        b=b_param,
                        c=float(row['c']),
                        constr_type=constr_type,
                        constr_op=constr_op
                    )

                    if len(existing_loans_df) > 0:
                        a_e = evaluate_expression(row['a'], existing_loans_df[existing_loans_df['facility_id']==facility_num])
                        b_e = evaluate_expression(row['b'], existing_loans_df[existing_loans_df['facility_id']==facility_num])
                        covenant.update_params(a_new=a_e,b_new=b_e)

                    facilities[facility_name].add_pool_covenants(covenant)

    return facilities