from typing import List, Dict, Any, Tuple
import pandas as pd
from dataclasses import dataclass
from gurobipy import Model, GRB, quicksum
from backend.models import Loan, Facility
from backend.existing_loans_handle import load_existing_loans, update_existing_loans_csv

def create_base_model(
    name: str,
    loans_to_assign: List[Loan],
    facilities: List[Facility],
    asset_acc_matrix: List[List[int]]
) -> tuple[Model, Any]:
    """Create a base Gurobi model with common constraints."""
    num_loans = len(loans_to_assign)
    num_facilities = len(facilities)
    
    model = Model(name)
    x = model.addVars(num_loans, num_facilities, vtype=GRB.BINARY, name="x")
    
    # Add constraints for one loan per facility
    for i in range(num_loans):
        model.addConstr(
            quicksum(x[i, j] for j in range(num_facilities)) <= 1,
            f"OneFacilityPerLoan_{i}"
        )
    
    # Add constraints for loan-facility compatibility
    for i in range(num_loans):
        for j in range(num_facilities):
            model.addConstr(
                x[i, j] <= asset_acc_matrix[i][j],
                f"LoanCompatibility_{i}_{j}"
            )
    
    # Add constraints for pool covenants
    for facility in facilities:
        j = facility.facility_id
        for pool_covenant in facility.pool_covenants:
            flip_ineq = 1 - 2*pool_covenant.constr_op  # -1 if geq, 1 otherwise
            
            if pool_covenant.constr_type:
                # Type 1 constraint: Weighted sum type
                left_sum = quicksum(
                    x[i, j] * float(pool_covenant.a[i]) * float(pool_covenant.b[i])
                    for i in range(len(pool_covenant.b))
                )
                existing_sum = quicksum(
                    float(pool_covenant.a_e[i]) * float(pool_covenant.b_e[i])
                    for i in range(len(pool_covenant.b_e))
                )
                model.addConstr(
                    (left_sum + existing_sum) * flip_ineq <= float(pool_covenant.c) * flip_ineq
                )
            else:
                # Type 0 constraint: Ratio type
                left_sum = quicksum(
                    x[i, j] * (float(pool_covenant.a[i]) - float(pool_covenant.c)) * float(pool_covenant.b[i])
                    for i in range(len(pool_covenant.b))
                )
                right_sum = quicksum(
                    (float(pool_covenant.c) - float(pool_covenant.a_e[i])) * float(pool_covenant.b_e[i])
                    for i in range(len(pool_covenant.b_e))
                )
                model.addConstr(
                    left_sum * flip_ineq <= right_sum * flip_ineq
                )
    
    return model, x

def set_objective(
    model: Model,
    x: Any,
    objective_type: str,
    input_field: str,
    loans_to_assign: List[Loan],
    facilities: List[Facility],
    prev_objectives: List[Dict] = None,
    tolerance: float = 1e-4
):
    """Set the objective function based on the optimization parameters."""
    num_loans = len(loans_to_assign)
    num_facilities = len(facilities)
    
    # Add constraints from previous optimization steps
    if prev_objectives:
        for prev_obj in prev_objectives:
            if prev_obj['input'] == 'facility_cost':
                continue
            
            model.addConstr(
                quicksum(float(getattr(loans_to_assign[i], prev_obj['input'])) * x[i, j]
                        for i in range(num_loans)
                        for j in range(num_facilities)) >= float(prev_obj['value']) - tolerance
            )
    
    # Set new objective
    sense = GRB.MAXIMIZE if objective_type == 'Max' else GRB.MINIMIZE
    
    if input_field == 'facility_cost':
        # Create facility usage variables
        facility_used = model.addVars(num_facilities, vtype=GRB.BINARY, name="facility_used")
        
        # Add facility usage constraints
        for j in range(num_facilities):
            model.addConstr(
                quicksum(x[i, j] for i in range(num_loans)) <= num_loans * facility_used[j],
                f"FacilityUsage_{j}"
            )
            
        # Set objective to minimize facility costs
        model.setObjective(
            quicksum(float(facilities[j].facility_cost) * facility_used[j] 
                    for j in range(num_facilities)),
            sense
        )
    else:
        # Standard objective for other fields
        model.setObjective(
            quicksum(float(getattr(loans_to_assign[i], input_field)) * x[i, j]
                    for i in range(num_loans)
                    for j in range(num_facilities)),
            sense
        )

