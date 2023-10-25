def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True


for i in range(5, 51):
    if is_prime(i):
        print(i)

# Print a end mesaage
