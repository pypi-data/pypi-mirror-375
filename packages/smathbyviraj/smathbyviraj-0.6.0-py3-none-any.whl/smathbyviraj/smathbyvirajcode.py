import math

def xnrt(x, n):
    root = abs(x) ** (1/n)
    signed_root = math.copysign(root, x)
    
    if x < 0 and n % 2 == 2:  
        return f"{root}i"
    elif x < 0 and n % 2 == 1: 
        return signed_root
    else:
        return root
def fbnci(n):
    if n < 0:
        raise ValueError('Fibonacci not defined for negative numbers')
    elif n == 0:
        return 0
    elif n == 1:
        return 1
    return n + fbnci(n-1)

def fctrl(n):
    if n < 0:
        raise ValueError('Factorial not defined for negative numbers')
    elif n == 0 or n == 1:
        return 1
    return n * fctrl(n - 1)

def divby(x, y):
    return f'''{x} by {y}:
    Quotient = {x//y}
    Remainder = {x%y}
    Exact Quotient = {x/y}

{y} by {x}:
    Quotient = {y//x}
    Remainder = {y%x}
    Exact Quotient = {y/x}'''

def baseconv(x, y, z, precision=12):
    """
    Converts number x from base y to base z.
    Supports fractional parts and bases 2–36.
    Uses capital letters for digits > 9.
    precision: number of digits after decimal in output
    """
    digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if not (2 <= y <= 36 and 2 <= z <= 36):
        raise ValueError("Bases must be between 2 and 36")

    # Step 1: Convert x (str) from base y to base 10 float
    x = str(x).strip().upper()
    is_negative = x.startswith('-')
    if is_negative:
        x = x[1:]

    if '.' in x:
        int_part, frac_part = x.split('.')
    else:
        int_part, frac_part = x, ''

    # Convert integer part
    base10_int = 0
    for char in int_part:
        if char not in digits[:y]:
            raise ValueError(f"Invalid character '{char}' for base {y}")
        base10_int = base10_int * y + digits.index(char)

    # Convert fractional part
    base10_frac = 0
    for i, char in enumerate(frac_part, 1):
        if char not in digits[:y]:
            raise ValueError(f"Invalid character '{char}' for base {y}")
        base10_frac += digits.index(char) / (y ** i)

    base10 = base10_int + base10_frac
    if is_negative:
        base10 = -base10

    # Step 2: Convert base10 float to base z string
    abs_val = abs(base10)
    int_part = int(abs_val)
    frac_part = abs_val - int_part

    # Convert integer part
    result_int = []
    if int_part == 0:
        result_int.append('0')
    else:
        while int_part > 0:
            result_int.append(digits[int_part % z])
            int_part //= z

    # Convert fractional part
    result_frac = []
    count = 0
    while frac_part > 0 and count < precision:
        frac_part *= z
        digit = int(frac_part)
        result_frac.append(digits[digit])
        frac_part -= digit
        count += 1

    result = ''.join(reversed(result_int))
    if result_frac:
        result += '.' + ''.join(result_frac)
    if base10 < 0:
        result = '-' + result
    return result

def euler_totient(n):
    result = n
    p = 2
    while p * p <= n:
        if n % p == 0:
            while n % p == 0:
                n //= p
            result -= result // p
        p += 1
    if n > 1:
        result -= result // n
    return result

import random

def vedicmath():
    tip_number = random.randint(1, 7)

    if tip_number == 1:
        # Multiplying Numbers Close to 100
        a = random.randint(91, 99)
        b = random.randint(91, 99)
        base = 100
        da = base - a
        db = base - b
        result = (base - (da + db)) * base + da * db
        print("Multiplying Numbers Close to 100")
        print(f"Example: {a} × {b}")
        print(f"Step 1: 100 - ({da} + {db}) = {base - (da + db)}")
        print(f"Step 2: {da} × {db} = {da * db}")
        print(f"Answer: {result}\n")

    elif tip_number == 2:
        # Squaring Numbers Ending in 5
        x = random.randint(1, 99)
        num = x * 10 + 5
        result = x * (x + 1) * 100 + 25
        print("Squaring Numbers Ending in 5")
        print(f"Example: {num}²")
        print(f"Step 1: {x} × {x+1} = {x * (x+1)}")
        print("Step 2: Add 25 at the end")
        print(f"Answer: {result}\n")

    elif tip_number == 3:
        # Subtracting from 1000
        num = random.randint(100, 999)
        digits = [int(d) for d in str(num)]
        result_digits = [9 - digits[0], 9 - digits[1], 10 - digits[2]]
        result = int("".join(str(d) for d in result_digits))
        print("Subtracting from 1000")
        print(f"Example: 1000 - {num}")
        print(f"Digits: 9-{digits[0]}, 9-{digits[1]}, 10-{digits[2]}")
        print(f"Answer: {result}\n")

    elif tip_number == 4:
        # Multiplying by 11 Quickly
        num = random.randint(10, 99)
        digits = [int(d) for d in str(num)]
        middle = digits[0] + digits[1]
        result = int(f"{digits[0]}{middle}{digits[1]}")
        print("Multiplying by 11 Quickly")
        print(f"Example: {num} × 11")
        print(f"Step: {digits[0]} ({digits[0]}+{digits[1]}) {digits[1]}")
        print(f"Answer: {result}\n")

    elif tip_number == 5:
        # Special Multiplication Trick
        a = random.randint(11, 19)
        b = 10 + (20 - a)
        if str(a)[-1] + str(b)[-1] != '10':
            b = a + (10 - int(str(a)[-1]))
        first = int(str(a)[0])
        last_a = int(str(a)[1])
        last_b = int(str(b)[1])
        result = first * (first + 1) * 100 + last_a * last_b
        print("Special Multiplication Trick")
        print(f"Example: {a} × {b}")
        print(f"Step 1: First digit × (First digit + 1) = {first} × {first+1} = {first * (first+1)}")
        print(f"Step 2: Last digits: {last_a} × {last_b} = {last_a * last_b}")
        print(f"Answer: {result}\n")

    elif tip_number == 6:
        # Multiplying Numbers Around a Base
        base = 50
        a = base + random.randint(1, 5)
        b = base - random.randint(1, 5)
        da = a - base
        db = b - base
        result = (base + db) * (base + da)
        print("Multiplying Numbers Around a Base")
        print(f"Example: {a} × {b}")
        print(f"Base = {base}, Deviations: +{da}, -{abs(db)}")
        print(f"Step: ({base + db}) × ({base + da}) = {result}")
        print(f"Answer: {result}\n")

    else:
        # Digit Sum Trick for Multiples of 9
        num = random.randint(100, 999)
        digit_sum = sum(int(d) for d in str(num))
        print("Digit Sum Trick for Multiples of 9")
        print(f"Example: Is {num} divisible by 9?")
        print(f"Step: Sum of digits = {digit_sum}")
        print("If the sum is divisible by 9, so is the number.")
        print(f"Answer: {'Yes' if digit_sum % 9 == 0 else 'No'}\n")

