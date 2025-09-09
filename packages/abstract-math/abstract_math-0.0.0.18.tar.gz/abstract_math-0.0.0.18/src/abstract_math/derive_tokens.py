from decimal import Decimal, getcontext
from .safe_math import *

# Set high precision for decimal operations
getcontext().prec = 50

# Constants for SOL decimal places and lamports conversion
SOL_DECIMAL_PLACE = 9
SOL_LAMPORTS = sol_lamports = int(exponential(1, SOL_DECIMAL_PLACE, 1))


def get_proper_args(strings, *args, **kwargs):
    """
    Extracts values from kwargs based on the provided keys (strings). If not present in kwargs,
    falls back to positional args in order.
    """
    properArgs = []
    for key in strings:
        kwarg = kwargs.get(key)
        if kwarg is None and args:
            kwarg = args[0]
            args = [] if len(args) == 1 else args[1:]
        properArgs.append(kwarg)
    return properArgs

# Lamports calculations

def get_lamports(integer):
    """
    Given an integer representing SOL, returns lamports (10^(digits_in_integer+1)).
    """
    return exp_it(10, len(str(integer)) + 1, 1)


def get_lamport_difference(lamports, virtual_lamports):
    """
    Compares actual lamports to virtual lamports and returns the corresponding exponent-based difference.
    """
    integer = int(virtual_lamports / lamports)
    exp = len(str(integer))
    return int(exponential(1, exp, 1))

# Virtual reserves and ratios

def get_vitual_reserves(*args, **kwargs):
    return get_proper_args(["virtualSolReserves", "virtualTokenReserves"], *args, **kwargs)


def get_virtual_reserve_ratio(*args, **kwargs):
    sol_res, token_res = get_vitual_reserves(*args, **kwargs)
    return divide_it(sol_res, token_res)

# SOL-specific calculations

def get_virtual_sol_reservs(*args, **kwargs):
    reserves = get_proper_args(["virtualSolReserves"], *args, **kwargs)
    return reserves[0] if reserves else None


def get_virtual_sol_lamports(*args, **kwargs):
    sol_res = get_virtual_sol_reservs(*args, **kwargs)
    return get_lamports(sol_res)


def get_virtual_sol_lamp_difference(*args, **kwargs):
    v_lam = get_virtual_sol_lamports(*args, **kwargs)
    return get_lamport_difference(SOL_LAMPORTS, v_lam)

# SOL amount conversions

def get_sol_amount(*args, **kwargs):
    amounts = get_proper_args(["solAmount"], *args, **kwargs)
    return amounts[0] if amounts else None


def getSolAmountUi(*args, **kwargs):
    sol_amt = get_sol_amount(*args, **kwargs)
    return exponential(sol_amt, SOL_DECIMAL_PLACE)

# Token-specific calculations

def get_virtual_token_reserves(*args, **kwargs):
    reserves = get_proper_args(["virtualTokenReserves"], *args, **kwargs)
    return reserves[0] if reserves else None


def get_virtual_token_lamports(*args, **kwargs):
    token_res = get_virtual_token_reserves(*args, **kwargs)
    return get_lamports(token_res)


def get_token_amount(*args, **kwargs):
    amounts = get_proper_args(["tokenAmount"], *args, **kwargs)
    return amounts[0] if amounts else None


def get_token_amount_ui(*args, **kwargs):
    token_amt = get_token_amount(*args, **kwargs)
    token_decimals = derive_decimals_from_vars(*args, **kwargs)
    return exponential(token_amt, token_decimals)


def derive_token_decimals_from_token_variables(**variables):
    variables["price"] = get_price(**variables)
    variables["tokenDecimals"] = derive_decimals_from_vars(**variables)
    return variables


def get_derived_token_ratio(*args, **kwargs):
    derived_amt = derive_token_amount(*args, **kwargs)
    token_amt = get_token_amount(*args, **kwargs)
    return divide_it(derived_amt, token_amt)


def derive_token_amount(*args, **kwargs):
    token_res = get_virtual_token_reserves(*args, **kwargs)
    price = get_price(*args, **kwargs)
    return divide_it(token_res, price)


def get_price(*args, **kwargs):
    reserve_ratio = get_virtual_reserve_ratio(*args, **kwargs)
    sol_diff = get_virtual_sol_lamp_difference(*args, **kwargs)
    return divide_it(reserve_ratio, sol_diff)


def derive_decimals_from_vars(*args, **kwargs):
    ratio = get_derived_token_ratio(*args, **kwargs)
    decimals = -1
    while abs(ratio - round(ratio)) > 1e-9:
        ratio *= 10
        decimals += 1
    return decimals


def update_token_variables(variables):
    variables['solAmountUi'] = getSolAmountUi(**variables)
    variables['solDecimals'] = SOL_DECIMAL_PLACE
    variables = derive_token_decimals_from_token_variables(**variables)
    variables['tokenAmountUi'] = get_token_amount_ui(**variables)
    return variables
