def conditions(x):
    current = x
    last_digit = None
    two_the_same = False
    monotonic = True
    for digit_index in range(6):
        digit = current % 10
        current //= 10
        if last_digit is not None:
            if digit > last_digit:
                monotonic = False
                break
            if digit == last_digit:
                two_the_same = True
        last_digit = digit
    return two_the_same and monotonic

def find_numbers(low, high):
    for x in range(low, high):
        if conditions(x):
            yield x

for x in [111111, 223450, 123789]:
    print(conditions(x))

print(sum(1 for _ in find_numbers(134792, 675810)))




