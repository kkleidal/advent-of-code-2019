from plant import Plant

with open("input.txt", "r") as f:
    input = f.read()
plant = Plant.parse(input)
print(plant.request({"FUEL": 1})[0])