def optimize_sequential(
    loans_to_assign: List[Loan],
    facilities: List[Facility],
    asset_acc_matrix: List[List[int]],
    optimization_order_file: pd.DataFrame
) -> Dict[str, Any]:
    """
    Perform sequential optimization with detailed results tracking
    """
    optimization_steps = optimization_order_file.to_dict('records')
    results = []
    prev_objectives = []
    final_results = {
        'objective_values': [],
        'assignments': [],
        'loans_by_facility': {},
        'unassigned_loans': [],
        'facility_stats': {}
    }
    
    for step in optimization_steps:
        print(f"Starting optimization step {step['Order']}: {step['Type']} {step['Input']}")
        
        model, x = create_base_model(
            f"Step_{step['Order']}", 
            loans_to_assign, 
            facilities, 
            asset_acc_matrix
        )
        
        set_objective(
            model, x, step['Type'], step['Input'],
            loans_to_assign, facilities, prev_objectives
        )

        model.setParam('OutputFlag', 0)
        
        model.optimize()
        
        if model.Status == GRB.OPTIMAL:
            obj_value = model.ObjVal
            prev_objectives.append({
                'input': step['Input'],
                'value': obj_value
            })
            
            # Track assignments and loans for each facility
            current_assignments = []
            facility_loans = {i: [] for i in range(len(facilities))}
            unassigned = []
            
            for i in range(len(loans_to_assign)):
                assigned = False
                for j in range(len(facilities)):
                    if x[i, j].X > 0:
                        current_assignments.append((i, j))
                        facility_loans[j].append(loans_to_assign[i])
                        assigned = True
                if not assigned:
                    unassigned.append(loans_to_assign[i])
            
            # Calculate facility statistics
            facility_stats = {}
            for fac_id, fac_loans in facility_loans.items():
                if fac_loans:
                    total_amount = sum(loan.orig_amt for loan in fac_loans)
                    avg_credit_score = sum(loan.CSCORE_B for loan in fac_loans) / len(fac_loans)
                    facility_stats[fac_id] = {
                        'total_amount': total_amount,
                        'avg_credit_score': avg_credit_score,
                        'num_loans': len(fac_loans)
                    }
            
            step_result = {
                'step': step['Order'],
                'objective_type': step['Type'],
                'input_field': step['Input'],
                'objective_value': obj_value,
                'assignments': current_assignments,
                'facility_loans': facility_loans,
                'unassigned_loans': unassigned,
                'facility_stats': facility_stats
            }
            
            results.append(step_result)
    
    # Store final results
    if results:
        final_step = results[-1]
        final_results['objective_values'] = [r['objective_value'] for r in results]
        final_results['assignments'] = final_step['assignments']
        final_results['loans_by_facility'] = final_step['facility_loans']
        final_results['unassigned_loans'] = final_step['unassigned_loans']
        final_results['facility_stats'] = final_step['facility_stats']
    
    return final_results

def apply_assignments(assignments: List[Tuple[int, int]], 
                     loans_to_assign: List[Loan], 
                     facilities: List[Facility]):
    """
    Apply the optimized assignments to the facilities
    """
    for assignment in assignments:
        loan_index = assignment[0]
        facility_index = assignment[1]
        loan_to_assign = loans_to_assign[loan_index]
        facility_to_assign = facilities[facility_index]
        facility_to_assign.add_existing_loans(existing_loans=[loan_to_assign])

def run_optimization_process(new_loans_df, asset_acc_matrix, facilities, 
                           existing_loans_file, order_df):
    """Run complete optimization process"""
    # Start with empty facilities
    for facility in facilities:
        facility.existing_loans = []
    
    # First load historical assignments
    load_existing_loans(facilities, existing_loans_file)
    
    # Convert new loans to Loan objects
    new_loans = [Loan(**new_loans_df.iloc[row]) for row in range(len(new_loans_df))]
    print(f"Processing {len(new_loans)} new loans")
      
    # Run optimization
    results = optimize_sequential(
        loans_to_assign=new_loans,
        facilities=facilities,
        asset_acc_matrix=asset_acc_matrix,
        optimization_order_file = order_df
    )
    
    # Apply new assignments
    apply_assignments(results['assignments'], new_loans, facilities)
    
    # Update existing loans CSV by appending only the new assignments
    combined_df = update_existing_loans_csv(facilities, existing_loans_file)

    
    return results, facilities, combined_df