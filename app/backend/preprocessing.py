import pandas as pd
import numpy as np
import os

# Define the column names and column data types (classes)
LPPUB_COLUMN_NAMES = [
    "POOL_ID", "LOAN_ID", "ACT_PERIOD", "CHANNEL", "SELLER", "SERVICER",
    "MASTER_SERVICER", "ORIG_RATE", "CURR_RATE", "ORIG_UPB", "ISSUANCE_UPB",
    "CURRENT_UPB", "ORIG_TERM", "ORIG_DATE", "FIRST_PAY", "LOAN_AGE",
    "REM_MONTHS", "ADJ_REM_MONTHS", "MATR_DT", "OLTV", "OCLTV", "NUM_BO", "DTI",
    "CSCORE_B", "CSCORE_C", "FIRST_FLAG", "PURPOSE", "PROP", "NO_UNITS",
    "OCC_STAT", "STATE", "MSA", "ZIP", "MI_PCT", "PRODUCT", "PPMT_FLG", "IO",
    "FIRST_PAY_IO", "MNTHS_TO_AMTZ_IO", "DLQ_STATUS", "PMT_HISTORY", "MOD_FLAG",
    "MI_CANCEL_FLAG", "Zero_Bal_Code", "ZB_DTE", "LAST_UPB", "RPRCH_DTE",
    "CURR_SCHD_PRNCPL", "TOT_SCHD_PRNCPL", "UNSCHD_PRNCPL_CURR",
    "LAST_PAID_INSTALLMENT_DATE", "FORECLOSURE_DATE", "DISPOSITION_DATE",
    "FORECLOSURE_COSTS", "PROPERTY_PRESERVATION_AND_REPAIR_COSTS",
    "ASSET_RECOVERY_COSTS", "MISCELLANEOUS_HOLDING_EXPENSES_AND_CREDITS",
    "ASSOCIATED_TAXES_FOR_HOLDING_PROPERTY", "NET_SALES_PROCEEDS",
    "CREDIT_ENHANCEMENT_PROCEEDS", "REPURCHASES_MAKE_WHOLE_PROCEEDS",
    "OTHER_FORECLOSURE_PROCEEDS", "NON_INTEREST_BEARING_UPB",
    "PRINCIPAL_FORGIVENESS_AMOUNT", "ORIGINAL_LIST_START_DATE",
    "ORIGINAL_LIST_PRICE", "CURRENT_LIST_START_DATE", "CURRENT_LIST_PRICE",
    "ISSUE_SCOREB", "ISSUE_SCOREC", "CURR_SCOREB", "CURR_SCOREC", "MI_TYPE",
    "SERV_IND", "CURRENT_PERIOD_MODIFICATION_LOSS_AMOUNT",
    "CUMULATIVE_MODIFICATION_LOSS_AMOUNT",
    "CURRENT_PERIOD_CREDIT_EVENT_NET_GAIN_OR_LOSS",
    "CUMULATIVE_CREDIT_EVENT_NET_GAIN_OR_LOSS", "HOMEREADY_PROGRAM_INDICATOR",
    "FORECLOSURE_PRINCIPAL_WRITE_OFF_AMOUNT", "RELOCATION_MORTGAGE_INDICATOR",
    "ZERO_BALANCE_CODE_CHANGE_DATE", "LOAN_HOLDBACK_INDICATOR",
    "LOAN_HOLDBACK_EFFECTIVE_DATE", "DELINQUENT_ACCRUED_INTEREST",
    "PROPERTY_INSPECTION_WAIVER_INDICATOR", "HIGH_BALANCE_LOAN_INDICATOR",
    "ARM_5_YR_INDICATOR", "ARM_PRODUCT_TYPE",
    "MONTHS_UNTIL_FIRST_PAYMENT_RESET", "MONTHS_BETWEEN_SUBSEQUENT_PAYMENT_RESET",
    "INTEREST_RATE_CHANGE_DATE", "PAYMENT_CHANGE_DATE", "ARM_INDEX",
    "ARM_CAP_STRUCTURE", "INITIAL_INTEREST_RATE_CAP",
    "PERIODIC_INTEREST_RATE_CAP", "LIFETIME_INTEREST_RATE_CAP", "MARGIN",
    "BALLOON_INDICATOR", "PLAN_NUMBER", "FORBEARANCE_INDICATOR",
    "HIGH_LOAN_TO_VALUE_HLTV_REFINANCE_OPTION_INDICATOR", "DEAL_NAME",
    "RE_PROCS_FLAG", "ADR_TYPE", "ADR_COUNT", "ADR_UPB",
    "PAYMENT_DEFERRAL_MOD_EVENT_FLAG", "INTEREST_BEARING_UPB"
]

