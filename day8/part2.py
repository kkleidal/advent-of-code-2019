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

def decode(H, W, encoding):
    array = construct(H, W, encoding)

    image = array[0, :, :]
    for layer in range(1, array.shape[0]):
        mask = image == 2
        if not np.any(mask):
            break
        image[mask] = array[layer, :, :][mask]
    return image

def render(img):
    for y in range(img.shape[0]):
        for x in range(img.shape[1]):
            if img[y, x] == 1:
                print("██", end="")
            else:
                print("  ", end="")
        print()


img = decode(2, 2, "0222112222120000")
render(img)

with open("input.txt", "r") as f:
    input_value = f.read().strip()
img = decode(6, 25, input_value)
render(img)
