from abstract_utilities import *
import math
import operator
from functools import reduce

# -------------------------------
# Core numeric hygiene
# -------------------------------
def _is_bad(x):
    return (x is None) or (not is_number(x)) or (str(x).strip().lower() in ('', 'null'))

def gather_0(*args):
    """Convert any bad / empty / 'null' to 0.0, keep others as float."""
    out = []
    for a in args:
        out.append(0.0 if _is_bad(a) else float(a))
    return out

# -------------------------------
# Basic ops (single definitions)
# -------------------------------
def add_it(*args):
    """Sum all args; bad values become 0."""
    return float(sum(gather_0(*args)))

def subtract_it(*args):
    """a0 - a1 - a2 - ... ; bad values become 0."""
    nums = gather_0(*args)
    if not nums:
        return 0.0
    return float(reduce(operator.sub, nums))

def multiply_it(*args):
    """Multiply all args; if any becomes 0 (bad or literal zero), result is 0."""
    nums = gather_0(*args)
    if any(n == 0.0 for n in nums):
        return 0.0
    return float(reduce(operator.mul, nums, 1.0))

def divide_it(*args):
    """a0 / a1 / a2 / ... ; bad => 0, safe against ZeroDivisionError (returns 0)."""
    nums = gather_0(*args)
    try:
        return float(reduce(operator.truediv, nums))
    except ZeroDivisionError:
        return 0.0

def floor_divide_it(*args):
    """a0 // a1 // a2 // ... ; bad => 0, safe against ZeroDivisionError (returns 0)."""
    nums = gather_0(*args)
    try:
        return float(reduce(operator.floordiv, nums))
    except ZeroDivisionError:
        return 0.0

# -------------------------------
# Exponent helpers (deduplicated)
# -------------------------------
def exp_it(base, *factors):
    """
    Raise `base` to the power of (product of all `factors`).
    exp_it(10, 2, 3) -> 10 ** (2*3) == 10**6
    If any input is bad or no factors given, returns 0.0 (consistent with other helpers).
    """
    nums = gather_0(base, *factors)
    b, *f = nums
    if not f or any(n == 0.0 for n in nums):
        return 0.0
    exponent = float(reduce(operator.mul, f, 1.0))
    return float(b) ** exponent

def pow10(exp):
    """10**exp with float output; bad exp -> 0.0^? -> return 1.0 (neutral for scaling)."""
    if _is_bad(exp):
        return 1.0
    return 10.0 ** float(exp)

def scale_pow10(value, exp):
    """Scale value by 10**exp. Neutral if exp is bad."""
    return multiply_it(value, pow10(exp))

# Canonical public API for “multiply by 10^…”:
def exponential(value, *exp_factors):
    """
    Multiply `value` by 10 ** (product(exp_factors)).
    exponential(5, 2, 3) -> 5 * 10**(2*3) == 5e6
    If no exp_factors are given, returns value.
    """
    if not exp_factors:
        return float(value) if not _is_bad(value) else 0.0
    exp_prod = multiply_it(*exp_factors)
    if exp_prod == 0.0 and all(not _is_bad(x) for x in exp_factors):
        # valid inputs produced 0 exponent => scale by 1
        return float(value) if not _is_bad(value) else 0.0
    return scale_pow10(value, exp_prod)

# Back-compat alias for legacy callers:
def exponentials(value, exp=9, num=1):
    """
    Legacy alias: multiply `value` by 10 ** (exp * num).
    Prefer: exponential(value, exp, num) or scale_pow10(value, exp*num).
    """
    return exponential(value, exp, num)

# -------------------------------
# Argument picker
# -------------------------------
def get_proper_args(strings, *args, **kwargs):
    """
    Extract values by key order from kwargs first; if missing, consume positional args in order.
    Example: get_proper_args(["a","b"], 1, b=3) -> [1, 3]
    """
    proper = []
    args = list(args)
    for key in strings:
        if key in kwargs:
            proper.append(kwargs[key])
        elif args:
            proper.append(args.pop(0))
        else:
            proper.append(None)
    return proper

