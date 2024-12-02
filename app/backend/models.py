class Loan:
    def __init__(self, LOAN_ID, ORIG_CHN, SELLER, orig_rt, orig_amt, orig_trm,
                 orig_date, first_pay, oltv, ocltv, num_bo, dti, CSCORE_B,
                 CSCORE_C, FTHB_FLG, purpose, PROP_TYP, NUM_UNIT, occ_stat,
                 state, zip_3, mi_pct, prod_type, MI_TYPE, relo_flg):
        self.LOAN_ID = LOAN_ID
        self.ORIG_CHN = ORIG_CHN
        self.SELLER = SELLER
        self.orig_rt = orig_rt
        self.orig_amt = orig_amt
        self.orig_trm = orig_trm
        self.orig_date = orig_date
        self.first_pay = first_pay
        self.oltv = oltv
        self.ocltv = ocltv
        self.num_bo = num_bo
        self.dti = dti
        self.CSCORE_B = CSCORE_B
        self.CSCORE_C = CSCORE_C
        self.FTHB_FLG = FTHB_FLG
        self.purpose = purpose
        self.PROP_TYP = PROP_TYP
        self.NUM_UNIT = NUM_UNIT
        self.occ_stat = occ_stat
        self.state = state
        self.zip_3 = zip_3
        self.mi_pct = mi_pct
        self.prod_type = prod_type
        self.MI_TYPE = MI_TYPE
        self.relo_flg = relo_flg


class Facility:
    def __init__(self, facility_id, facility_cost, facility_size):
        self.facility_cost = facility_cost
        self.facility_id = facility_id
        self.facility_size = facility_size
        self.asset_covenants = []
        self.pool_covenants = []
        self.existing_loans = []

    def add_asset_covenants(self, asset_covenant):
        self.asset_covenants.append(asset_covenant)

    def add_pool_covenants(self, pool_covenant):
        self.pool_covenants.append(pool_covenant)

    def add_existing_loans(self, existing_loans):
        self.existing_loans.extend(existing_loans)

    def asset_check(self, new_loan):
        return all(asset_covenant.asset_check(new_loan) for asset_covenant in self.asset_covenants)  # Checks all Asset Covenants


class AssetCovenant:
    def __init__(self, constr_prop, constr_op, constr_val, crit_prop, crit_op, crit_val):
        self.constr_prop = constr_prop
        self.constr_op = constr_op
        self.constr_val = constr_val
        self.crit_prop = crit_prop
        self.crit_op = crit_op
        self.crit_val = crit_val

    def asset_check(self, new_loan):
        if all(self._helper(getattr(new_loan, prop), op, val) for prop, op, val in zip(self.crit_prop, self.crit_op, self.crit_val)):
            return self._helper(getattr(new_loan, self.constr_prop), self.constr_op, self.constr_val)
        else:
            return True

    def _helper(self, prop, op, val):
        if op == '==':
            return prop == val
        elif op == '!=':
            return prop != val
        elif op == '<=':
            return prop <= val
        elif op == '>=':
            return prop >= val
        else:
            return False


class PoolCovenant:
    def __init__(self, a, b, c, constr_type, constr_op):
        self.a = a
        self.b = b
        self.c = c
        self.constr_type = constr_type
        self.constr_op = constr_op
        self.a_e = []
        self.b_e = []

    def update_params(self, a_new, b_new):
        self.a_e.extend(a_new)
        self.b_e.extend(b_new)
