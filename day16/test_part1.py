import numpy as np

from fft import naieve_fft, smart_fft

def test_example1():
    signal = [1, 2, 3, 4, 5, 6, 7, 8]
    assert np.allclose(naieve_fft(signal, 1), np.array([4, 8, 2, 2, 6, 1, 5, 8]))
    assert np.allclose(naieve_fft(signal, 2), np.array([3, 4, 0, 4, 0, 4, 3, 8]))
    assert np.allclose(naieve_fft(signal, 3), np.array([0, 3, 4, 1, 5, 5, 1, 8]))
    assert np.allclose(naieve_fft(signal, 4), np.array([0, 1, 0, 2, 9, 4, 9, 8]))

def a(numbers):
    return np.array([int(c) for c in numbers])

def test_example2():
    signal = a("80871224585914546619083218645595")
    assert np.allclose(naieve_fft(signal, 100)[:8], a("24176176"))

def test_example3():
    signal = a("19617804207202209144916044189917")
    assert np.allclose(naieve_fft(signal, 100)[:8], a("73745418"))

def test_example4():
    signal = a("69317163492948606335995924319873")
    assert np.allclose(naieve_fft(signal, 100)[:8], a("52432133"))

def test_example1_smart():
    signal = [1, 2, 3, 4, 5, 6, 7, 8]
    assert np.allclose(smart_fft(signal, 1), np.array([4, 8, 2, 2, 6, 1, 5, 8]))
    assert np.allclose(smart_fft(signal, 2), np.array([3, 4, 0, 4, 0, 4, 3, 8]))
    assert np.allclose(smart_fft(signal, 3), np.array([0, 3, 4, 1, 5, 5, 1, 8]))
    assert np.allclose(smart_fft(signal, 4), np.array([0, 1, 0, 2, 9, 4, 9, 8]))

def test_example2_smart():
    signal = a("80871224585914546619083218645595")
    assert np.allclose(smart_fft(signal, 100)[:8], a("24176176"))

def test_example3_smart():
    signal = a("19617804207202209144916044189917")
    assert np.allclose(smart_fft(signal, 100)[:8], a("73745418"))

def test_example4_smart():
    signal = a("69317163492948606335995924319873")
    assert np.allclose(smart_fft(signal, 100)[:8], a("52432133"))