# -------------------------------
# Your SOL / token helpers (using the unified expo)
# -------------------------------
SOL_DECIMAL_PLACE = 9
SOL_LAMPORTS = int(pow10(SOL_DECIMAL_PLACE))  # 10**9

def get_lamp_difference(*args, **kwargs):
    """
    Keep behavior: compute a lamport “scale” based on digit length of virtualSolReserves.
    """
    sol_lamports = SOL_LAMPORTS
    [virtualSolReserves] = get_proper_args(["virtualSolReserves"], *args, **kwargs)
    if _is_bad(virtualSolReserves):
        return 0
    virtual_len = len(str(int(float(virtualSolReserves))))
    virtual_sol_lamports = int(pow10(virtual_len))  # 10**virtual_len
    scale_len = len(str(int(virtual_sol_lamports / sol_lamports))) if sol_lamports else 0
    return int(pow10(scale_len))

def get_price(*args, **kwargs):
    """
    price = virtualSolReserves / virtualTokenReserves / lamp_difference
    """
    virtualSolReserves, virtualTokenReserves = get_proper_args(
        ["virtualSolReserves", "virtualTokenReserves"], *args, **kwargs
    )
    base = divide_it(virtualSolReserves, virtualTokenReserves)
    return divide_it(base, get_lamp_difference(*args, **kwargs))

def get_amount_price(*args, **kwargs):
    solAmount, tokenAmount = get_proper_args(["solAmount", "tokenAmount"], *args, **kwargs)
    return divide_it(solAmount, tokenAmount)

def getSolAmountUi(*args, **kwargs):
    [solAmount] = get_proper_args(["solAmount"], *args, **kwargs)
    # scale by 10**9
    return exponential(solAmount, SOL_DECIMAL_PLACE)

def getTokenAmountUi(*args, **kwargs):
    solAmountUi = getSolAmountUi(*args, **kwargs)
    price = get_price(*args, **kwargs)
    return divide_it(solAmountUi, price)

def derive_token_decimals(*args, **kwargs):
    virtualTokenReserves, tokenAmount = get_proper_args(
        ["virtualTokenReserves", "tokenAmount"], *args, **kwargs
    )
    price = get_price(*args, **kwargs)
    if not (virtualTokenReserves and tokenAmount and price) or any(
        float(x) <= 0 for x in [virtualTokenReserves, tokenAmount, price]
    ):
        raise ValueError("All inputs must be positive.")
    derived_token_amount = divide_it(virtualTokenReserves, price)
    ratio = divide_it(derived_token_amount, tokenAmount)
    # count decimal places needed to make ratio an integer (tolerant to fp noise)
    decimals = -1
    while abs(ratio - round(ratio)) > 1e-9:
        ratio *= 10
        decimals += 1
    return decimals

def derive_token_decimals_from_token_variables(variables):
    variables["price"] = get_price(**variables)
    derived_token_amount = divide_it(variables["virtualTokenReserves"], variables["price"])
    ratio = divide_it(derived_token_amount, variables["tokenAmount"])
    decimals = -1
    while abs(ratio - round(ratio)) > 1e-9:
        ratio *= 10
        decimals += 1
    variables["tokenDecimals"] = decimals
    return variables

def get_token_amount_ui(*args, **kwargs):
    [tokenAmount] = get_proper_args(["tokenAmount"], *args, **kwargs)
    # scale by 10**(-token_decimals)
    dec = derive_token_decimals(*args, **kwargs)
    return exponential(tokenAmount, -dec, 1)

def update_token_variables(variables):
    variables['solAmountUi'] = getSolAmountUi(**variables)
    variables['solDecimals'] = SOL_DECIMAL_PLACE
    variables = derive_token_decimals_from_token_variables(variables)
    variables['tokenAmountUi'] = exponential(variables['tokenAmount'], -variables["tokenDecimals"], 1)
    return variables