LPPUB_COLUMN_CLASSES = {
    "POOL_ID": str, "LOAN_ID": str, "ACT_PERIOD": str, "CHANNEL": str,
    "SELLER": str, "SERVICER": str, "MASTER_SERVICER": str, "ORIG_RATE": float,
    "CURR_RATE": float, "ORIG_UPB": float, "ISSUANCE_UPB": float,
    "CURRENT_UPB": float, "ORIG_TERM": "Int64", "ORIG_DATE": str,
    "FIRST_PAY": str, "LOAN_AGE": "Int64", "REM_MONTHS": "Int64",
    "ADJ_REM_MONTHS": "Int64", "MATR_DT": str, "OLTV": float, "OCLTV": float,
    "NUM_BO": "Int64", "DTI": float, "CSCORE_B": "Int64", "CSCORE_C": "Int64",
    "FIRST_FLAG": str, "PURPOSE": str, "PROP": str, "NO_UNITS": "Int64",
    "OCC_STAT": str, "STATE": str, "MSA": str, "ZIP": str, "MI_PCT": float,
    "PRODUCT": str, "PPMT_FLG": str, "IO": str, "FIRST_PAY_IO": str,
    "MNTHS_TO_AMTZ_IO": "Int64", "DLQ_STATUS": str, "PMT_HISTORY": str,
    "MOD_FLAG": str, "MI_CANCEL_FLAG": str, "Zero_Bal_Code": str,
    "ZB_DTE": str, "LAST_UPB": float, "RPRCH_DTE": str,
    "CURR_SCHD_PRNCPL": float, "TOT_SCHD_PRNCPL": float,
    "UNSCHD_PRNCPL_CURR": float, "LAST_PAID_INSTALLMENT_DATE": str,
    "FORECLOSURE_DATE": str, "DISPOSITION_DATE": str,
    "FORECLOSURE_COSTS": float, "PROPERTY_PRESERVATION_AND_REPAIR_COSTS": float,
    "ASSET_RECOVERY_COSTS": float,
    "MISCELLANEOUS_HOLDING_EXPENSES_AND_CREDITS": float,
    "ASSOCIATED_TAXES_FOR_HOLDING_PROPERTY": float,
    "NET_SALES_PROCEEDS": float, "CREDIT_ENHANCEMENT_PROCEEDS": float,
    "REPURCHASES_MAKE_WHOLE_PROCEEDS": float,
    "OTHER_FORECLOSURE_PROCEEDS": float, "NON_INTEREST_BEARING_UPB": float,
    "PRINCIPAL_FORGIVENESS_AMOUNT": float, "ORIGINAL_LIST_START_DATE": str,
    "ORIGINAL_LIST_PRICE": float, "CURRENT_LIST_START_DATE": str,
    "CURRENT_LIST_PRICE": float, "ISSUE_SCOREB": "Int64", "ISSUE_SCOREC": "Int64",
    "CURR_SCOREB": "Int64", "CURR_SCOREC": "Int64", "MI_TYPE": str, "SERV_IND": str,
    "CURRENT_PERIOD_MODIFICATION_LOSS_AMOUNT": float,
    "CUMULATIVE_MODIFICATION_LOSS_AMOUNT": float,
    "CURRENT_PERIOD_CREDIT_EVENT_NET_GAIN_OR_LOSS": float,
    "CUMULATIVE_CREDIT_EVENT_NET_GAIN_OR_LOSS": float,
    "HOMEREADY_PROGRAM_INDICATOR": str, "FORECLOSURE_PRINCIPAL_WRITE_OFF_AMOUNT": float,
    "RELOCATION_MORTGAGE_INDICATOR": str, "ZERO_BALANCE_CODE_CHANGE_DATE": str,
    "LOAN_HOLDBACK_INDICATOR": str, "LOAN_HOLDBACK_EFFECTIVE_DATE": str,
    "DELINQUENT_ACCRUED_INTEREST": float,
    "PROPERTY_INSPECTION_WAIVER_INDICATOR": str,
    "HIGH_BALANCE_LOAN_INDICATOR": str, "ARM_5_YR_INDICATOR": str,
    "ARM_PRODUCT_TYPE": str, "MONTHS_UNTIL_FIRST_PAYMENT_RESET": "Int64",
    "MONTHS_BETWEEN_SUBSEQUENT_PAYMENT_RESET": "Int64",
    "INTEREST_RATE_CHANGE_DATE": str, "PAYMENT_CHANGE_DATE": str, "ARM_INDEX": str,
    "ARM_CAP_STRUCTURE": str, "INITIAL_INTEREST_RATE_CAP": float,
    "PERIODIC_INTEREST_RATE_CAP": float, "LIFETIME_INTEREST_RATE_CAP": float,
    "MARGIN": float, "BALLOON_INDICATOR": str, "PLAN_NUMBER": str,
    "FORBEARANCE_INDICATOR": str,
    "HIGH_LOAN_TO_VALUE_HLTV_REFINANCE_OPTION_INDICATOR": str, "DEAL_NAME": str,
    "RE_PROCS_FLAG": str, "ADR_TYPE": str, "ADR_COUNT": "Int64", "ADR_UPB": float,
    "PAYMENT_DEFERRAL_MOD_EVENT_FLAG": str, "INTEREST_BEARING_UPB": float
}

