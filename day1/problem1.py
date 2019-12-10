import sys

def fuel_for_module(x):
    return x // 3 - 2

total_fuel = 0
for line in sys.stdin:
    total_fuel += fuel_for_module(int(line.strip()))
print(total_fuel)
