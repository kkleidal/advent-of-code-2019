import sys

def fuel_for_module(x):
    total_fuel_required = x // 3 - 2
    fuel_weight = total_fuel_required
    while True:
        fuel_required_for_fuel = max(0, fuel_weight // 3 - 2)
        if fuel_required_for_fuel == 0:
            break
        total_fuel_required += fuel_required_for_fuel
        fuel_weight = fuel_required_for_fuel
    return total_fuel_required

total_fuel = 0
for line in sys.stdin:
    total_fuel += fuel_for_module(int(line.strip()))
print(total_fuel)
