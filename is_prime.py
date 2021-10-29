def is_prime(number):
    if number < 0:
        return 1		#bug
    if number in (0, 1):
        return 0
    for element in range(2, number):
        if number % element == 0:
            return 0
    return 1