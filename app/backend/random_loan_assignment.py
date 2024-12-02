import pandas as pd
from backend.models import Loan 

def assign_loans(df, n=200):
    """
    Assign loans randomly and filter them based on certain criteria.

    Parameters:
        df (pd.DataFrame): The preprocessed DataFrame containing loan data.
        n (int): The number of random loans to select.

    Returns:
        dict: A dictionary containing the assigned loans and relevant statistics.
    """
    # Select 'n' random assets to be assigned
    df_filtered = df.sample(n)

    # Split the random sample into two groups
    random_df = df_filtered.iloc[len(df_filtered) // 2:]
    random_df_prealloc = df_filtered.iloc[:len(df_filtered) // 2]

    # Apply filters to the preallocated loans
    random_df_prealloc = random_df_prealloc[
        (random_df_prealloc['oltv'] <= 90) &
        (random_df_prealloc['CSCORE_B'] >= 600) &
        (random_df_prealloc['orig_rt'] >= 6)
    ]

    # Further split the preallocated loans
    random_df_prealloc_f1 = random_df_prealloc[:len(random_df_prealloc) // 2]
    random_df_prealloc_f2 = random_df_prealloc[len(random_df_prealloc) // 2:]

    # Convert DataFrames to Loan objects
    loans_to_assign = [Loan(**random_df.iloc[row]) for row in range(len(random_df))]
    loans_assigned = [Loan(**random_df_prealloc.iloc[row]) for row in range(len(random_df_prealloc))]
    loans_assigned_f1 = [Loan(**random_df_prealloc_f1.iloc[row]) for row in range(len(random_df_prealloc_f1))]
    loans_assigned_f2 = [Loan(**random_df_prealloc_f2.iloc[row]) for row in range(len(random_df_prealloc_f2))]

    # Calculate totals for testing
    total_assigned = sum(loan.orig_amt for loan in loans_assigned)
    total_to_assign = sum(loan.orig_amt for loan in loans_to_assign)
    total_f1 = sum(random_df_prealloc_f1['orig_amt'])
    total_f2 = sum(random_df_prealloc_f2['orig_amt'])

    # Return results as a dictionary
    return random_df, loans_to_assign
