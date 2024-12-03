import pandas as pd
from backend.models import Loan

def load_existing_loans(facilities, existing_loans_df):
    """Load existing loans from CSV into facilities, assigning based on facility_id."""

    try:
        # Load the CSV file

        if len(existing_loans_df) == 0:  # Check if the file is empty
            return

        # Columns required to instantiate the Loan class
        required_columns = [
            'LOAN_ID', 'ORIG_CHN', 'SELLER', 'orig_rt', 'orig_amt', 'orig_trm',
            'orig_date', 'first_pay', 'oltv', 'ocltv', 'num_bo', 'dti',
            'CSCORE_B', 'CSCORE_C', 'FTHB_FLG', 'purpose', 'PROP_TYP',
            'NUM_UNIT', 'occ_stat', 'state', 'zip_3', 'mi_pct', 'prod_type',
            'MI_TYPE', 'relo_flg'
        ]

        for _, row in existing_loans_df.iterrows():
            # Extract facility_id and loan data
            facility_id = row['facility_id']
            loan_data = {key: row[key] for key in required_columns}

            # Create Loan object
            loan = Loan(**loan_data)

            # Assign the loan to the appropriate facility
            if facility_id < len(facilities):
                facilities[facility_id].add_existing_loans([loan])
                
    except Exception as e:
        print(f"Error loading existing loans: {str(e)}")
        
def update_existing_loans_csv(facilities, existing_loans_df):
    """Update existing loans CSV by appending new loans while preserving existing ones."""
    
    existing_data = existing_loans_df.to_dict('records')
    # Collect all current loans from facilities
    new_data = []
    for facility_id, facility in enumerate(facilities):
        for loan in facility.existing_loans:
            loan_dict = {
                'facility_id': facility_id,
                'LOAN_ID': loan.LOAN_ID,
                'ORIG_CHN': loan.ORIG_CHN,
                'SELLER': loan.SELLER,
                'orig_rt': loan.orig_rt,
                'orig_amt': loan.orig_amt,
                'orig_trm': loan.orig_trm,
                'orig_date': loan.orig_date,
                'first_pay': loan.first_pay,
                'oltv': loan.oltv,
                'ocltv': loan.ocltv,
                'num_bo': loan.num_bo,
                'dti': loan.dti,
                'CSCORE_B': loan.CSCORE_B,
                'CSCORE_C': loan.CSCORE_C,
                'FTHB_FLG': loan.FTHB_FLG,
                'purpose': loan.purpose,
                'PROP_TYP': loan.PROP_TYP,
                'NUM_UNIT': loan.NUM_UNIT,
                'occ_stat': loan.occ_stat,
                'state': loan.state,
                'zip_3': loan.zip_3,
                'mi_pct': loan.mi_pct,
                'prod_type': loan.prod_type,
                'MI_TYPE': loan.MI_TYPE,
                'relo_flg': loan.relo_flg,
            }
            new_data.append(loan_dict)

    # Combine existing and new data
    
    combined_df = pd.DataFrame(new_data)

    # Write the updated DataFrame to the CSV file
    return combined_df