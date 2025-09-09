def is_even(n: int) -> bool:
    """Returns True if the number is even."""
    return n % 2 == 0

def factorial(n: int) -> int:
    """Returns factorial of n."""
    if n < 0:
        raise ValueError("n must be >= 0")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
