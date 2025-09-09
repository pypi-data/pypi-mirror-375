from abstract_utilities import *
import math
#math functions ------------------------------------------------------------------------------------------------------
def exponential(value,exp=9,num=-1):
    return multiply_it(value,exp_it(10,exp,num))

def add_it(number_1,number_2):
    if return_0(number_1,number_2)==float(0):
        return float(0)
    return float(number_1)+float(number_2)

def subtract_it(number_1,number_2):
    if return_0(number_1,number_2)==float(0):
        return float(0)
    return float(number_1)-float(number_2)

def get_percentage(owner_balance,address_balance):
    retained_div = divide_it(owner_balance,address_balance)
    retained_mul = multiply_it(retained_div,100)
    return round(retained_mul,2)

def return_0(*args):
    """Return True if *any* arg is “falsy” (None, non-number, or zero‐like)."""
    for arg in args:
        if arg is None or not is_number(arg) or str(arg).strip().lower() in ('0', '', 'null'):
            return True
    return False

def gather_0(*args):
    """Convert any “falsy” arg into float(0), leave others alone."""
    cleaned = []
    for arg in args:
        if arg is None or not is_number(arg) or str(arg).strip().lower() in ('0', '', 'null'):
            cleaned.append(0.0)
        else:
            cleaned.append(float(arg))
    return cleaned

def add_it(*args):
    """Sum together any number of args, treating bad values as 0."""
    nums = gather_0(*args)
    return float(sum(nums))

def multiply_it(*args):
    """Multiply any number of args, but return 0 if any input is ‘bad’ or zero-like."""
    nums = gather_0(*args)
    if any(n == 0.0 for n in nums):
        return 0.0
    return float(reduce(operator.mul, nums, 1.0))

def divide_it(*args):
    """
    Divide args[0] by args[1] by args[2]… 
    If any input is bad or you hit a zero‐division, return 0.
    """
    nums = gather_0(*args)
    try:
        return float(reduce(operator.truediv, nums))
    except ZeroDivisionError:
        return 0.0

def floor_divide_it(*args):
    """
    Floor‐divide args[0] by args[1] by args[2]…
    If any input is bad or you hit a zero‐division, return 0.
    """
    nums = gather_0(*args)
    try:
        return float(reduce(operator.floordiv, nums))
    except ZeroDivisionError:
        return 0.0

def subtract_it(*args):
    """
    Subtract all subsequent args from the first:
       args[0] - args[1] - args[2] - …
    Bad values become 0.
    """
    nums = gather_0(*args)
    if not nums:
        return 0.0
    return float(reduce(operator.sub, nums))

def exp_it(base, *factors):
    """
    Raise `base` to the power of (product of all `factors`).
    e.g. exp_it(10, 2, 3) → 10**(2*3) == 10**6
    Bad values become 0 (and so the result is 0).
    """
    nums = gather_0(base, *factors)
    b, *f = nums
    if return_0(*nums) or not f:
        return 0.0
    exponent = reduce(operator.mul, f, 1.0)
    return float(b) ** exponent

def exponential(value, *exp_factors):
    """
    Multiply `value` by 10 to the power of (product of exp_factors).
    e.g. exponential(5, 2, 3) → 5 * (10**(2*3)) == 5 * 1_000_000
    If you give no exp_factors, it just returns value.
    """
    power = exp_it(10, *exp_factors) or 1.0
    return multiply_it(value, power)

def get_proper_args(strings,*args,**kwargs):
    properArgs = [] 
    for key in strings:
        kwarg = kwargs.get(key)
        if kwarg == None and args:
            kwarg = args[0]
            args = [] if len(args) == 1 else args[1:]
        properArgs.append(kwarg)
    return properArgs
def get_lamp_difference(*args,**kwargs):
    sol_lamports =int(exponential(1,exp=9,num=1))
    proper_args = get_proper_args(["virtualSolReserves"],*args,**kwargs)
    virtualLamports = len(str(proper_args[0]))
    virtual_sol_lamports =int(exponential(1,exp=virtualLamports,num=1))
    return int(exponential(1,exp=len(str(int(virtual_sol_lamports/sol_lamports))),num=1))
def get_price(*args,**kwargs):
    proper_args = get_proper_args(["virtualSolReserves","virtualTokenReserves"],*args,**kwargs)
    return divide_it(*proper_args)/get_lamp_difference(*args,**kwargs)
def get_amount_price(*args,**kwargs):
    proper_args = get_proper_args(["solAmount","tokenAmount"],*args,**kwargs)
    return divide_it(*proper_args) 
def getSolAmountUi(*args,**kwargs):
    proper_args = get_proper_args(["solAmount"],*args,**kwargs)
    return exponential(proper_args[0],9)
def getTokenAmountUi(*args,**kwargs):
    solAmountUi = getSolAmountUi(*args,**kwargs)
    price = get_price(*args,**kwargs)
    return solAmountUi/price
def derive_token_decimals(*args,**kwargs):
    proper_args = get_proper_args(["virtualTokenReserves","tokenAmount"],*args,**kwargs)
    price = get_price(*args,**kwargs)
    if not (proper_args[1] > 0 and proper_args[0] > 0 and price > 0):
        raise ValueError("All inputs must be positive.")
    derived_token_amount = proper_args[0] / price
    ratio = derived_token_amount / proper_args[1]
    decimals = -1
    while abs(ratio - round(ratio)) > 1e-9:
        ratio *= 10
        decimals += 1
    return decimals
def derive_token_decimals_from_token_variables(variables):
  variables["price"] = get_price(**variables)
  derived_token_amount = variables["virtualTokenReserves"] / variables["price"]
  ratio = derived_token_amount / variables["tokenAmount"]
  decimals = -1
  while abs(ratio - round(ratio)) > 1e-9:
      ratio *= 10
      decimals += 1
  variables["tokenDecimals"] = decimals
  return variables
def get_token_amount_ui(*args,**kwargs):
  proper_args = get_proper_args(["tokenAmount"],*args,**kwargs)
  return exponential(proper_args[0],exp=-derive_token_decimals(*args,**kwargs),num=1)
def update_token_variables(variables):
    variables['solAmountUi'] = getSolAmountUi(**variables)
    variables['solDecimals'] = 9
    variables = derive_token_decimals_from_token_variables(variables)
    variables['tokenAmountUi'] = exponential(variables['tokenAmount'],exp=-variables["tokenDecimals"],num=1)
    return variables

