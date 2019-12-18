import numpy as np

from fft import naieve_fft

with open("input.txt", "r") as f:
    signal = np.array([int(c) for c in f.read().strip()])

print("".join(str(c) for c in naieve_fft(signal, 100)[:8]))
