import numpy as np

def construct(H, W, encoding):
    layers = len(encoding) // (H * W)
    output = np.zeros([layers, H, W], dtype=np.uint8)
    for i, c in enumerate(encoding):
        x = i % W
        y = (i // W) % H
        layer = (i // W) // H
        output[layer, y, x] = int(c)
    return output

def count_on_layers(array, number):
    return np.sum(np.sum(array == number, axis=-1), axis=-1)

def problem(array):
    fewest = np.argmin(count_on_layers(array, 0))
    return count_on_layers(array[fewest], 1) * count_on_layers(array[fewest], 2)

print(construct(2, 3, "123456789012"))
print(problem(construct(2, 3, "123456789012")))

with open("input.txt", "r") as f:
    input_value = f.read().strip()
print(problem(construct(6, 25, input_value)))