def load_lppub_file(filename, col_names, col_classes):
    """
    Loads a single Loan Performance file.
    """
    return pd.read_csv(filename, delimiter='|', names=col_names, dtype=col_classes)

def preprocess_lppub(file_list):
    """
    Preprocesses loan performance data from multiple files.
    :param file_list: List of file paths to load and preprocess.
    :return: Tuple of processed acquisition and performance DataFrames.
    """
    # Initialize an empty DataFrame
    lppub_file = pd.DataFrame()

    # Sequentially read in and combine the files into one DataFrame
    for file_name in file_list:
        file_data = load_lppub_file(file_name, LPPUB_COLUMN_NAMES, LPPUB_COLUMN_CLASSES)
        if lppub_file.empty:
            lppub_file = file_data
        else:
            lppub_file = pd.concat([lppub_file, file_data], ignore_index=True)

    # Ensure interest rate columns are treated as numeric
    lppub_file['ORIG_RATE'] = pd.to_numeric(lppub_file['ORIG_RATE'], errors='coerce')
    lppub_file['CURR_RATE'] = pd.to_numeric(lppub_file['CURR_RATE'], errors='coerce')

    # Select and rename key columns for statistical summary analysis
    lppub_base = lppub_file[[
        'LOAN_ID', 'ACT_PERIOD', 'CHANNEL', 'SELLER', 'SERVICER', 'ORIG_RATE', 'CURR_RATE',
        'ORIG_UPB', 'CURRENT_UPB', 'ORIG_TERM', 'ORIG_DATE', 'FIRST_PAY', 'LOAN_AGE', 'REM_MONTHS',
        'ADJ_REM_MONTHS', 'MATR_DT', 'OLTV', 'OCLTV', 'NUM_BO', 'DTI', 'CSCORE_B', 'CSCORE_C',
        'FIRST_FLAG', 'PURPOSE', 'PROP', 'NO_UNITS', 'OCC_STAT', 'STATE', 'MSA', 'ZIP', 'MI_PCT',
        'PRODUCT', 'DLQ_STATUS', 'MOD_FLAG', 'Zero_Bal_Code', 'ZB_DTE', 'LAST_PAID_INSTALLMENT_DATE',
        'FORECLOSURE_DATE', 'DISPOSITION_DATE', 'FORECLOSURE_COSTS',
        'PROPERTY_PRESERVATION_AND_REPAIR_COSTS', 'ASSET_RECOVERY_COSTS',
        'MISCELLANEOUS_HOLDING_EXPENSES_AND_CREDITS',
        'ASSOCIATED_TAXES_FOR_HOLDING_PROPERTY', 'NET_SALES_PROCEEDS',
        'CREDIT_ENHANCEMENT_PROCEEDS', 'REPURCHASES_MAKE_WHOLE_PROCEEDS',
        'OTHER_FORECLOSURE_PROCEEDS', 'NON_INTEREST_BEARING_UPB',
        'PRINCIPAL_FORGIVENESS_AMOUNT', 'RELOCATION_MORTGAGE_INDICATOR', 'MI_TYPE',
        'SERV_IND', 'RPRCH_DTE', 'LAST_UPB'
    ]].copy()  # Use .copy() to avoid issues with chained assignments

    # Mutate new columns and transform date-related fields using .loc[]
    lppub_base['repch_flag'] = np.where(lppub_base['RPRCH_DTE'].notna(), 1, 0)
    lppub_base['ACT_PERIOD'] = pd.to_datetime(
        lppub_base['ACT_PERIOD'].str[2:6] + '-' + lppub_base['ACT_PERIOD'].str[0:2] + '-01'
    )
    lppub_base['FIRST_PAY'] = pd.to_datetime(
        lppub_base['FIRST_PAY'].str[2:6] + '-' + lppub_base['FIRST_PAY'].str[0:2] + '-01'
    )
    lppub_base['ORIG_DATE'] = pd.to_datetime(
        lppub_base['ORIG_DATE'].str[2:6] + '-' + lppub_base['ORIG_DATE'].str[0:2] + '-01'
    )

    # Sort by LOAN_ID and ACT_PERIOD
    lppub_base = lppub_base.sort_values(by=['LOAN_ID', 'ACT_PERIOD'])

    # Remove the original DataFrame to save memory
    del lppub_file

    # Split the data into static "Acquisition" variables and dynamic "Performance" variables
    acquisition_file = lppub_base[[
        'LOAN_ID', 'ACT_PERIOD', 'CHANNEL', 'SELLER', 'ORIG_RATE', 'ORIG_UPB',
        'ORIG_TERM', 'ORIG_DATE', 'FIRST_PAY', 'OLTV', 'OCLTV', 'NUM_BO', 'DTI',
        'CSCORE_B', 'CSCORE_C', 'FIRST_FLAG', 'PURPOSE', 'PROP', 'NO_UNITS', 'OCC_STAT',
        'STATE', 'ZIP', 'MI_PCT', 'PRODUCT', 'MI_TYPE', 'RELOCATION_MORTGAGE_INDICATOR'
    ]].rename(columns={
        'CHANNEL': 'ORIG_CHN', 'ORIG_RATE': 'orig_rt', 'ORIG_UPB': 'orig_amt',
        'ORIG_TERM': 'orig_trm', 'ORIG_DATE': 'orig_date', 'FIRST_PAY': 'first_pay',
        'OLTV': 'oltv', 'OCLTV': 'ocltv', 'NUM_BO': 'num_bo', 'DTI': 'dti',
        'FIRST_FLAG': 'FTHB_FLG', 'PURPOSE': 'purpose', 'PROP': 'PROP_TYP',
        'NO_UNITS': 'NUM_UNIT', 'OCC_STAT': 'occ_stat', 'STATE': 'state', 'ZIP': 'zip_3',
        'MI_PCT': 'mi_pct', 'PRODUCT': 'prod_type', 'RELOCATION_MORTGAGE_INDICATOR': 'relo_flg'
    })

    # Summarize first period of acquisition data
    acq_first_period = acquisition_file.groupby('LOAN_ID').agg(first_period=('ACT_PERIOD', 'max')).reset_index()

    # Join the summarized data back to the original data
    acq_first_period = acq_first_period.merge(
        acquisition_file, how='left', left_on=['LOAN_ID', 'first_period'], right_on=['LOAN_ID', 'ACT_PERIOD']
    )

    # Select the necessary columns
    acq_first_period = acq_first_period[[
        'LOAN_ID', 'ORIG_CHN', 'SELLER', 'orig_rt', 'orig_amt', 'orig_trm', 'orig_date',
        'first_pay', 'oltv', 'ocltv', 'num_bo', 'dti', 'CSCORE_B', 'CSCORE_C', 'FTHB_FLG',
        'purpose', 'PROP_TYP', 'NUM_UNIT', 'occ_stat', 'state', 'zip_3', 'mi_pct',
        'prod_type', 'MI_TYPE', 'relo_flg'
    ]]

    # Reassign acquisition_file and remove the intermediate DataFrame to save memory
    acquisition_file = acq_first_period
    del acq_first_period

    return acquisition_file
