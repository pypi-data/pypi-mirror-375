def fibonacci(n):
    """Return a list containing the Fibonacci series up to n terms."""
    seq = []
    a, b = 0, 1
    for _ in range(n):
        seq.append(a)
        a, b = b, a + b
    return seq


def fib(num):
    """Check input and print Fibonacci series."""
    if num <= 0:
        print("Please enter a positive number")
    else:
        print("Fibonacci series:", fibonacci(num))

