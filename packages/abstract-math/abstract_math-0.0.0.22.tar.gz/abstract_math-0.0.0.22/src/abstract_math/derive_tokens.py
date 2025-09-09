from decimal import Decimal, getcontext
from .safe_math import *
def exponentials(value,exp=9,num=-1):
    return multiply_it(value,exp_it(10,exp,num))

# High precision for decimal ops
getcontext().prec = 50

# SOL constants
SOL_DECIMAL_PLACE = 9
# lamports per SOL = 10**9
SOL_LAMPORTS = sol_lamports = int(exponentials(1, exp=SOL_DECIMAL_PLACE, num=1))


def get_proper_args(strings, *args, **kwargs):
    """
    Extract values for keys in `strings` from kwargs; if missing, pull from positional args in order.
    """
    properArgs = []
    for key in strings:
        kwarg = kwargs.get(key)
        if kwarg is None and args:
            kwarg = args[0]
            args = [] if len(args) == 1 else args[1:]
        properArgs.append(kwarg)
    return properArgs


# ---------- Lamports helpers ----------
def get_lamports(integer: int):
    """
    Convert an integer N to 10^(len(str(N)) + 1).
    NOTE: this is your original behavior, not 10**9 unless N is 1 with exp=9.
    """
    return exp_it(10, len(str(integer)) + 1, 1)


def get_lamport_difference(lamports: int, virtual_lamports: int):
    """
    Compare 'lamports' vs 'virtual_lamports' and return 10^(len(str(int(virtual/actual))))
    """
    integer = int(virtual_lamports / lamports)
    exp = len(str(integer))
    return int(exponential(1, exp, 1))


# ---------- Virtual reserves / ratios ----------
def get_vitual_reserves(*args, **kwargs):
    return get_proper_args(["virtualSolReserves", "virtualTokenReserves"], *args, **kwargs)


def get_virtual_reserve_ratio(*args, **kwargs):
    sol_res, token_res = get_vitual_reserves(*args, **kwargs)
    return divide_it(sol_res, token_res)


# ---------- SOL-specific ----------
def get_virtual_sol_reservs(*args, **kwargs):
    reserves = get_proper_args(["virtualSolReserves"], *args, **kwargs)
    return reserves[0] if reserves else None


def get_virtual_sol_lamports(*args, **kwargs):
    sol_res = get_virtual_sol_reservs(*args, **kwargs)
    return get_lamports(sol_res)


def get_virtual_sol_lamp_difference(*args, **kwargs):
    v_lam = get_virtual_sol_lamports(*args, **kwargs)
    return get_lamport_difference(SOL_LAMPORTS, v_lam)


def get_sol_amount(*args, **kwargs):
    amounts = get_proper_args(["solAmount"], *args, **kwargs)
    return amounts[0] if amounts else None


def getSolAmountUi(*args, **kwargs):
    sol_amt = get_sol_amount(*args, **kwargs)
    return exponential(sol_amt, SOL_DECIMAL_PLACE)


# ---------- Token-specific ----------
def get_virtual_token_reserves(*args, **kwargs):
    reserves = get_proper_args(["virtualTokenReserves"], *args, **kwargs)
    return reserves[0] if reserves else None


def get_virtual_token_lamports(*args, **kwargs):
    token_res = get_virtual_token_reserves(*args, **kwargs)
    return get_lamports(token_res)


def get_token_amount(*args, **kwargs):
    amounts = get_proper_args(["tokenAmount"], *args, **kwargs)
    return amounts[0] if amounts else None


def get_price(*args, **kwargs):
    reserve_ratio = get_virtual_reserve_ratio(*args, **kwargs)
    sol_diff = get_virtual_sol_lamp_difference(*args, **kwargs)
    return divide_it(reserve_ratio, sol_diff)


def derive_token_amount(*args, **kwargs):
    token_res = get_virtual_token_reserves(*args, **kwargs)
    price = get_price(*args, **kwargs)
    return divide_it(token_res, price)


def get_derived_token_ratio(*args, **kwargs):
    derived_amt = derive_token_amount(*args, **kwargs)
    token_amt = get_token_amount(*args, **kwargs)
    return divide_it(derived_amt, token_amt)


def derive_decimals_from_vars(*args, **kwargs):
    ratio = get_derived_token_ratio(*args, **kwargs)
    decimals = -1
    # Count how many decimal places are needed to make ratio an integer (<= 1e-9 tolerance)
    while abs(ratio - round(ratio)) > 1e-9:
        ratio *= 10
        decimals += 1
    return decimals


def get_token_amount_ui(*args, **kwargs):
    token_amt = get_token_amount(*args, **kwargs)
    token_decimals = derive_decimals_from_vars(*args, **kwargs)
    return exponential(token_amt, token_decimals)


def derive_token_decimals_from_token_variables(**variables):
    variables["price"] = get_price(**variables)
    variables["tokenDecimals"] = derive_decimals_from_vars(**variables)
    return variables


def update_token_variables(variables: dict):
    variables['solAmountUi'] = getSolAmountUi(**variables)
    variables['solDecimals'] = SOL_DECIMAL_PLACE
    variables = derive_token_decimals_from_token_variables(**variables)
    variables['tokenAmountUi'] = get_token_amount_ui(**variables)
    return variables
