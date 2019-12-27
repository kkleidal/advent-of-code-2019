for a in range(20):
    for b in range(20):
        for m in range(2, 20):
            assert ((a % m) * (b % m)) % m == ((a * b) % m)
