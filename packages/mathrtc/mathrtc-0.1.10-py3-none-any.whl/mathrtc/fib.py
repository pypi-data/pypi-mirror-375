def fib(num):
    def fibonacci(n):
        seq = []
        a, b = 0, 1
        for _ in range(n):
            seq.append(a)
            a, b = b, a + b
        return seq
        if num <= 0:
            print("Please enter a positive number")
        else:
            print("Fibonacci series:", fibonacci(num))
    