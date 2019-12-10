def conditions(x):
    current = x
    last_digit = None
    two_the_same = False
    monotonic = True
    group = 0
    for digit_index in range(6):
        digit = current % 10
        current //= 10
        if last_digit is not None:
            if digit > last_digit:
                monotonic = False
                break
            if digit == last_digit:
                group += 1
            else:
                if group == 2:
                    two_the_same = True
                group = 1
        else:
            group = 1
        last_digit = digit
    if group == 2:
        two_the_same = True
    return two_the_same and monotonic

def find_numbers(low, high):
    for x in range(low, high):
        if conditions(x):
            yield x

for x in [112233, 123444, 111122]:
    print(conditions(x))

print(sum(1 for _ in find_numbers(134792, 675810)))
